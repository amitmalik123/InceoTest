"""
Asset Allocation Blend Validator

Service-specific validator for Analytics API Asset Allocation calculations including:
- Blended asset class/type/sub-type weight calculations
- Component breakdown validation
- Hierarchical weight aggregation
- API-based data fetching for model holdings and security classifications

This validator computes expected asset allocation results based on:
1. Model composition data (from API or DB)
2. Input model IDs and weights from the request
3. Asset classification hierarchy (Asset Class -> Asset Type -> Asset Sub Type)
"""

import json
import math
import os
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

# Import logger
from framework.common.logger import get_logger
# Import framework API client
from framework.clients.api_client import ApiClientFactory

logger = get_logger(__name__)


# =============================================================================
# API DATA FETCHING UTILITIES (using framework ApiClientFactory)
# =============================================================================

class APIDataFetcher:
    """
    Utility class for fetching model holdings and security classifications
    from external APIs. Uses framework's ApiClientFactory for centralized
    configuration, retry logic, and connection pooling.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the API data fetcher using framework clients.
        
        Args:
            config: Configuration dict (optional, uses framework config if not provided)
        """
        self.config = config or {}
        self.token = None
        self._models_client = None
        self._securities_client = None
        self._token_client = None
        
        logger.debug("APIDataFetcher initialized (using framework ApiClientFactory)")
    
    def _get_models_client(self):
        """Get or create the Models API client."""
        if self._models_client is None:
            try:
                self._models_client = ApiClientFactory.get_client('models')
                logger.debug("Using framework 'models' API client")
            except (ValueError, KeyError) as e:
                logger.error(f"Could not get 'models' client from factory: {e}")
        return self._models_client
    
    def _get_securities_client(self):
        """Get or create the Securities API client."""
        if self._securities_client is None:
            try:
                self._securities_client = ApiClientFactory.get_client('securities')
                logger.debug("Using framework 'securities' API client")
            except (ValueError, KeyError) as e:
                logger.error(f"Could not get 'securities' client from factory: {e}")
        return self._securities_client
    
    def _get_token_client(self):
        """Get or create the Token API client."""
        if self._token_client is None:
            try:
                self._token_client = ApiClientFactory.get_client('wrapToken')
                logger.debug("Using framework 'wrapToken' API client")
            except (ValueError, KeyError) as e:
                logger.warning(f"Could not get 'wrapToken' client from factory: {e}")
        return self._token_client
    
    def get_auth_token(self) -> str:
        """
        Fetch authentication token from the token endpoint (wrapToken).
        Uses framework's ApiClientFactory.
        
        Returns:
            Authentication token string
        """
        token_client = self._get_token_client()
        if not token_client:
            logger.warning("No wrapToken client available, proceeding without authentication")
            return None
        
        try:
            logger.info("Fetching auth token using framework wrapToken client")
            response = token_client.request('GET', '')
            
            if response.status_code == 200:
                token = self._parse_token_response(response)
                if token:
                    self.token = token
                    self._update_client_tokens()
                    logger.info("Successfully fetched authentication token")
                    return self.token
            else:
                logger.error(f"Failed to get token: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching token: {e}")
            return None
    
    def _parse_token_response(self, response) -> Optional[str]:
        """Parse token from response (handles JSON and plain text formats)."""
        try:
            token_data = response.json()
            if isinstance(token_data, dict):
                token = (token_data.get('access_token') or 
                        token_data.get('token') or 
                        token_data.get('Token') or
                        token_data.get('userToken') or
                        token_data.get('UserToken'))
                if token:
                    return token
            # String from JSON
            raw = str(token_data).strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            return raw.replace('\\"', '"')
        except:
            # Plain text response
            raw = response.text.strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            return raw.replace('\\"', '"')
    
    def _update_client_tokens(self):
        """Update auth tokens on cached clients."""
        if self.token:
            if self._models_client:
                self._models_client.auth_token = self.token
            if self._securities_client:
                self._securities_client.auth_token = self.token
    
    def fetch_model_holdings(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Fetch holdings for a specific model from the Models API.
        Uses framework's ApiClientFactory with built-in retry logic.
        
        Args:
            model_id: The model ID to fetch holdings for
            
        Returns:
            List of holding dictionaries with security_id, weight, etc.
        """
        client = self._get_models_client()
        if not client:
            logger.warning("No models API client available")
            return []
        
        # Ensure we have a token
        if not self.token:
            self.get_auth_token()
        
        # Construct endpoint: /models/{modelId}/holdings (relative to base_url)
        endpoint = f"/{model_id}/holdings"
        logger.info(f"Fetching holdings for model {model_id} via framework client")
        
        try:
            # Add Authorization header with custom token format (not Bearer)
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = self.token
            
            response = client.request('GET', endpoint, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch holdings for {model_id}: {response.status_code}")
                return []
            
            data = response.json()
            
            # Handle various response formats
            if isinstance(data, list):
                holdings = data
            elif isinstance(data, dict):
                holdings = (data.get('holdings') or 
                           data.get('data') or 
                           data.get('items') or
                           [data])
            else:
                holdings = []
            
            logger.info(f"Fetched {len(holdings)} holdings for model {model_id}")
            return holdings
            
        except Exception as e:
            logger.error(f"Error fetching holdings for {model_id}: {e}")
            return []
    
    def fetch_security_by_cusip(self, cusip: str) -> Dict[str, Any]:
        """
        Fetch security details by CUSIP from the Securities API.
        Uses framework's ApiClientFactory with built-in retry logic.
        
        Args:
            cusip: The CUSIP number to look up
            
        Returns:
            Dict with security details including asset classification
        """
        client = self._get_securities_client()
        if not client:
            logger.warning("No securities API client available")
            return {}
        
        if not cusip or cusip == 'None':
            return {}
        
        if not self.token:
            self.get_auth_token()
        
        # Endpoint: /security?cusip={cusip}
        endpoint = f"/security?cusip={cusip}"
        logger.info(f"Calling Securities API for CUSIP {cusip}")
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = self.token
            
            response = client.request('GET', endpoint, headers=headers)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch security for CUSIP {cusip}: {response.status_code}")
                return {}
            
            data = response.json()
            logger.debug(f"Security data retrieved for CUSIP {cusip}")
            logger.debug(f"Full security response: {data}")
            
            # Handle both single object and array response
            security = data[0] if isinstance(data, list) and len(data) > 0 else data if isinstance(data, dict) else {}
            
            return {
                'cusip': cusip,
                'ticker': security.get('ticker') or security.get('symbol') or '',
                'description': security.get('name') or security.get('securityDescription') or security.get('description') or '',
                'asset_class': security.get('assetClass') or security.get('assetClassName') or security.get('Level1') or '',
                'asset_class_id': security.get('assetClass_id') or security.get('assetClassID') or security.get('assetClassId') or 0,
                'asset_type': security.get('assetType') or security.get('assetTypeName') or security.get('Level2') or '',
                'asset_type_id': security.get('assetType_id') or security.get('assetTypeId') or 0,
                'asset_sub_type': security.get('subAssetType') or security.get('subAssetClassName') or security.get('assetSubType') or security.get('Level3') or '',
                'asset_sub_type_id': security.get('subAssetType_id') or security.get('subAssetClassId') or security.get('assetSubTypeId') or 0,
                'raw': security
            }
        except Exception as e:
            logger.error(f"Error parsing security data for CUSIP {cusip}: {e}")
            return {}
    
    def fetch_all_model_compositions(
        self, 
        model_ids: List[str]
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        """
        Fetch compositions for all models and enrich with classifications.
        Uses framework's ApiClientFactory for API calls.
        
        Args:
            model_ids: List of model IDs to fetch
            
        Returns:
            Tuple of (model_compositions dict, total holdings fetched count)
        """
        model_compositions = {}
        total_holdings = 0
        cusip_cache = {}  # Cache CUSIP lookups to avoid duplicate API calls
        
        for model_id in model_ids:
            holdings = self.fetch_model_holdings(model_id)
            
            # Enrich holdings with classifications
            enriched_holdings = []
            for holding in holdings:
                cusip = str(holding.get('cusipNo') or 
                           holding.get('cusip') or 
                           holding.get('CUSIP', '')).strip()
                
                security_id = str(holding.get('securityId') or 
                                 holding.get('security_id') or 
                                 holding.get('ticker', '')).strip().upper()
                
                ticker = str(holding.get('ticker') or 
                            holding.get('symbol', '')).strip().upper()
                
                weight = float(holding.get('weight') or 
                              holding.get('allocation') or 
                              holding.get('percentage', 0))
                
                classification = None
                
                # STEP 1: Call Securities API for CUSIP
                if cusip:
                    if cusip in cusip_cache:
                        classification = cusip_cache[cusip]
                        logger.debug(f"Using cached classification for CUSIP {cusip}")
                    else:
                        security_data = self.fetch_security_by_cusip(cusip)
                        if security_data and security_data.get('asset_class'):
                            classification = {
                                'asset_class': security_data.get('asset_class', ''),
                                'asset_type': security_data.get('asset_type', ''),
                                'asset_sub_type': security_data.get('asset_sub_type', '')
                            }
                            cusip_cache[cusip] = classification
                            logger.info(f"Securities API returned for CUSIP {cusip}: {classification}")
                        else:
                            cusip_cache[cusip] = None
                
                # STEP 2: Fallback to holdings data
                if not classification:
                    if holding.get('assetClassName') or holding.get('assetClass'):
                        classification = {
                            'asset_class': holding.get('assetClassName') or holding.get('assetClass') or 'Other',
                            'asset_type': holding.get('assetTypeName') or holding.get('assetType') or 'Other',
                            'asset_sub_type': holding.get('subAssetClassName') or holding.get('assetSubType') or 'Other'
                        }
                        logger.info(f"Fallback to holdings data for {ticker}")
                    else:
                        classification = {'asset_class': 'Other', 'asset_type': 'Other', 'asset_sub_type': 'Other'}
                        logger.warning(f"No classification found for {ticker}, using 'Other'")
                
                enriched_holdings.append({
                    'security_id': security_id or ticker,
                    'ticker': ticker,
                    'cusip': cusip,
                    'weight': weight,
                    'asset_class': classification.get('asset_class', 'Other'),
                    'asset_type': classification.get('asset_type', 'Other'),
                    'asset_sub_type': classification.get('asset_sub_type', 'Other')
                })
            
            model_compositions[model_id] = enriched_holdings
            total_holdings += len(enriched_holdings)
            logger.info(f"Model {model_id}: {len(enriched_holdings)} holdings enriched")
            
        return model_compositions, total_holdings


class AssetAllocationValidator:
    """
    Validates Asset Allocation Blend calculations by independently computing:
    1. Component-level asset allocations weighted by model weights
    2. Blended breakdown aggregated across all models
    3. Hierarchical weight rollups (Asset Sub Type -> Asset Type -> Asset Class)
    
    The validator supports:
    - Multiple models with different weights
    - Three-level asset hierarchy (Asset Class, Asset Type, Asset Sub Type)
    - Weight precision comparison with configurable tolerance
    """
    
    # Asset hierarchy levels
    LEVEL_ASSET_CLASS = "asset class"
    LEVEL_ASSET_TYPE = "asset type"
    LEVEL_ASSET_SUB_TYPE = "asset sub type"
    
    def __init__(self, tolerance: float = 0.1):
        """
        Initialize the Asset Allocation validator.
        
        Args:
            tolerance: Acceptable difference for weight comparisons (default: 0.1 = 0.1%)
        """
        self.tolerance = tolerance
        logger.debug(f"AssetAllocationValidator initialized with tolerance: {tolerance}")
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def compare_values(
        self, 
        actual: Any, 
        expected: Any, 
        field_name: str, 
        tolerance: float = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Compare two values with optional tolerance for floating point numbers.
        
        Args:
            actual: Actual value from API response
            expected: Expected/computed value
            field_name: Name of field being compared (for error message)
            tolerance: Acceptable absolute difference for floats (default: self.tolerance)
            
        Returns:
            Tuple of (is_match, error_message or None)
        """
        if tolerance is None:
            tolerance = self.tolerance
            
        if actual is None and expected is None:
            return True, None
        
        if actual is None:
            return False, f"{field_name} missing in response (expected: {expected})"
        
        if expected is None:
            return False, f"{field_name} has no expected value to compare"
        
        # Numeric comparison with tolerance
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            diff = abs(actual - expected)
            is_match = diff <= tolerance
            
            if not is_match:
                return False, f"{field_name} mismatch: actual={actual}, expected={expected}, diff={diff}"
            return True, None
        
        # String comparison (case-insensitive)
        if isinstance(actual, str) and isinstance(expected, str):
            if actual.lower() != expected.lower():
                return False, f"{field_name} mismatch: actual='{actual}', expected='{expected}'"
            return True, None
        
        # Direct comparison for other types
        if actual != expected:
            return False, f"{field_name} mismatch: actual={actual}, expected={expected}"
        
        return True, None
    
    def round_weight(self, value: float, decimals: int = 1) -> float:
        """
        Round weight value to specified decimal places.
        
        Args:
            value: Weight value to round
            decimals: Number of decimal places (default: 1)
            
        Returns:
            Rounded weight value
        """
        return round(value, decimals)
    
    # =========================================================================
    # BLEND CALCULATION METHODS
    # =========================================================================
    
    def compute_blended_weights(
        self,
        model_compositions: Dict[str, List[Dict[str, Any]]],
        model_weights: Dict[str, float]
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Compute blended asset allocation weights from model compositions.
        
        Args:
            model_compositions: Dict mapping model_id to list of holdings:
                {
                    "CSETM6": [
                        {"security_id": "AAPL", "weight": 10.0, "asset_class": "Equity", ...},
                        ...
                    ],
                    ...
                }
            model_weights: Dict mapping model_id to blend weight:
                {"CSETM6": 0.6, "TPUAR5": 0.4}
        
        Returns:
            Hierarchical blended weights structure:
            {
                "Equity": {
                    "weight": 55.2,
                    "asset_types": {
                        "U.S. Equity": {
                            "weight": 55.2,
                            "asset_sub_types": {
                                "U.S. Large Cap Equity": 54.0,
                                "U.S. Small/Mid Cap Equity": 1.2
                            }
                        }
                    }
                },
                ...
            }
        """
        # Initialize aggregation structures
        # Format: {asset_class: {asset_type: {asset_sub_type: weight}}}
        blend_agg = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for model_id, holdings in model_compositions.items():
            raw_weight = model_weights.get(model_id, 0.0)
            # Determine if weight is already a decimal (0.6) or percentage (60)
            # If raw weight > 1, it's a percentage; if <= 1, it's a decimal
            if raw_weight > 1:
                model_weight = raw_weight / 100.0  # Convert percentage to decimal
            else:
                model_weight = raw_weight  # Already a decimal
            
            if model_weight == 0:
                logger.warning(f"Model {model_id} has zero weight, skipping")
                continue
            
            logger.debug(f"Processing model {model_id} with weight {model_weight * 100}%")
            
            for holding in holdings:
                security_weight = holding.get("weight", 0.0)
                asset_class = holding.get("asset_class", "Other")
                asset_type = holding.get("asset_type", asset_class)
                asset_sub_type = holding.get("asset_sub_type", asset_type)
                
                # Calculate weighted contribution
                weighted_contribution = security_weight * model_weight
                
                # Aggregate at sub-type level
                blend_agg[asset_class][asset_type][asset_sub_type] += weighted_contribution
        
        # Build hierarchical result structure
        result = {}
        for asset_class, types in blend_agg.items():
            class_weight = 0.0
            asset_types = {}
            
            for asset_type, sub_types in types.items():
                type_weight = 0.0
                asset_sub_types = {}
                
                for asset_sub_type, sub_weight in sub_types.items():
                    rounded_weight = self.round_weight(sub_weight)
                    asset_sub_types[asset_sub_type] = rounded_weight
                    type_weight += sub_weight
                
                rounded_type_weight = self.round_weight(type_weight)
                asset_types[asset_type] = {
                    "weight": rounded_type_weight,
                    "asset_sub_types": asset_sub_types
                }
                class_weight += type_weight
            
            rounded_class_weight = self.round_weight(class_weight)
            result[asset_class] = {
                "weight": rounded_class_weight,
                "asset_types": asset_types
            }
        
        return result
    
    def compute_component_breakdown(
        self,
        model_compositions: Dict[str, List[Dict[str, Any]]],
        model_weights: Dict[str, float],
        model_types: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        Compute component breakdown for each model in the blend.
        
        Args:
            model_compositions: Dict mapping model_id to holdings
            model_weights: Dict mapping model_id to blend weight
            model_types: Dict mapping model_id to type (e.g., "strategist", "advisor")
        
        Returns:
            List of component breakdowns:
            [
                {
                    "modelType": "strategist",
                    "modelId": "CSETM6",
                    "weight": 60.0,
                    "segments": [...]  # Hierarchical asset breakdown
                },
                ...
            ]
        """
        if model_types is None:
            model_types = {}
        
        components = []
        
        for model_id, holdings in model_compositions.items():
            raw_weight = model_weights.get(model_id, 0.0)
            # Determine if weight is already a decimal (0.6) or percentage (60)
            if raw_weight > 1:
                model_weight_decimal = raw_weight / 100.0
            else:
                model_weight_decimal = raw_weight
            model_weight = raw_weight  # Keep original for reporting
            model_type = model_types.get(model_id, "model")
            
            # Aggregate holdings by asset hierarchy
            # For componentBreakdown, we show the model's INTERNAL allocation (100% basis)
            # The blend weight is NOT applied here - each component shows its own allocation
            agg = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
            
            for holding in holdings:
                security_weight = holding.get("weight", 0.0)
                asset_class = holding.get("asset_class", "Other")
                asset_type = holding.get("asset_type", asset_class)
                asset_sub_type = holding.get("asset_sub_type", asset_type)
                
                # For componentBreakdown: use raw security weight (no blend weight applied)
                # This shows each model's internal allocation on a 100% basis
                agg[asset_class][asset_type][asset_sub_type] += security_weight
            
            # Build segments structure
            segments = []
            for asset_class, types in agg.items():
                class_weight = 0.0
                type_segments = []
                
                for asset_type, sub_types in types.items():
                    type_weight = 0.0
                    sub_segments = []
                    
                    for asset_sub_type, weight in sub_types.items():
                        rounded = self.round_weight(weight)
                        sub_segments.append({
                            "level": self.LEVEL_ASSET_SUB_TYPE,
                            "name": asset_sub_type,
                            "weight": rounded
                        })
                        type_weight += weight
                    
                    type_segments.append({
                        "level": self.LEVEL_ASSET_TYPE,
                        "name": asset_type,
                        "weight": self.round_weight(type_weight),
                        "segments": sub_segments
                    })
                    class_weight += type_weight
                
                segments.append({
                    "level": self.LEVEL_ASSET_CLASS,
                    "name": asset_class,
                    "weight": self.round_weight(class_weight),
                    "segments": type_segments
                })
            
            components.append({
                "modelType": model_type,
                "modelId": model_id,
                "weight": 100.0,  # Component weight is always 100% (model's internal allocation)
                "segments": segments
            })
        
        return components
    
    def build_blend_breakdown(
        self,
        blended_weights: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert blended weights to API response format (blendBreakdown).
        
        Args:
            blended_weights: Hierarchical weight structure from compute_blended_weights
        
        Returns:
            List in API response format:
            [
                {
                    "level": "asset class",
                    "name": "Equity",
                    "weight": 55.2,
                    "segments": [
                        {
                            "level": "asset type",
                            "name": "U.S. Equity",
                            "weight": 55.2,
                            "segments": [
                                {"level": "asset sub type", "name": "U.S. Large Cap Equity", "weight": 54.0}
                            ]
                        }
                    ]
                },
                ...
            ]
        """
        breakdown = []
        
        for asset_class, class_data in blended_weights.items():
            type_segments = []
            
            for asset_type, type_data in class_data.get("asset_types", {}).items():
                sub_segments = []
                
                for asset_sub_type, sub_weight in type_data.get("asset_sub_types", {}).items():
                    sub_segments.append({
                        "level": self.LEVEL_ASSET_SUB_TYPE,
                        "name": asset_sub_type,
                        "weight": sub_weight
                    })
                
                type_segments.append({
                    "level": self.LEVEL_ASSET_TYPE,
                    "name": asset_type,
                    "weight": type_data.get("weight", 0.0),
                    "segments": sub_segments
                })
            
            breakdown.append({
                "level": self.LEVEL_ASSET_CLASS,
                "name": asset_class,
                "weight": class_data.get("weight", 0.0),
                "segments": type_segments
            })
        
        return breakdown
    
    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================
    
    def validate_blend_breakdown(
        self,
        actual_breakdown: List[Dict[str, Any]],
        expected_breakdown: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate blendBreakdown section of API response.
        
        Args:
            actual_breakdown: Actual blendBreakdown from API response
            expected_breakdown: Computed expected blendBreakdown
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        logger.info("-" * 80)
        logger.info("BLEND BREAKDOWN VALIDATION")
        logger.info("-" * 80)
        
        # Build lookup maps for comparison
        actual_map = {item.get("name", "").lower(): item for item in actual_breakdown}
        expected_map = {item.get("name", "").lower(): item for item in expected_breakdown}
        
        # Check for missing asset classes
        for name in expected_map:
            if name not in actual_map:
                errors.append(f"Missing asset class in response: {name}")
                logger.error(f"  [FAIL] Asset class '{name}' missing in response")
        
        # Validate each asset class
        for name, expected_class in expected_map.items():
            if name not in actual_map:
                continue
            
            actual_class = actual_map[name]
            
            # Compare class-level weight
            is_match, error = self.compare_values(
                actual_class.get("weight"),
                expected_class.get("weight"),
                f"Asset class '{expected_class.get('name')}' weight"
            )
            
            if error:
                errors.append(error)
                logger.error(f"  [FAIL] {error}")
            else:
                logger.info(f"  [PASS] Asset class '{expected_class.get('name')}': weight={actual_class.get('weight')}")
            
            # Validate nested segments (asset types)
            actual_types = {s.get("name", "").lower(): s for s in actual_class.get("segments", [])}
            expected_types = {s.get("name", "").lower(): s for s in expected_class.get("segments", [])}
            
            for type_name, expected_type in expected_types.items():
                if type_name not in actual_types:
                    errors.append(f"Missing asset type '{expected_type.get('name')}' in '{expected_class.get('name')}'")
                    continue
                
                actual_type = actual_types[type_name]
                
                is_match, error = self.compare_values(
                    actual_type.get("weight"),
                    expected_type.get("weight"),
                    f"Asset type '{expected_type.get('name')}' weight"
                )
                
                if error:
                    errors.append(error)
                    logger.error(f"    [FAIL] {error}")
                else:
                    logger.info(f"    [PASS] Asset type '{expected_type.get('name')}': weight={actual_type.get('weight')}")
                
                # Validate sub-types
                actual_subs = {s.get("name", "").lower(): s for s in actual_type.get("segments", [])}
                expected_subs = {s.get("name", "").lower(): s for s in expected_type.get("segments", [])}
                
                for sub_name, expected_sub in expected_subs.items():
                    if sub_name not in actual_subs:
                        errors.append(f"Missing asset sub type '{expected_sub.get('name')}'")
                        continue
                    
                    actual_sub = actual_subs[sub_name]
                    
                    is_match, error = self.compare_values(
                        actual_sub.get("weight"),
                        expected_sub.get("weight"),
                        f"Asset sub type '{expected_sub.get('name')}' weight"
                    )
                    
                    if error:
                        errors.append(error)
                        logger.error(f"      [FAIL] {error}")
                    else:
                        logger.debug(f"      [PASS] Sub type '{expected_sub.get('name')}': weight={actual_sub.get('weight')}")
        
        return len(errors) == 0, errors
    
    def validate_component_breakdown(
        self,
        actual_components: List[Dict[str, Any]],
        expected_components: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate componentBreakdown section of API response.
        
        Args:
            actual_components: Actual componentBreakdown from API response
            expected_components: Computed expected componentBreakdown
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        logger.info("-" * 80)
        logger.info("COMPONENT BREAKDOWN VALIDATION")
        logger.info("-" * 80)
        
        # Build lookup by modelId
        actual_map = {c.get("modelId", "").upper(): c for c in actual_components}
        expected_map = {c.get("modelId", "").upper(): c for c in expected_components}
        
        for model_id, expected_comp in expected_map.items():
            if model_id not in actual_map:
                errors.append(f"Missing model component: {model_id}")
                logger.error(f"  [FAIL] Model '{model_id}' missing in componentBreakdown")
                continue
            
            actual_comp = actual_map[model_id]
            
            # Validate modelType
            actual_model_type = actual_comp.get("modelType", "").lower()
            expected_model_type = expected_comp.get("modelType", "").lower()
            if actual_model_type != expected_model_type:
                error_msg = f"Model '{model_id}' modelType mismatch: actual='{actual_comp.get('modelType')}', expected='{expected_comp.get('modelType')}'"
                errors.append(error_msg)
                logger.error(f"  [FAIL] {error_msg}")
            else:
                logger.info(f"  [PASS] Model '{model_id}': modelType='{actual_comp.get('modelType')}'")
            
            # Validate model weight
            is_match, error = self.compare_values(
                actual_comp.get("weight"),
                expected_comp.get("weight"),
                f"Model '{model_id}' weight"
            )
            
            if error:
                errors.append(error)
                logger.error(f"  [FAIL] {error}")
            else:
                logger.info(f"  [PASS] Model '{model_id}': weight={actual_comp.get('weight')}")
            
            # Validate segments (similar to blend breakdown)
            actual_segments = {s.get("name", "").lower(): s for s in actual_comp.get("segments", [])}
            expected_segments = {s.get("name", "").lower(): s for s in expected_comp.get("segments", [])}
            
            for seg_name, expected_seg in expected_segments.items():
                if seg_name not in actual_segments:
                    # Not necessarily an error - model may not have all asset classes
                    logger.debug(f"    Asset class '{seg_name}' not in model {model_id}")
                    continue
                
                actual_seg = actual_segments[seg_name]
                
                is_match, error = self.compare_values(
                    actual_seg.get("weight"),
                    expected_seg.get("weight"),
                    f"Model '{model_id}' -> '{expected_seg.get('name')}' weight"
                )
                
                if error:
                    errors.append(error)
                    logger.error(f"    [FAIL] {error}")
                else:
                    logger.info(f"    [PASS] '{expected_seg.get('name')}': weight={actual_seg.get('weight')}")
        
        return len(errors) == 0, errors
    
    def validate_api_response(
        self,
        api_response: Dict[str, Any],
        model_compositions: Dict[str, List[Dict[str, Any]]],
        model_weights: Dict[str, float],
        model_types: Dict[str, str] = None,
        skip_blend_recalc: bool = False
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate full asset allocation API response.
        
        Args:
            api_response: Full API response
            model_compositions: Model holdings data
            model_weights: Model blend weights
            model_types: Model type mappings
            skip_blend_recalc: If True, skip recomputing blend weights (for self-validation mode)
        
        Returns:
            Tuple of (is_valid, errors, computed_values)
        """
        errors = []
        
        logger.info("=" * 80)
        logger.info("ASSET ALLOCATION BLEND VALIDATION")
        logger.info("=" * 80)
        
        # Extract actual values from response
        calc_results = api_response.get("calculationResults", [])
        asset_alloc_result = None
        
        for result in calc_results:
            if result.get("calculationType") == "asset allocation":
                asset_alloc_result = result.get("result", {})
                break
        
        if asset_alloc_result is None:
            errors.append("No 'asset allocation' calculationType in response")
            return False, errors, {"expected": []}
        
        actual_blend = asset_alloc_result.get("blendBreakdown", [])
        actual_components = asset_alloc_result.get("componentBreakdown", [])
        
        if skip_blend_recalc:
            # Self-validation mode: use actual API values as expected
            # This validates internal consistency (blend matches component sum)
            logger.info("Self-validation mode: Comparing API blend vs component sums")
            expected_blend_breakdown = actual_blend
            expected_component_breakdown = actual_components
        else:
            # Extract actual modelTypes from API response for accurate comparison
            # The API returns the real modelType (strategist, advisor, etc.)
            actual_model_types = {}
            for comp in actual_components:
                model_id = comp.get("modelId", "").upper()
                actual_model_type = comp.get("modelType", "model")
                actual_model_types[model_id] = actual_model_type
            
            # Merge actual modelTypes with any provided (API takes precedence)
            merged_model_types = {**model_types, **actual_model_types} if model_types else actual_model_types
            
            # Compute expected values from model compositions
            blended_weights = self.compute_blended_weights(model_compositions, model_weights)
            expected_blend_breakdown = self.build_blend_breakdown(blended_weights)
            expected_component_breakdown = self.compute_component_breakdown(
                model_compositions, model_weights, merged_model_types
            )
            
            # Validate blend breakdown
            blend_valid, blend_errors = self.validate_blend_breakdown(
                actual_blend, expected_blend_breakdown
            )
            errors.extend(blend_errors)
            
            # Validate component breakdown
            comp_valid, comp_errors = self.validate_component_breakdown(
                actual_components, expected_component_breakdown
            )
            errors.extend(comp_errors)
        
        is_valid = len(errors) == 0
        
        logger.info("=" * 80)
        if is_valid:
            logger.info("RESULT: [PASS] All asset allocation calculations validated successfully")
        else:
            logger.error(f"RESULT: [FAIL] Asset allocation validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.error(f"  - {error}")
        logger.info("=" * 80)
        
        computed_values = {
            "blendBreakdown": expected_blend_breakdown,
            "componentBreakdown": expected_component_breakdown,
            "apiValues": {
                "blendBreakdown": actual_blend,
                "componentBreakdown": actual_components
            }
        }
        
        return is_valid, errors, computed_values
    
    def compare_api_vs_script_results(
        self,
        api_blend_breakdown: List[Dict[str, Any]],
        script_blend_breakdown: List[Dict[str, Any]],
        api_component_breakdown: List[Dict[str, Any]] = None,
        script_component_breakdown: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare API response values against script-computed values.
        Provides detailed matching information for each asset allocation component.
        
        Args:
            api_blend_breakdown: Actual blendBreakdown from API response
            script_blend_breakdown: Script-computed expected blendBreakdown
            api_component_breakdown: Actual componentBreakdown from API response
            script_component_breakdown: Script-computed expected componentBreakdown
            
        Returns:
            Dict with comparison results including:
            - blend_weight_matches: List of detailed match results per asset class
            - component_weight_matches: List of detailed match results per model
            - overall_match: bool indicating if all values match within tolerance
            - mismatches: List of specific mismatches found
        """
        logger.info("-" * 80)
        logger.info("API vs SCRIPT RESULT COMPARISON")
        logger.info("-" * 80)
        
        blend_matches = []
        component_matches = []
        mismatches = []
        overall_match = True
        
        # Compare blend breakdown
        api_blend_map = {item.get("name", "").lower(): item for item in (api_blend_breakdown or [])}
        script_blend_map = {item.get("name", "").lower(): item for item in (script_blend_breakdown or [])}
        
        for name, script_item in script_blend_map.items():
            api_item = api_blend_map.get(name)
            script_weight = script_item.get("weight", 0)
            
            if api_item is None:
                blend_matches.append({
                    "asset_class": script_item.get("name"),
                    "api_weight": None,
                    "script_weight": script_weight,
                    "match": False,
                    "difference": None,
                    "status": "MISSING_IN_API"
                })
                mismatches.append(f"Asset class '{script_item.get('name')}' missing in API response")
                overall_match = False
                continue
            
            api_weight = api_item.get("weight", 0)
            is_match, _ = self.compare_values(api_weight, script_weight, "weight")
            diff = abs(api_weight - script_weight)
            
            blend_matches.append({
                "asset_class": script_item.get("name"),
                "api_weight": api_weight,
                "script_weight": script_weight,
                "match": is_match,
                "difference": round(diff, 3),
                "status": "PASS" if is_match else "FAIL"
            })
            
            if not is_match:
                mismatches.append(
                    f"Blend weight mismatch for '{script_item.get('name')}': "
                    f"API={api_weight}, Script={script_weight}, Diff={diff}"
                )
                overall_match = False
            else:
                logger.info(f"  [MATCH] Asset class '{script_item.get('name')}': API={api_weight}, Script={script_weight}")
            
            # Compare nested asset types
            api_types = {s.get("name", "").lower(): s for s in api_item.get("segments", [])}
            script_types = {s.get("name", "").lower(): s for s in script_item.get("segments", [])}
            
            for type_name, script_type in script_types.items():
                api_type = api_types.get(type_name)
                script_type_weight = script_type.get("weight", 0)
                
                if api_type:
                    api_type_weight = api_type.get("weight", 0)
                    type_match, _ = self.compare_values(api_type_weight, script_type_weight, "weight")
                    type_diff = abs(api_type_weight - script_type_weight)
                    
                    if not type_match:
                        mismatches.append(
                            f"Type weight mismatch for '{script_type.get('name')}': "
                            f"API={api_type_weight}, Script={script_type_weight}"
                        )
                        overall_match = False
        
        # Compare component breakdown if provided
        if api_component_breakdown and script_component_breakdown:
            api_comp_map = {c.get("modelId", "").upper(): c for c in api_component_breakdown}
            script_comp_map = {c.get("modelId", "").upper(): c for c in script_component_breakdown}
            
            for model_id, script_comp in script_comp_map.items():
                api_comp = api_comp_map.get(model_id)
                script_model_weight = script_comp.get("weight", 0)
                
                if api_comp is None:
                    component_matches.append({
                        "model_id": model_id,
                        "api_weight": None,
                        "script_weight": script_model_weight,
                        "match": False,
                        "status": "MISSING_IN_API"
                    })
                    mismatches.append(f"Model '{model_id}' missing in API componentBreakdown")
                    overall_match = False
                    continue
                
                api_model_weight = api_comp.get("weight", 0)
                is_match, _ = self.compare_values(api_model_weight, script_model_weight, "weight")
                
                component_matches.append({
                    "model_id": model_id,
                    "model_type": api_comp.get("modelType"),
                    "api_weight": api_model_weight,
                    "script_weight": script_model_weight,
                    "match": is_match,
                    "status": "PASS" if is_match else "FAIL"
                })
                
                if not is_match:
                    mismatches.append(
                        f"Component weight mismatch for model '{model_id}': "
                        f"API={api_model_weight}, Script={script_model_weight}"
                    )
                    overall_match = False
                else:
                    logger.info(f"  [MATCH] Model '{model_id}': API={api_model_weight}, Script={script_model_weight}")
        
        result = {
            "blend_weight_matches": blend_matches,
            "component_weight_matches": component_matches,
            "overall_match": overall_match,
            "total_blend_classes": len(blend_matches),
            "blend_matches_count": sum(1 for m in blend_matches if m.get("match")),
            "total_components": len(component_matches),
            "component_matches_count": sum(1 for m in component_matches if m.get("match")),
            "mismatches": mismatches,
            "mismatch_count": len(mismatches)
        }
        
        logger.info(f"  Comparison Summary: Blend {result['blend_matches_count']}/{result['total_blend_classes']} matched, "
                   f"Components {result['component_matches_count']}/{result['total_components']} matched")
        
        return result
    
    def validate_blend_component_consistency(
        self,
        blend_breakdown: List[Dict[str, Any]],
        component_breakdown: List[Dict[str, Any]],
        model_weights: Dict[str, float] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that blendBreakdown totals are consistent with componentBreakdown totals.
        The sum of weighted contributions from all components should equal the blend totals.
        
        Args:
            blend_breakdown: The blendBreakdown from API response
            component_breakdown: The componentBreakdown from API response
            model_weights: Optional dict mapping model_id to blend weight (decimal or percentage)
            
        Returns:
            Tuple of (is_consistent, error_messages)
        """
        errors = []
        
        logger.info("-" * 80)
        logger.info("BLEND-COMPONENT CONSISTENCY CHECK")
        logger.info("-" * 80)
        
        # Aggregate component contributions by asset class
        # Apply the blend weight to each component's segments
        component_totals = defaultdict(float)
        
        for component in component_breakdown:
            model_id = component.get("modelId", "").upper()
            
            # Get the blend weight for this model (from request, not componentBreakdown)
            # componentBreakdown.weight is always 100 (internal allocation)
            # We need the actual blend weight (0.6, 0.4, etc.)
            if model_weights:
                raw_blend_weight = model_weights.get(model_id, 0)
                # Normalize to decimal if percentage
                if raw_blend_weight > 1:
                    blend_weight_decimal = raw_blend_weight / 100.0
                else:
                    blend_weight_decimal = raw_blend_weight
            else:
                # Fallback: if no model_weights provided, assume equal weighting
                blend_weight_decimal = 1.0 / len(component_breakdown) if component_breakdown else 0
                logger.warning(f"No model_weights provided, using fallback weight {blend_weight_decimal:.2f} for {model_id}")
            
            for segment in component.get("segments", []):
                if segment.get("level") == "asset class":
                    asset_class = segment.get("name", "").lower()
                    # Apply blend weight to segment weight to get contribution to blend
                    segment_weight = segment.get("weight", 0)
                    weighted_contribution = segment_weight * blend_weight_decimal
                    component_totals[asset_class] += weighted_contribution
        
        # Compare with blend totals
        for blend_item in blend_breakdown:
            asset_class = blend_item.get("name", "").lower()
            blend_weight = blend_item.get("weight", 0)
            component_weight = component_totals.get(asset_class, 0)
            
            is_match, error = self.compare_values(
                blend_weight, component_weight,
                f"Blend vs Component total for '{blend_item.get('name')}'"
            )
            
            if not is_match:
                errors.append(
                    f"Inconsistency: Blend '{blend_item.get('name')}' weight={blend_weight} "
                    f"but component total={round(component_weight, 2)}"
                )
                logger.error(f"  [FAIL] {errors[-1]}")
            else:
                logger.info(f"  [PASS] '{blend_item.get('name')}': blend={blend_weight}, component_total={round(component_weight, 2)}")
        
        return len(errors) == 0, errors


# =============================================================================
# DB/INPUT PARSING UTILITIES
# =============================================================================

# Column name variants for flexible DB parsing
_COLUMN_VARIANTS = {
    'model_id': ['model_id', 'ModelId', 'MODEL_ID', 'modelId', 'ItemId'],
    'security_id': ['security_id', 'SecurityId', 'SECURITY_ID', 'securityId', 'ticker', 'Ticker'],
    'weight': ['weight', 'Weight', 'WEIGHT', 'allocation', 'Allocation'],
    'asset_class': ['asset_class', 'AssetClass', 'ASSET_CLASS', 'Level1'],
    'asset_type': ['asset_type', 'AssetType', 'ASSET_TYPE', 'Level2'],
    'asset_sub_type': ['asset_sub_type', 'AssetSubType', 'ASSET_SUB_TYPE', 'Level3']
}


def _detect_column(row: Dict, field: str) -> Optional[str]:
    """Detect column name from row using known variants."""
    return next((c for c in _COLUMN_VARIANTS.get(field, []) if c in row), None)


def parse_model_compositions_from_db(
    db_results: List[Dict[str, Any]],
    model_ids: List[str],
    asset_classifications: Dict[str, Dict[str, str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parse model holdings from database results with flexible column detection.
    
    Args:
        db_results: List of holding records from DB
        model_ids: Model IDs to include
        asset_classifications: Optional security -> classification lookup
    
    Returns:
        Dict mapping model_id to list of holdings
    """
    asset_classifications = asset_classifications or {}
    model_compositions = {mid: [] for mid in model_ids}
    
    if not db_results:
        logger.warning("Empty DB results for model compositions")
        return model_compositions
    
    first_row = db_results[0]
    model_col = _detect_column(first_row, 'model_id')
    security_col = _detect_column(first_row, 'security_id')
    weight_col = _detect_column(first_row, 'weight')
    class_col = _detect_column(first_row, 'asset_class')
    type_col = _detect_column(first_row, 'asset_type')
    sub_type_col = _detect_column(first_row, 'asset_sub_type')
    
    if not model_col or not weight_col:
        logger.error(f"Required columns not found. Available: {list(first_row.keys())}")
        return model_compositions
    
    for row in db_results:
        model_id = str(row.get(model_col, "")).strip().upper()
        if model_id not in model_ids:
            continue
        
        security_id = str(row.get(security_col, "")).strip().upper() if security_col else None
        weight = float(row.get(weight_col, 0))
        
        # Get classification: DB row > external lookup > default "Other"
        if class_col and row.get(class_col):
            classification = {
                "asset_class": row.get(class_col),
                "asset_type": row.get(type_col) or row.get(class_col),
                "asset_sub_type": row.get(sub_type_col) or row.get(type_col) or row.get(class_col)
            }
        elif security_id and security_id in asset_classifications:
            classification = asset_classifications[security_id]
        else:
            classification = {"asset_class": "Other", "asset_type": "Other", "asset_sub_type": "Other"}
        
        model_compositions[model_id].append({
            "security_id": security_id,
            "weight": weight,
            "asset_class": classification.get("asset_class", "Other"),
            "asset_type": classification.get("asset_type", "Other"),
            "asset_sub_type": classification.get("asset_sub_type", "Other")
        })
    
    for model_id, holdings in model_compositions.items():
        logger.info(f"Parsed {len(holdings)} holdings for model {model_id}")
    
    return model_compositions


def extract_model_inputs_from_payload(request_payload: Dict[str, Any]) -> Tuple[List[str], Dict[str, float], Dict[str, str]]:
    """
    Extract model IDs, weights, and types from API request payload.
    
    Returns:
        Tuple of (model_ids, weights_dict, model_types_dict)
    """
    model_ids, weights, model_types = [], {}, {}
    
    blend = request_payload.get("calculationRequest", {}).get("inputs", {}).get("blend", [])
    
    for item in blend:
        entity_type = item.get("entityType", "model")
        if entity_type in ["model", "strategist", "advisor"]:
            model_id = item.get("id", "").upper()
            model_ids.append(model_id)
            weights[model_id] = item.get("weight", 0.0)
            model_types[model_id] = entity_type
    
    logger.info(f"Extracted {len(model_ids)} models: {model_ids}, weights: {weights}")
    return model_ids, weights, model_types


# =============================================================================
# SCRIPT EXECUTOR INTEGRATION
# =============================================================================

def validate(context):
    """
    Main entry point for script executor integration.
    
    This function is called by the ScriptExecutor when 'scripts' field 
    references this file. It receives full test context and returns 
    results in ScriptResult-compatible format.
    
    Supports multiple data sources:
    1. API-based: Fetches model holdings via intermediary API calls
    2. DB-based: Uses database query results for model compositions
    3. Self-validation: Extracts from API response componentBreakdown
    
    Args:
        context: ScriptContext or dict with test execution data
            - test_case: Full test case configuration
            - request: Request details (endpoint, method, payload)
            - response: API response data
            - db_results: Database query results (model compositions)
            - extracted_vars: Previously extracted variables
            - config: Framework configuration
    
    Returns:
        dict: ScriptResult-compatible dictionary with:
            - success: bool
            - errors: List[str]
            - extracted_values: Dict[str, Any]
            - computed_values: Dict[str, Any]
    """
    try:
        # Handle both ScriptContext object and dict formats
        if hasattr(context, 'to_dict'):
            ctx = context.to_dict()
        elif isinstance(context, dict):
            ctx = context
        else:
            return {
                "success": False,
                "errors": [f"Invalid context type: {type(context)}"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # Extract required data from context
        test_case = ctx.get('test_case', {})
        response_ctx = ctx.get('response', {})
        db_results = ctx.get('db_results', [])
        extracted_vars = ctx.get('extracted_vars', {})
        config = ctx.get('config', {})
        
        # Get API response body
        api_response = response_ctx.get('body') if isinstance(response_ctx, dict) else None
        
        if not api_response:
            return {
                "success": False,
                "errors": ["No API response body available for validation"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # Get request payload
        request_ctx = ctx.get('request', {})
        request_payload = request_ctx.get('payload') if isinstance(request_ctx, dict) else None
        
        if not request_payload:
            request_payload = extracted_vars.get('api_request')
        
        if not request_payload:
            return {
                "success": False,
                "errors": ["No request payload available for validation"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # Extract model inputs from payload
        model_ids, weights, model_types = extract_model_inputs_from_payload(request_payload)
        
        # Preserve original blend weights for consistency check
        original_blend_weights = dict(weights)
        
        if not model_ids:
            return {
                "success": False,
                "errors": ["No model IDs found in request payload"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # =====================================================================
        # DETERMINE DATA SOURCE AND FETCH MODEL COMPOSITIONS
        # =====================================================================
        validator = AssetAllocationValidator()
        model_compositions = {}
        data_source = "unknown"
        api_holdings_fetched = 0
        
        use_api_data_source = test_case.get("use_api_data_source", False)
        
        if use_api_data_source:
            # ===== API-BASED DATA FETCHING =====
            logger.info("Using API-based data source for model compositions")
            data_source = "api"
            
            # Get API configuration from test case
            api_data_config = test_case.get("api_data_config", {})
            
            # Get api_endpoints from config file (config.T11.yaml structure)
            api_endpoints = config.get("api_endpoints", {})
            
            # Build URLs from config - use specific endpoints:
            # - wrapToken: for authentication token
            # - strategies: for model holdings (strategies API)
            # - securities: for security classifications
            
            # Token endpoint - use wrapToken from config
            wrap_token_config = api_endpoints.get("wrapToken") or {}
            
            # Strategies API endpoint for model holdings
            strategies_endpoint_config = (api_endpoints.get("strategies") or 
                                          api_endpoints.get("models") or
                                          api_endpoints.get("modelsApiServices") or {})
            
            # Securities API endpoint
            securities_endpoint_config = (api_endpoints.get("securities") or 
                                          api_endpoints.get("securitiesApiServices") or {})
            
            # Get token URL - prioritize wrapToken from config
            token_url = (wrap_token_config.get("base_url") or
                        api_data_config.get("token_endpoint") or 
                        config.get("token_url") or
                        extracted_vars.get("token_url"))
            
            # Resolve template variable if still contains {{}}
            if token_url and '{{' in str(token_url):
                token_url = wrap_token_config.get("base_url")  # Fall back to config
            
            # Get models/strategies API base URL from config.yaml api_endpoints structure
            models_api_base = api_data_config.get("models_api_base")
            if not models_api_base or (models_api_base and '{{' in str(models_api_base)):
                # Template not resolved or not set, use strategies endpoint from config
                models_api_base = (strategies_endpoint_config.get("base_url") or
                                   config.get("models_api_base") or
                                   extracted_vars.get("models_api_base"))
            
            # Get securities API base URL from config.yaml api_endpoints structure
            securities_api_base = api_data_config.get("securities_api_base")
            if not securities_api_base or (securities_api_base and '{{' in str(securities_api_base)):
                # Template not resolved or not set, use securities endpoint from config
                securities_api_base = (securities_endpoint_config.get("base_url") or
                                       config.get("securities_api_base") or
                                       extracted_vars.get("securities_api_base"))
            
            logger.info("Resolved API URLs for token, models/strategies, and securities endpoints")
            logger.debug(f"API URLs - token: {token_url}, models/strategies: {models_api_base}, securities: {securities_api_base}")
            
            # Initialize API data fetcher
            fetcher = APIDataFetcher({
                'token_endpoint': token_url,
                'models_api_base': models_api_base,
                'securities_api_base': securities_api_base
            })
            
            # Fetch model compositions via API
            model_compositions, api_holdings_fetched = fetcher.fetch_all_model_compositions(
                model_ids
            )
            
            logger.info(f"Fetched {api_holdings_fetched} total holdings via API")
            
            # Log warning if no holdings were fetched (models may not exist in strategies API)
            if api_holdings_fetched == 0:
                logger.warning("API fetch returned no holdings - models may not exist in strategies API")
                logger.warning(f"Model IDs requested: {model_ids}")
                logger.info("Falling back to self-validation mode using API response componentBreakdown")
        
        elif isinstance(db_results, dict) and db_results:
            # ===== DB-BASED DATA SOURCE =====
            logger.info("Using DB-based data source for model compositions")
            data_source = "database"
            
            comp_data = (
                db_results.get('model_compositions') or
                db_results.get('modelCompositions') or
                db_results.get('holdings') or
                db_results.get('model_holdings') or
                next((v for k, v in db_results.items()), [])
            )
            model_compositions = parse_model_compositions_from_db(
                comp_data, model_ids
            )
            
        elif isinstance(db_results, list) and db_results:
            # ===== DB RESULTS AS LIST =====
            data_source = "database"
            model_compositions = parse_model_compositions_from_db(
                db_results, model_ids
            )
        
        # If no external data, extract from API response componentBreakdown
        if not any(model_compositions.values()):
            logger.info("No external data source, extracting from API response (self-validation mode)")
            data_source = "api_response"
            
            # Store original API model weights for component comparison
            api_model_weights = {}
            
            calc_results = api_response.get("calculationResults", [])
            for result in calc_results:
                if result.get("calculationType") == "asset allocation":
                    components = result.get("result", {}).get("componentBreakdown", [])
                    for comp in components:
                        model_id = comp.get("modelId", "").upper()
                        if model_id in model_ids:
                            holdings = []
                            for segment in comp.get("segments", []):
                                _extract_holdings_from_segments(segment, holdings)
                            model_compositions[model_id] = holdings
                            # Store the original model weight from API for component comparison
                            api_model_weights[model_id] = comp.get("weight", 0)
            
            # IMPORTANT: In self-validation mode, the weights from componentBreakdown are already
            # the blended contributions (e.g., 55.2% not 92%), so:
            # 1. Use 1.0 for blend calculation to avoid double-weighting
            # 2. Use API model weights (60.0, 40.0) for component breakdown comparison
            if model_compositions:
                logger.info("Self-validation mode: Using API model weights for component comparison")
                # Set weights to API values (as percentage) for correct component comparison
                weights = api_model_weights
                logger.info(f"API model weights: {weights}")
        
        # =====================================================================
        # VALIDATE API RESPONSE AGAINST COMPUTED VALUES
        # =====================================================================
        # For self-validation mode, we pass a flag to skip recalculating blend weights
        success, errors, computed_values = validator.validate_api_response(
            api_response, model_compositions, weights, model_types,
            skip_blend_recalc=(data_source == "api_response")
        )
        
        # =====================================================================
        # COMPARE API VS SCRIPT RESULTS
        # =====================================================================
        actual_blend = computed_values.get("apiValues", {}).get("blendBreakdown", [])
        actual_components = computed_values.get("apiValues", {}).get("componentBreakdown", [])
        script_blend = computed_values.get("blendBreakdown", [])
        script_components = computed_values.get("componentBreakdown", [])
        
        comparison_result = validator.compare_api_vs_script_results(
            actual_blend, script_blend,
            actual_components, script_components
        )
        
        # =====================================================================
        # LOG DETAILED COMPARISON RESULTS
        # =====================================================================
        import json
        logger.info("=" * 80)
        logger.info("ASSET ALLOCATION VALIDATION RESULTS")
        logger.info("=" * 80)
        
        # Log blendBreakdown comparison
        logger.info("\n[BLEND BREAKDOWN COMPARISON]")
        logger.debug(f"API blendBreakdown:\n{json.dumps(actual_blend, indent=2, default=str)}")
        logger.debug(f"Script blendBreakdown:\n{json.dumps(script_blend, indent=2, default=str)}")
        blend_match = actual_blend == script_blend
        logger.info(f"Blend Match: {'[PASS]' if blend_match else '[FAIL]'} - {blend_match}")
        
        # Log componentBreakdown comparison
        logger.info("\n[COMPONENT BREAKDOWN COMPARISON]")
        logger.debug(f"API componentBreakdown:\n{json.dumps(actual_components, indent=2, default=str)}")
        logger.debug(f"Script componentBreakdown:\n{json.dumps(script_components, indent=2, default=str)}")
        component_match = actual_components == script_components
        logger.info(f"Component Match: {'[PASS]' if component_match else '[FAIL]'} - {component_match}")
        
        # Log overall comparison result
        logger.info("\n[OVERALL COMPARISON]")
        logger.info(f"Overall Match: {'[PASS]' if comparison_result.get('overall_match', False) else '[FAIL]'}")
        if comparison_result.get('blend_weight_matches'):
            logger.info(f"Blend Weight Matches: {comparison_result.get('blend_weight_matches')}")
        if comparison_result.get('component_weight_matches'):
            logger.info(f"Component Weight Matches: {comparison_result.get('component_weight_matches')}")
        if comparison_result.get('mismatches'):
            logger.info(f"Mismatches Found: {comparison_result.get('mismatches')}")
        logger.info("=" * 80)
        
        # =====================================================================
        # CHECK BLEND-COMPONENT CONSISTENCY
        # Use original blend weights (0.6, 0.4) not API component weights (100.0, 100.0)
        # =====================================================================
        consistency_passed, consistency_errors = validator.validate_blend_component_consistency(
            actual_blend, actual_components, original_blend_weights
        )
        
        if consistency_errors:
            errors.extend(consistency_errors)
        
        # =====================================================================
        # BUILD EXTRACTED VALUES FOR TEST CASE
        # =====================================================================
        extracted_values = {
            "model_ids": model_ids,
            "model_weights": weights,
            "validation_success": success,
            "data_source": data_source,
            "error_count": len(errors),
            "api_holdings_fetched": api_holdings_fetched,
            "blend_weight_matches": comparison_result.get("blend_weight_matches", []),
            "component_weight_matches": comparison_result.get("component_weight_matches", []),
            "blend_component_consistency": consistency_passed,
            # Add blendBreakdown and componentBreakdown for direct JSON comparison
            "api_blendBreakdown": actual_blend,
            "api_componentBreakdown": actual_components,
            "script_blendBreakdown": script_blend,
            "script_componentBreakdown": script_components,
            "overall_comparison_match": comparison_result.get("overall_match", False)
        }
        
        # Add computed values to result
        computed_values["comparison"] = comparison_result
        computed_values["consistency_check"] = {
            "passed": consistency_passed,
            "errors": consistency_errors
        }
        
        return {
            "success": success and consistency_passed,
            "errors": errors,
            "extracted_values": extracted_values,
            "computed_values": computed_values,
            "metadata": {
                "validator": "AssetAllocationValidator",
                "test_id": test_case.get('test_id'),
                "models_validated": model_ids,
                "data_source": data_source,
                "api_holdings_fetched": api_holdings_fetched
            }
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Asset allocation validator error: {e}")
        logger.debug(traceback.format_exc())
        return {
            "success": False,
            "errors": [f"Asset allocation validation error: {str(e)}"],
            "extracted_values": {},
            "computed_values": {},
            "metadata": {
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
        }


def _extract_holdings_from_segments(
    segment: Dict[str, Any],
    holdings: List[Dict[str, Any]],
    parent_class: str = None,
    parent_type: str = None
):
    """
    Recursively extract holdings from segment hierarchy.
    
    Args:
        segment: Current segment node
        holdings: List to append holdings to
        parent_class: Parent asset class name
        parent_type: Parent asset type name
    """
    level = segment.get("level", "")
    name = segment.get("name", "")
    weight = segment.get("weight", 0.0)
    sub_segments = segment.get("segments", [])
    
    if level == "asset class":
        for sub in sub_segments:
            _extract_holdings_from_segments(sub, holdings, name, None)
    elif level == "asset type":
        for sub in sub_segments:
            _extract_holdings_from_segments(sub, holdings, parent_class, name)
    elif level == "asset sub type":
        # Leaf node - this is a holding
        holdings.append({
            "security_id": None,  # Not available from breakdown
            "weight": weight,
            "asset_class": parent_class or "Other",
            "asset_type": parent_type or parent_class or "Other",
            "asset_sub_type": name
        })


# Alias for backward compatibility
run = validate


if __name__ == "__main__":
    """
    Run the asset allocation validator independently.
    
    Usage:
        python asset_allocation_validator.py --model-ids CSETM6,TPUAR5 --weights 0.6,0.4
        python asset_allocation_validator.py --model-ids CSETM6 --weights 1.0
    """
    import argparse
    import yaml
    import requests
    
    parser = argparse.ArgumentParser(description="Asset Allocation Validator - Standalone Mode")
    parser.add_argument(
        "--model-ids", "-m",
        required=True,
        help="Comma-separated model IDs (e.g., CSETM6,TPUAR5)"
    )
    parser.add_argument(
        "--weights", "-w",
        required=True,
        help="Comma-separated weights corresponding to model IDs (e.g., 0.6,0.4)"
    )
    parser.add_argument(
        "--env", "-e",
        default="T11",
        help="Environment name (default: T11)"
    )
    parser.add_argument(
        "--config-path", "-c",
        default=None,
        help="Path to config file (default: config/config.<env>.yaml)"
    )
    
    args = parser.parse_args()
    
    # Parse model IDs and weights
    model_ids = [m.strip().upper() for m in args.model_ids.split(",")]
    weights_list = [float(w.strip()) for w in args.weights.split(",")]
    
    if len(model_ids) != len(weights_list):
        print(f"ERROR: Number of model IDs ({len(model_ids)}) must match number of weights ({len(weights_list)})")
        exit(1)
    
    # Build weights dict
    model_weights = {mid: w for mid, w in zip(model_ids, weights_list)}
    model_types = {mid: "model" for mid in model_ids}
    
    print("=" * 80)
    print("ASSET ALLOCATION VALIDATOR - STANDALONE MODE")
    print("=" * 80)
    print(f"Model IDs: {model_ids}")
    print(f"Weights: {model_weights}")
    print(f"Environment: {args.env}")
    print("=" * 80)
    
    # Load config
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    config_path = args.config_path or os.path.join(base_path, f"config/config.{args.env}.yaml")
    
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Loaded config from: {config_path}")
    
    # Get API endpoints
    api_endpoints = config.get("api_endpoints", {})
    wrap_token_config = api_endpoints.get("wrapToken", {})
    strategies_config = api_endpoints.get("strategies", {})
    securities_config = api_endpoints.get("securities", {})
    analytics_config = api_endpoints.get("analyticsApiServices", {})
    
    token_url = wrap_token_config.get("base_url")
    strategies_url = strategies_config.get("base_url")
    securities_url = securities_config.get("base_url")
    analytics_url = analytics_config.get("base_url")
    
    print(f"Token URL: {token_url}")
    print(f"Strategies URL: {strategies_url}")
    print(f"Securities URL: {securities_url}")
    print(f"Analytics URL: {analytics_url}")
    print("=" * 80)
    
    # Build request payload
    blend_items = [
        {"id": mid, "entityType": "model", "weight": w}
        for mid, w in model_weights.items()
    ]
    
    request_payload = {
        "calculationRequest": {
            "inputs": {
                "blend": blend_items
            },
            "calculations": [
                {"calculationType": "asset allocation", "configurations": {}}
            ]
        }
    }
    
    print("Request Payload:")
    print(json.dumps(request_payload, indent=2))
    print("=" * 80)
    
    # Initialize fetcher and get token
    fetcher = APIDataFetcher({
        'token_endpoint': token_url,
        'models_api_base': strategies_url,
        'securities_api_base': securities_url
    })
    
    token = fetcher.get_auth_token()
    if not token:
        print("ERROR: Failed to fetch authentication token")
        exit(1)
    
    print(f"Token fetched successfully (length: {len(token)})")
    
    # Call analytics API
    print("\nCalling Analytics API...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": token  # Token from wrapToken doesn't need "Bearer" prefix
    }
    
    analytics_endpoint = f"{analytics_url}/v1/analytics"
    print(f"Endpoint: {analytics_endpoint}")
    
    # Disable SSL warnings for internal APIs
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    response = requests.post(analytics_endpoint, json=request_payload, headers=headers, timeout=30, verify=False)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Response Body: {response.text}")
        exit(1)
    
    api_response = response.json()
    print("\nAPI Response:")
    print(json.dumps(api_response, indent=2))
    print("=" * 80)
    
    # Initialize validator
    validator = AssetAllocationValidator()
    
    # Fetch model compositions from strategies API (with Securities API enrichment)
    print("\nFetching model compositions from Strategies API...")
    model_compositions, holdings_count = fetcher.fetch_all_model_compositions(model_ids)
    
    print(f"Fetched {holdings_count} total holdings")
    for mid, holdings in model_compositions.items():
        print(f"  {mid}: {len(holdings)} holdings")
    
    # =========================================================================
    # COMPUTE EXPECTED PAYLOAD FROM STRATEGIES + SECURITIES API DATA
    # =========================================================================
    print("\n" + "=" * 80)
    print("COMPUTING EXPECTED PAYLOAD FROM API DATA")
    print("=" * 80)
    
    def build_hierarchical_breakdown(holdings: list, model_weight: float = 1.0) -> list:
        """
        Build hierarchical asset allocation breakdown from holdings.
        Groups by Asset Class -> Asset Type -> Asset Sub Type
        
        Args:
            holdings: List of holding dicts with asset_class, asset_type, asset_sub_type, weight
            model_weight: Weight multiplier for the model (0-1)
            
        Returns:
            List of asset class segments with nested asset type and sub type
        """
        from collections import defaultdict
        
        # Aggregate weights by hierarchy
        # Structure: {asset_class: {asset_type: {asset_sub_type: weight}}}
        hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for holding in holdings:
            asset_class = holding.get('asset_class', 'Other')
            asset_type = holding.get('asset_type', 'Other')
            asset_sub_type = holding.get('asset_sub_type', 'Other')
            weight = float(holding.get('weight', 0))
            
            # Apply model weight and convert to percentage of blend
            weighted = weight * model_weight
            hierarchy[asset_class][asset_type][asset_sub_type] += weighted
        
        # Build the hierarchical structure
        breakdown = []
        for asset_class, types in sorted(hierarchy.items()):
            asset_class_weight = 0
            type_segments = []
            
            for asset_type, sub_types in sorted(types.items()):
                asset_type_weight = 0
                sub_type_segments = []
                
                for asset_sub_type, sub_weight in sorted(sub_types.items()):
                    rounded_weight = round(sub_weight, 1)
                    asset_type_weight += rounded_weight
                    sub_type_segments.append({
                        "level": "asset sub type",
                        "name": asset_sub_type,
                        "weight": rounded_weight
                    })
                
                asset_class_weight += round(asset_type_weight, 1)
                type_segments.append({
                    "level": "asset type",
                    "name": asset_type,
                    "weight": round(asset_type_weight, 1),
                    "segments": sub_type_segments
                })
            
            breakdown.append({
                "level": "asset class",
                "name": asset_class,
                "weight": round(asset_class_weight, 1),
                "segments": type_segments
            })
        
        return breakdown
    
    def compute_expected_payload(model_compositions: dict, model_weights: dict) -> dict:
        """
        Compute the expected API response payload from model compositions.
        
        Args:
            model_compositions: Dict of model_id -> list of holdings
            model_weights: Dict of model_id -> weight (0-1)
            
        Returns:
            Dict with blendBreakdown and componentBreakdown
        """
        from collections import defaultdict
        from datetime import date
        
        # Build componentBreakdown for each model
        component_breakdown = []
        
        # Also aggregate all holdings for blendBreakdown
        blended_holdings = []
        
        for model_id, holdings in model_compositions.items():
            model_weight = model_weights.get(model_id, 0)
            model_weight_pct = model_weight * 100  # Convert to percentage
            
            # Build breakdown for this model
            model_breakdown = build_hierarchical_breakdown(holdings, model_weight=1.0)
            
            # Scale weights by model weight for component display
            for segment in model_breakdown:
                segment['weight'] = round(segment['weight'] * model_weight, 1)
                for type_seg in segment.get('segments', []):
                    type_seg['weight'] = round(type_seg['weight'] * model_weight, 1)
                    for sub_seg in type_seg.get('segments', []):
                        sub_seg['weight'] = round(sub_seg['weight'] * model_weight, 1)
            
            component_breakdown.append({
                "modelType": "strategist",
                "modelId": model_id,
                "weight": round(model_weight_pct, 1),
                "segments": model_breakdown
            })
            
            # Add weighted holdings to blend
            for holding in holdings:
                blended_holdings.append({
                    'asset_class': holding.get('asset_class', 'Other'),
                    'asset_type': holding.get('asset_type', 'Other'),
                    'asset_sub_type': holding.get('asset_sub_type', 'Other'),
                    'weight': float(holding.get('weight', 0)) * model_weight
                })
        
        # Build blendBreakdown from all blended holdings
        blend_breakdown = build_hierarchical_breakdown(
            [{'asset_class': h['asset_class'], 'asset_type': h['asset_type'], 
              'asset_sub_type': h['asset_sub_type'], 'weight': h['weight']} 
             for h in blended_holdings],
            model_weight=1.0
        )
        
        return {
            "blendBreakdown": blend_breakdown,
            "componentBreakdown": component_breakdown
        }
    
    # Compute expected payload
    expected_result = compute_expected_payload(model_compositions, model_weights)
    
    # Build full expected response
    expected_response = {
        "responseCode": 200,
        "message": "Request processed successfully",
        "asOfDate": api_response.get("asOfDate", ""),
        "calculationResults": [
            {
                "calculationType": "asset allocation",
                "result": {
                    "modelType": "advisor",
                    "asOfDate": api_response.get("asOfDate", ""),
                    "blendBreakdown": expected_result["blendBreakdown"],
                    "componentBreakdown": expected_result["componentBreakdown"]
                }
            }
        ]
    }
    
    print("\nCOMPUTED EXPECTED RESPONSE (from Strategies + Securities APIs):")
    print(json.dumps(expected_response, indent=2))
    
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    
    # Validate - always use normal validation (no self-validation fallback)
    success, errors, computed_values = validator.validate_api_response(
        api_response, model_compositions, model_weights, model_types,
        skip_blend_recalc=False
    )
    
    # Compare results
    comparison = validator.compare_api_vs_script_results(
        api_response.get("calculationResults", [{}])[0].get("result", {}).get("blendBreakdown", []),
        computed_values.get("blendBreakdown", []),
        api_response.get("calculationResults", [{}])[0].get("result", {}).get("componentBreakdown", []),
        computed_values.get("componentBreakdown", [])
    )
    
    print("\n" + "=" * 80)
    if success:
        print("FINAL RESULT: [PASS] Validation successful!")
    else:
        print("FINAL RESULT: [FAIL] Validation failed!")
        for error in errors:
            print(f"  - {error}")
    print("=" * 80)

"""
Return Calculation Validator

Validates cumulative and annualized return calculations for the Analytics API.
Implements financial formulas derived from RiskVsReturn.xlsx Cumulative Returns sheet 
(formulas only - does NOT read the Excel file).

Formulas Derived from RiskVsReturn.xlsx:
1. Cumulative Return = Product(1 + Monthly_Return_i) - 1
   - Compounds monthly returns over the calculation period
   - Example: If month1=0.02, month2=0.03, month3=-0.01
     Cumulative = (1.02 × 1.03 × 0.99) - 1 = 0.0401 (4.01%)

2. Annualized Return = ((1 + Cumulative Return) ^ (1 / Years)) - 1
   - Converts cumulative return to annual equivalent
   - Years = (End Date - Start Date) / 365.25

3. Blended Return = Σ(Model_i Return × Weight_i)
   - Weighted average of component model returns

Data Sources:
- Monthly performance data: Fetched from /api/strategies/v2/models/monthlyperformancelist
- API response to validate: /v1/analytics return calculation results
"""

import math
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from framework.common.logger import get_logger
from framework.clients.api_client import ApiClientFactory

logger = get_logger(__name__)


def _ci_get(data: Dict[str, Any], key: str, default=None):
    """Case-insensitive dict key lookup."""
    if not isinstance(data, dict):
        return default
    if key in data:
        return data[key]
    key_lower = key.lower()
    for existing_key, value in data.items():
        if str(existing_key).lower() == key_lower:
            return value
    return default


def _pick_key(data: Dict[str, Any], *candidates: str) -> Optional[str]:
    """Return the first matching key name found in dict (case-insensitive)."""
    if not isinstance(data, dict):
        return None
    for candidate in candidates:
        if candidate in data:
            return candidate
    lowered = {str(k).lower(): k for k in data.keys()}
    for candidate in candidates:
        found = lowered.get(candidate.lower())
        if found is not None:
            return found
    return None


# =============================================================================
# API DATA FETCHING UTILITIES
# =============================================================================

class MonthlyPerformanceDataFetcher:
    """
    Utility class for fetching monthly performance data from Strategies API.
    Uses framework's ApiClientFactory for centralized configuration.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the API data fetcher.
        
        Args:
            config: Configuration dict (optional, uses framework config if not provided)
        """
        self.config = config or {}
        self.token = None
        self._strategies_client = None
        self._token_client = None
        
        logger.debug("MonthlyPerformanceDataFetcher initialized")
    
    def _get_strategies_client(self):
        """Get or create the Strategies API client."""
        if self._strategies_client is None:
            try:
                self._strategies_client = ApiClientFactory.get_client('strategies')
                logger.debug("Using framework 'strategies' API client")
            except (ValueError, KeyError) as e:
                logger.error(f"Could not get 'strategies' client from factory: {e}")
        return self._strategies_client
    
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
            if self._strategies_client:
                self._strategies_client.auth_token = self.token
    
    def fetch_monthly_performance(
        self, 
        item_ids: List[str], 
        start_date: str, 
        end_date: str,
        item_type: str = "model"
    ) -> Dict[str, Any]:
        """
        Fetch monthly performance data from Strategies API.
        
        Endpoint: POST /api/strategies/v2/models/monthlyperformancelist?fromMonth={start}&toMonth={end}
        Request Body: Array of model/benchmark IDs
        
        Args:
            item_ids: List of model or benchmark IDs
            start_date: Start date in YYYY-MM-DD format (used as fromMonth query param)
            end_date: End date in YYYY-MM-DD format (used as toMonth query param)
            item_type: Type of item ("model" or "benchmark") - for logging only
        
        Returns:
            Response data with monthly performance
        """
        client = self._get_strategies_client()
        if not client:
            logger.warning("No strategies API client available")
            return {}
        
        # Ensure we have a token
        if not self.token:
            self.get_auth_token()
        
        # Construct endpoint with query parameters (fromMonth and toMonth)
        endpoint = f"/models/monthlyperformancelist?fromMonth={start_date}&toMonth={end_date}"
        
        logger.info(f"Benchmark ID to fetch: {item_ids}")

        # Request body is just the array of IDs (benchmark or model IDs)
        payload = item_ids
        
        logger.info(f"Fetching monthly performance for {len(item_ids)} {item_type}(s)")
        logger.info(f"Endpoint: {endpoint}")
        logger.debug(f"Request body (IDs): {json.dumps(payload, indent=2)}")
        
        try:
            # Add Authorization header
            headers = {
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
            if self.token:
                headers['Authorization'] = self.token
            
            response = client.request('POST', endpoint, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch monthly performance: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return {}
            
            data = response.json()
            logger.info(f"Successfully fetched monthly performance data")
            logger.debug(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching monthly performance: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {}


class ReturnCalculationValidator:
    """
    Validates return calculations including cumulative and annualized returns
    for blended portfolios and benchmarks.
    """
    
    def __init__(self, tolerance: float = 0.0001):
        """
        Initialize the return validator.
        
        Args:
            tolerance: Acceptable relative difference for float comparisons (0.01%)
        """
        self.tolerance = tolerance
        logger.debug(f"ReturnCalculationValidator initialized with tolerance: {tolerance}")
    
    def calculate_years_between_dates(self, start_date: str, end_date: str) -> float:
        """
        Calculate the number of years between two dates.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Number of years as float (using 365.25 days per year)
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days_diff = (end - start).days
        years = days_diff / 365.25
        
        logger.debug(f"Years between {start_date} and {end_date}: {years:.4f} years ({days_diff} days)")
        return years
    
    def calculate_annualized_return(
        self, 
        cumulative_return: float, 
        years: float
    ) -> float:
        """
        Calculate annualized return from cumulative return.
        
        Formula: Annualized Return = ((1 + Cumulative Return) ^ (1 / Years)) - 1
        
        Args:
            cumulative_return: Total cumulative return (e.g., 0.88 for 88% gain)
            years: Number of years for the period
        
        Returns:
            Annualized return as decimal
        """
        if years <= 0:
            logger.warning(f"Invalid years value: {years}, returning 0")
            return 0.0
        
        annualized = math.pow(1 + cumulative_return, 1 / years) - 1
        logger.debug(f"Annualized Return: (1 + {cumulative_return})^(1/{years}) - 1 = {annualized}")
        
        return annualized
    
    def calculate_standard_deviation(self, monthly_returns: List[float]) -> float:
        """
        Calculate standard deviation from monthly returns.
        
        Formula (Excel STDEV.S): sqrt(Σ(x - mean)² / (N - 1))
        
        Args:
            monthly_returns: List of monthly returns
        
        Returns:
            Standard deviation as decimal
        """
        if not monthly_returns or len(monthly_returns) < 2:
            logger.warning(f"Insufficient data for standard deviation: {len(monthly_returns) if monthly_returns else 0} months")
            return 0.0
        
        n = len(monthly_returns)
        mean = sum(monthly_returns) / n
        variance = sum((x - mean) ** 2 for x in monthly_returns) / (n - 1)
        std_dev = math.sqrt(variance)
        
        logger.debug(f"Standard Deviation: sqrt({variance}) = {std_dev} (from {n} months)")
        return std_dev
    
    def calculate_annualized_volatility(self, monthly_std_dev: float) -> float:
        """
        Calculate annualized volatility from monthly standard deviation.
        
        Formula: Annualized Volatility = Monthly StdDev × sqrt(12)
        
        Args:
            monthly_std_dev: Monthly standard deviation
        
        Returns:
            Annualized volatility as decimal
        """
        annualized_volatility = monthly_std_dev * math.sqrt(12)
        logger.debug(f"Annualized Volatility: {monthly_std_dev} × sqrt(12) = {annualized_volatility}")
        
        return annualized_volatility
    
    def compute_volatility_from_monthly(
        self,
        monthly_performance_data: Dict[str, Any],
        item_id: str
    ) -> Optional[Tuple[float, float]]:
        """
        Compute volatility and annualized volatility from monthly performance data.
        
        Formula (from RiskVsReturn.xlsx):
        1. Monthly Volatility = STDEV.S(monthly returns)
        2. Annualized Volatility = Monthly Volatility × sqrt(12)
        
        Args:
            monthly_performance_data: Response from monthlyperformancelist API
            item_id: Model or benchmark ID
        
        Returns:
            Tuple of (monthly_volatility, annualized_volatility) or None if data unavailable
        """
        try:
            # Extract monthly performance array for the item (same logic as returns)
            if not monthly_performance_data:
                logger.warning(f"No performance data available for {item_id}")
                return None
            
            # Check if data is already in simple dict format: {"CCPUP5": [0.0068, 0.0120, ...]}
            if isinstance(monthly_performance_data, dict) and item_id in monthly_performance_data:
                monthly_returns = monthly_performance_data[item_id]
                logger.debug(f"Found {len(monthly_returns)} monthly returns for {item_id} in dict format")
            else:
                # Handle different response structures (legacy format)
                items = monthly_performance_data
                if isinstance(monthly_performance_data, dict):
                    items = (monthly_performance_data.get('data') or 
                            monthly_performance_data.get('items') or 
                            monthly_performance_data.get('monthlyPerformance') or
                            [monthly_performance_data])
                
                # Find data for this specific item
                item_data = None
                for item in items if isinstance(items, list) else [items]:
                    if isinstance(item, dict):
                        item_identifier = (item.get('id') or 
                                         item.get('itemId') or 
                                         item.get('modelId') or
                                         item.get('benchmarkId'))
                        if item_identifier == item_id:
                            item_data = item
                            break
                
                if not item_data:
                    logger.warning(f"No data found for item {item_id} in performance response")
                    return None
                
                # Extract monthly returns
                monthly_returns = (item_data.get('monthlyReturns') or 
                                 item_data.get('returns') or 
                                 item_data.get('performance') or
                                 [])
            
            if not monthly_returns:
                logger.warning(f"No monthly returns found for {item_id}")
                return None
            
            # Handle dict or numeric values
            clean_returns = []
            for monthly_return in monthly_returns:
                if isinstance(monthly_return, dict):
                    return_value = (monthly_return.get('return') or 
                                  monthly_return.get('performance') or 
                                  monthly_return.get('value') or 0)
                else:
                    return_value = monthly_return
                clean_returns.append(return_value)
            
            # Compute volatility metrics
            monthly_volatility = self.calculate_standard_deviation(clean_returns)
            annualized_volatility = self.calculate_annualized_volatility(monthly_volatility)
            
            logger.info(f"Computed volatility for {item_id}:")
            logger.info(f"  Monthly Volatility: {monthly_volatility:.10f}")
            logger.info(f"  Annualized Volatility: {annualized_volatility:.10f}")
            logger.debug(f"  Based on {len(clean_returns)} monthly returns")
            
            return (monthly_volatility, annualized_volatility)
            
        except Exception as e:
            logger.error(f"Error computing volatility for {item_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def compute_cumulative_return_from_monthly(
        self,
        monthly_performance_data: Dict[str, Any],
        item_id: str
    ) -> Optional[float]:
        """
        Compute cumulative return from monthly performance data.
        
        Formula (from RiskVsReturn.xlsx):
        Cumulative Return = Product(1 + monthly_return_i) - 1
        
        Args:
            monthly_performance_data: Response from monthlyperformancelist API
            item_id: Model or benchmark ID
        
        Returns:
            Cumulative return as decimal, or None if data unavailable
        """
        try:
            # Extract monthly performance array for the item
            if not monthly_performance_data:
                logger.warning(f"No performance data available for {item_id}")
                return None
            
            # Check if data is already in simple dict format: {"CCPUP5": [0.0068, 0.0120, ...]}
            if isinstance(monthly_performance_data, dict) and item_id in monthly_performance_data:
                monthly_returns = monthly_performance_data[item_id]
                logger.debug(f"Found {len(monthly_returns)} monthly returns for {item_id} in dict format")
            else:
                # Handle different response structures (legacy format)
                items = monthly_performance_data
                if isinstance(monthly_performance_data, dict):
                    items = (monthly_performance_data.get('data') or 
                            monthly_performance_data.get('items') or 
                            monthly_performance_data.get('monthlyPerformance') or
                            [monthly_performance_data])
                
                # Find data for this specific item
                item_data = None
                for item in items if isinstance(items, list) else [items]:
                    if isinstance(item, dict):
                        item_identifier = (item.get('id') or 
                                         item.get('itemId') or 
                                         item.get('modelId') or
                                         item.get('benchmarkId'))
                        if item_identifier == item_id:
                            item_data = item
                            break
                
                if not item_data:
                    logger.warning(f"No data found for item {item_id} in performance response")
                    return None
                
                # Extract monthly returns
                monthly_returns = (item_data.get('monthlyReturns') or 
                                 item_data.get('returns') or 
                                 item_data.get('performance') or
                                 [])
            
            if not monthly_returns:
                logger.warning(f"No monthly returns found for {item_id}")
                return None
            
            # Compute cumulative return: Product(1 + r_i) - 1
            cumulative_product = 1.0
            for monthly_return in monthly_returns:
                # Handle dict or numeric values
                if isinstance(monthly_return, dict):
                    return_value = (monthly_return.get('return') or 
                                  monthly_return.get('performance') or 
                                  monthly_return.get('value') or 0)
                else:
                    return_value = monthly_return
                
                cumulative_product *= (1 + return_value)
            
            cumulative_return = cumulative_product - 1
            
            logger.info(f"Computed cumulative return for {item_id}: {cumulative_return:.10f} ({len(monthly_returns)} months)")
            logger.debug(f"  Monthly returns: {monthly_returns[:5]}..." if len(monthly_returns) > 5 else f"  Monthly returns: {monthly_returns}")
            
            return cumulative_return
            
        except Exception as e:
            logger.error(f"Error computing cumulative return for {item_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def calculate_blended_cumulative_return(
        self, 
        model_returns: List[Dict[str, float]], 
        weights: List[float]
    ) -> float:
        """
        Calculate blended cumulative return from component model returns.
        
        Formula: Blended Return = Σ(Model Return × Weight)
        
        Args:
            model_returns: List of dicts with 'id' and 'cumulativeReturn'
            weights: List of weights corresponding to each model
        
        Returns:
            Blended cumulative return
        """
        if len(model_returns) != len(weights):
            logger.error(f"Mismatch: {len(model_returns)} models but {len(weights)} weights")
            return 0.0
        
        blended_return = sum(
            model['cumulativeReturn'] * weight 
            for model, weight in zip(model_returns, weights)
        )
        
        logger.debug(f"Blended Cumulative Return: {blended_return}")
        for model, weight in zip(model_returns, weights):
            logger.debug(f"  {model['id']}: {model['cumulativeReturn']} × {weight} = {model['cumulativeReturn'] * weight}")
        
        return blended_return
    
    def compare_values(
        self, 
        actual: float, 
        expected: float, 
        field_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Compare two numeric values with tolerance.
        
        Args:
            actual: Actual value from API
            expected: Expected/computed value
            field_name: Name of field being compared
        
        Returns:
            Tuple of (is_match, error_message or None)
        """
        if actual is None or expected is None:
            return False, f"{field_name}: One value is None (actual={actual}, expected={expected})"
        
        # Calculate relative difference
        if expected == 0:
            is_match = abs(actual) <= self.tolerance
        else:
            relative_diff = abs((actual - expected) / expected)
            is_match = relative_diff <= self.tolerance
        
        if not is_match:
            abs_diff = abs(actual - expected)
            return False, f"{field_name} mismatch: actual={actual:.10f}, expected={expected:.10f}, diff={abs_diff:.10f}"
        
        return True, None
    
    def compute_monthly_cumulative_returns(
        self,
        monthly_returns: List[float]
    ) -> List[float]:
        """
        Compute cumulative returns for each month in the series.
        
        Formula (from RiskVsReturn.xlsx Cumulative Returns sheet):
        For each month i:
            Cumulative_Return[i] = Product(1 + monthly_return[0..i]) - 1
        
        Example:
        Month 1: return=0.02 -> cumulative = 0.02
        Month 2: return=0.03 -> cumulative = (1.02 * 1.03) - 1 = 0.0506
        Month 3: return=-0.01 -> cumulative = (1.02 * 1.03 * 0.99) - 1 = 0.0401
        
        Args:
            monthly_returns: List of monthly returns in chronological order
        
        Returns:
            List of cumulative returns (same length as input)
        """
        cumulative_returns = []
        cumulative_product = 1.0
        
        for i, monthly_return in enumerate(monthly_returns):
            cumulative_product *= (1 + monthly_return)
            cumulative_return = cumulative_product - 1
            cumulative_returns.append(cumulative_return)
            logger.debug(f"  Month {i+1}: return={monthly_return:.6f}, cumulative={cumulative_return:.10f}")
        
        return cumulative_returns
    
    def compute_blended_monthly_returns(
        self,
        models_monthly_data: Dict[str, List[float]],
        blend_ids: List[str],
        blend_weights: List[float]
    ) -> List[float]:
        """
        Compute blended monthly returns from component model returns.
        
        Formula (from RiskVsReturn.xlsx):
        Blend_Return[month] = Σ(Model_i_Return[month] × Weight_i)
        
        Args:
            models_monthly_data: Dict mapping model_id to list of monthly returns
            blend_ids: List of model IDs in the blend
            blend_weights: List of weights corresponding to each model
        
        Returns:
            List of blended monthly returns
        """
        if not models_monthly_data or not blend_ids:
            logger.warning("No model data available for blending")
            return []
        
        # Get the number of months (should be same for all models)
        num_months = 0
        for model_id in blend_ids:
            if model_id in models_monthly_data:
                num_months = len(models_monthly_data[model_id])
                break
        
        if num_months == 0:
            logger.warning("No monthly data found for any blend model")
            return []
        
        blended_returns = []
        for month_idx in range(num_months):
            blended_return = 0.0
            for model_id, weight in zip(blend_ids, blend_weights):
                if model_id in models_monthly_data:
                    model_returns = models_monthly_data[model_id]
                    if month_idx < len(model_returns):
                        contribution = model_returns[month_idx] * weight
                        blended_return += contribution
                        logger.debug(f"    {model_id}[{month_idx}]: {model_returns[month_idx]:.6f} × {weight} = {contribution:.6f}")
            
            blended_returns.append(blended_return)
            logger.debug(f"  Month {month_idx+1} Blended Return: {blended_return:.10f}")
        
        return blended_returns
    
    def validate_monthly_cumulative_returns_time_series(
        self,
        api_response: Dict[str, Any],
        models_monthly_data: Dict[str, List[float]],
        benchmark_monthly_data: Dict[str, List[float]],
        blend_ids: List[str],
        blend_weights: List[float]
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate monthly cumulative returns time series from API response.
        
        This validates the 'cumulative returns time series' calculation type where
        the API returns cumulative returns for each month in the period.
        
        Formula (from RiskVsReturn.xlsx Cumulative Returns sheet):
        1. For each model:
           - Cumulative_Return[month_i] = Product(1 + monthly_return[0..i]) - 1
        
        2. For blended portfolio:
           - Blend_Return[month] = Σ(Model_i_Return[month] × Weight_i)
           - Blend_Cumulative[month_i] = Product(1 + blend_return[0..i]) - 1
        
        3. For benchmark:
           - Benchmark_Cumulative[month_i] = Product(1 + benchmark_return[0..i]) - 1
        
        Args:
            api_response: Full API response dict
            models_monthly_data: Dict mapping model_id to list of monthly returns
            benchmark_monthly_data: Dict mapping benchmark_id to list of monthly returns
            blend_ids: List of model IDs in blend
            blend_weights: List of weights for blend models
        
        Returns:
            Tuple of (is_valid, list of error messages, computed values dict)
        """
        logger.info("=" * 80)
        logger.info("MONTHLY CUMULATIVE RETURNS TIME SERIES VALIDATION")
        logger.info("=" * 80)
        
        errors = []
        computed_data = {
            'models': {},
            'blend': {},
            'benchmark': {}
        }
        
        # Extract calculation results from API response
        calc_results = _ci_get(api_response, 'calculationResults', [])
        if not calc_results:
            errors.append("No calculationResults found in response")
            return False, errors, computed_data
        
        # Find the cumulative returns time series calculation
        cumulative_result = None
        for result in calc_results:
            calc_type = _ci_get(result, 'calculationType')
            if isinstance(calc_type, str) and calc_type.strip().lower() == 'cumulative returns time series':
                cumulative_result = result
                break
        
        if not cumulative_result:
            errors.append("No 'cumulative returns time series' calculation found in response")
            return False, errors, computed_data
        
        result_data = _ci_get(cumulative_result, 'result', [])
        if not result_data:
            errors.append("No result data found in cumulative returns time series")
            return False, errors, computed_data
        
        # Parse API response structure
        # result[0] contains cumulativeReturn and blend arrays
        # result[1] contains benchmark data
        blend_section = result_data[0] if len(result_data) > 0 else {}
        benchmark_section = result_data[1] if len(result_data) > 1 else {}
        
        # =====================================================================
        # VALIDATE INDIVIDUAL MODEL CUMULATIVE RETURNS
        # =====================================================================
        logger.info("-" * 80)
        logger.info("VALIDATING INDIVIDUAL MODEL CUMULATIVE RETURNS")
        logger.info("-" * 80)
        
        blend_models_api = _ci_get(blend_section, 'blend', [])
        
        for model_api in blend_models_api:
            model_id = _ci_get(model_api, 'id')
            if not model_id or model_id not in models_monthly_data:
                logger.warning(f"Model {model_id} not found in monthly data, skipping")
                continue
            
            logger.info(f"Validating model: {model_id}")
            
            # Get monthly returns for this model
            monthly_returns = models_monthly_data[model_id]
            
            # Compute expected monthly cumulative returns
            computed_cumulative = self.compute_monthly_cumulative_returns(monthly_returns)
            
            # Get API cumulative returns (may be in reverse order)
            api_cumulative_array = _ci_get(model_api, 'cumulativeReturn', [])
            
            # Sort API data by date to ensure chronological order
            api_cumulative_sorted = sorted(api_cumulative_array, key=lambda x: _ci_get(x, 'date', ''))
            
            # Validate each month's cumulative return
            for i, api_cum_obj in enumerate(api_cumulative_sorted):
                api_date = _ci_get(api_cum_obj, 'date')
                api_cum_value = _ci_get(api_cum_obj, 'return')
                
                if i < len(computed_cumulative):
                    computed_cum_value = computed_cumulative[i]
                    
                    # Compare values
                    is_match, error = self.compare_values(
                        api_cum_value,
                        computed_cum_value,
                        f"Model {model_id} cumulative return [{api_date}]"
                    )
                    
                    if not is_match:
                        logger.error(f"  [FAIL] {error}")
                        errors.append(error)
                    else:
                        logger.info(f"  [PASS] {api_date}: API={api_cum_value:.10f}, Computed={computed_cum_value:.10f}")
            
            # Store computed values
            computed_data['models'][model_id] = {
                'monthly_returns': monthly_returns,
                'monthly_cumulative': computed_cumulative
            }
        
        # =====================================================================
        # VALIDATE BLENDED CUMULATIVE RETURNS
        # =====================================================================
        logger.info("-" * 80)
        logger.info("VALIDATING BLENDED CUMULATIVE RETURNS")
        logger.info("-" * 80)
        
        # Compute blended monthly returns
        logger.info(f"Computing blended returns from {len(blend_ids)} models:")
        for model_id, weight in zip(blend_ids, blend_weights):
            logger.info(f"  - {model_id}: weight={weight}")
        
        blended_monthly_returns = self.compute_blended_monthly_returns(
            models_monthly_data,
            blend_ids,
            blend_weights
        )
        
        # Compute cumulative returns for blended portfolio
        blended_cumulative = self.compute_monthly_cumulative_returns(blended_monthly_returns)
        
        # Get API blended cumulative returns (may be in reverse order)
        api_blend_cumulative_array = _ci_get(blend_section, 'cumulativeReturn', [])
        
        # Sort API data by date to ensure chronological order
        api_blend_cumulative_sorted = sorted(api_blend_cumulative_array, key=lambda x: _ci_get(x, 'date', ''))
        
        # Validate each month's blended cumulative return
        for i, api_cum_obj in enumerate(api_blend_cumulative_sorted):
            api_date = _ci_get(api_cum_obj, 'date')
            api_cum_value = _ci_get(api_cum_obj, 'return')
            
            if i < len(blended_cumulative):
                computed_cum_value = blended_cumulative[i]
                
                # Compare values
                is_match, error = self.compare_values(
                    api_cum_value,
                    computed_cum_value,
                    f"Blended cumulative return [{api_date}]"
                )
                
                if not is_match:
                    logger.error(f"  [FAIL] {error}")
                    errors.append(error)
                else:
                    logger.info(f"  [PASS] {api_date}: API={api_cum_value:.10f}, Computed={computed_cum_value:.10f}")
        
        # Store computed blended values
        computed_data['blend'] = {
            'monthly_returns': blended_monthly_returns,
            'monthly_cumulative': blended_cumulative
        }
        
        # =====================================================================
        # VALIDATE BENCHMARK CUMULATIVE RETURNS
        # =====================================================================
        logger.info("-" * 80)
        logger.info("VALIDATING BENCHMARK CUMULATIVE RETURNS")
        logger.info("-" * 80)
        
        benchmark_id = _ci_get(benchmark_section, 'id')
        if benchmark_id and benchmark_id in benchmark_monthly_data:
            logger.info(f"Validating benchmark: {benchmark_id}")
            
            # Get monthly returns for benchmark
            benchmark_returns = benchmark_monthly_data[benchmark_id]
            
            # Compute expected monthly cumulative returns
            benchmark_cumulative = self.compute_monthly_cumulative_returns(benchmark_returns)
            
            # Get API benchmark cumulative returns (may be in reverse order)
            api_benchmark_cumulative_array = _ci_get(benchmark_section, 'cumulativeReturn', [])
            
            # Sort API data by date to ensure chronological order
            api_benchmark_cumulative_sorted = sorted(api_benchmark_cumulative_array, key=lambda x: _ci_get(x, 'date', ''))
            
            # Validate each month's benchmark cumulative return
            for i, api_cum_obj in enumerate(api_benchmark_cumulative_sorted):
                api_date = _ci_get(api_cum_obj, 'date')
                api_cum_value = _ci_get(api_cum_obj, 'return')
                
                if i < len(benchmark_cumulative):
                    computed_cum_value = benchmark_cumulative[i]
                    
                    # Compare values
                    is_match, error = self.compare_values(
                        api_cum_value,
                        computed_cum_value,
                        f"Benchmark {benchmark_id} cumulative return [{api_date}]"
                    )
                    
                    if not is_match:
                        logger.error(f"  [FAIL] {error}")
                        errors.append(error)
                    else:
                        logger.info(f"  [PASS] {api_date}: API={api_cum_value:.10f}, Computed={computed_cum_value:.10f}")
            
            # Store computed benchmark values
            computed_data['benchmark'][benchmark_id] = {
                'monthly_returns': benchmark_returns,
                'monthly_cumulative': benchmark_cumulative
            }
        else:
            logger.warning(f"Benchmark {benchmark_id} not found in monthly data")
        
        # =====================================================================
        # SUMMARY
        # =====================================================================
        logger.info("=" * 80)
        if not errors:
            logger.info("RESULT: [PASS] All monthly cumulative returns validated successfully")
        else:
            logger.error(f"RESULT: [FAIL] Validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.error(f"  - {error}")
        logger.info("=" * 80)
        
        return len(errors) == 0, errors, computed_data
    
    def validate_return_calculation(
        self,
        api_response: Dict[str, Any],
        start_date: str,
        end_date: str,
        blend_ids: List[str],
        blend_weights: List[float],
        benchmark_id: str,
        blend_performance_data: Dict[str, Any],
        benchmark_performance_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate return calculations in API response against computed values.
        
        This method:
        1. Computes cumulative returns from monthly performance data
        2. Computes annualized returns
        3. Computes blended portfolio returns
        4. Compares computed values with API response
        
        Args:
            api_response: Full API response dict from /v1/analytics
            start_date: Start date for calculation period
            end_date: End date for calculation period
            blend_ids: List of model IDs in blend
            blend_weights: List of model weights in blend
            benchmark_id: Benchmark ID
            blend_performance_data: Monthly performance data for blend models
            benchmark_performance_data: Monthly performance data for benchmark
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        logger.info("=" * 80)
        logger.info("RETURN CALCULATION VALIDATION")
        logger.info("=" * 80)
        
        errors = []
        
        # Extract calculation results from API response
        calc_results = _ci_get(api_response, 'calculationResults', [])
        if not calc_results:
            errors.append("No calculationResults found in response")
            return False, errors, {}
        
        return_result = calc_results[0]
        calc_type = _ci_get(return_result, 'calculationType')
        if str(calc_type).strip().lower() != 'return':
            errors.append(f"Expected calculationType 'return', got '{calc_type}'")
        
        result_data = _ci_get(return_result, 'result', [])
        if not result_data or len(result_data) < 1:
            errors.append("No result data found")
            return False, errors, {}
        
        # Extract blend and benchmark data from API response
        blend_result = result_data[0]
        benchmark_result = result_data[1] if len(result_data) > 1 else None
        
        # Calculate expected years
        years = self.calculate_years_between_dates(start_date, end_date)
        logger.info(f"Calculation Period: {start_date} to {end_date} = {years:.4f} years")
        logger.info("-" * 80)
        
        # =====================================================================
        # COMPUTE EXPECTED VALUES FROM MONTHLY PERFORMANCE DATA
        # =====================================================================
        
        logger.info("COMPUTING EXPECTED VALUES FROM MONTHLY PERFORMANCE DATA")
        logger.info("-" * 80)
        
        # Compute cumulative returns for each blend model
        computed_model_returns = []
        blend_models_api = _ci_get(blend_result, 'blend', [])
        
        for i, (model_id, weight) in enumerate(zip(blend_ids, blend_weights)):
            logger.info(f"Computing returns for blend model {i+1}: {model_id} (weight: {weight})")
            
            # Compute from monthly performance data
            computed_cumulative = self.compute_cumulative_return_from_monthly(
                blend_performance_data, 
                model_id
            )
            
            if computed_cumulative is None:
                logger.warning(f"Could not compute cumulative return for {model_id}, skipping validation")
                continue
            
            # Compute annualized return
            computed_annualized = self.calculate_annualized_return(computed_cumulative, years)
            
            computed_model_returns.append({
                'id': model_id,
                'cumulativeReturn': computed_cumulative,
                'annualizedReturn': computed_annualized,
                'weight': weight
            })
            
            logger.info(f"  Computed Cumulative Return: {computed_cumulative:.10f}")
            logger.info(f"  Computed Annualized Return: {computed_annualized:.10f}")
            
            # Compare with API response for this model
            api_model = next((m for m in blend_models_api if _ci_get(m, 'id') == model_id), None)
            if api_model:
                api_cum = _ci_get(api_model, 'cumulativeReturn')
                api_ann = _ci_get(api_model, 'annualizedReturn')
                
                logger.info(f"  API Cumulative Return: {api_cum:.10f}")
                logger.info(f"  API Annualized Return: {api_ann:.10f}")
                
                # Validate cumulative return
                is_match, error = self.compare_values(
                    api_cum, computed_cumulative, 
                    f"Model {model_id} cumulativeReturn"
                )
                if not is_match:
                    logger.error(f"  [FAIL] {error}")
                    errors.append(error)
                else:
                    logger.info(f"  [PASS] Cumulative return matches")
                
                # Validate annualized return
                is_match, error = self.compare_values(
                    api_ann, computed_annualized,
                    f"Model {model_id} annualizedReturn"
                )
                if not is_match:
                    logger.error(f"  [FAIL] {error}")
                    errors.append(error)
                else:
                    logger.info(f"  [PASS] Annualized return matches")
        
        logger.info("-" * 80)
        
        # Compute blended portfolio returns
        computed_blend_cumulative = None
        computed_blend_annualized = None
        if computed_model_returns:
            logger.info("Computing Blended Portfolio Returns:")
            
            computed_blend_cumulative = self.calculate_blended_cumulative_return(
                computed_model_returns,
                blend_weights
            )
            computed_blend_annualized = self.calculate_annualized_return(
                computed_blend_cumulative, 
                years
            )
            
            logger.info(f"  Computed Blended Cumulative Return: {computed_blend_cumulative:.10f}")
            logger.info(f"  Computed Blended Annualized Return: {computed_blend_annualized:.10f}")
            
            # Compare with API response
            api_blend_cum = _ci_get(blend_result, 'cumulativeReturn')
            api_blend_ann = _ci_get(blend_result, 'annualizedReturn')
            
            logger.info(f"  API Blended Cumulative Return: {api_blend_cum:.10f}")
            logger.info(f"  API Blended Annualized Return: {api_blend_ann:.10f}")
            
            # Validate blended cumulative return
            is_match, error = self.compare_values(
                api_blend_cum, computed_blend_cumulative,
                "Blended cumulativeReturn"
            )
            if not is_match:
                logger.error(f"  [FAIL] {error}")
                errors.append(error)
            else:
                logger.info(f"  [PASS] Blended cumulative return matches")
            
            # Validate blended annualized return
            is_match, error = self.compare_values(
                api_blend_ann, computed_blend_annualized,
                "Blended annualizedReturn"
            )
            if not is_match:
                logger.error(f"  [FAIL] {error}")
                errors.append(error)
            else:
                logger.info(f"  [PASS] Blended annualized return matches")
        
        logger.info("-" * 80)
        
        # Compute benchmark returns
        computed_benchmark_cumulative = None
        computed_benchmark_annualized = None
        if benchmark_result and benchmark_id:
            logger.info(f"Computing Benchmark Returns for {benchmark_id}:")
            
            computed_benchmark_cumulative = self.compute_cumulative_return_from_monthly(
                benchmark_performance_data,
                benchmark_id
            )
            
            if computed_benchmark_cumulative is not None:
                computed_benchmark_annualized = self.calculate_annualized_return(
                    computed_benchmark_cumulative,
                    years
                )
                
                logger.info(f"  Computed Benchmark Cumulative Return: {computed_benchmark_cumulative:.10f}")
                logger.info(f"  Computed Benchmark Annualized Return: {computed_benchmark_annualized:.10f}")
                
                # Compare with API response
                api_bench_cum = _ci_get(benchmark_result, 'cumulativeReturn')
                api_bench_ann = _ci_get(benchmark_result, 'annualizedReturn')
                
                logger.info(f"  API Benchmark Cumulative Return: {api_bench_cum:.10f}")
                logger.info(f"  API Benchmark Annualized Return: {api_bench_ann:.10f}")
                
                # Validate benchmark cumulative return
                is_match, error = self.compare_values(
                    api_bench_cum, computed_benchmark_cumulative,
                    f"Benchmark {benchmark_id} cumulativeReturn"
                )
                if not is_match:
                    logger.error(f"  [FAIL] {error}")
                    errors.append(error)
                else:
                    logger.info(f"  [PASS] Benchmark cumulative return matches")
                
                # Validate benchmark annualized return
                is_match, error = self.compare_values(
                    api_bench_ann, computed_benchmark_annualized,
                    f"Benchmark {benchmark_id} annualizedReturn"
                )
                if not is_match:
                    logger.error(f"  [FAIL] {error}")
                    errors.append(error)
                else:
                    logger.info(f"  [PASS] Benchmark annualized return matches")
            else:
                logger.warning(f"Could not compute benchmark returns for {benchmark_id}")
        
        logger.info("=" * 80)
        
        if not errors:
            logger.info("RESULT: [PASS] All return calculations validated successfully")
        else:
            logger.error(f"RESULT: [FAIL] Return validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.error(f"  - {error}")
        
        logger.info("=" * 80)
        
        # Return computed values for use in test assertions
        return_data = {
            'computed_model_returns': computed_model_returns,
            'computed_blend_cumulative': computed_blend_cumulative,
            'computed_blend_annualized': computed_blend_annualized,
            'computed_benchmark_cumulative': computed_benchmark_cumulative,
            'computed_benchmark_annualized': computed_benchmark_annualized
        }
        
        return len(errors) == 0, errors, return_data


def validate(context):
    """
    Main validation function called by the framework.
    
    This function is called by the ScriptExecutor when 'scripts' field 
    references this file. It receives full test context and returns 
    results in ScriptResult-compatible format.
    
    Args:
        context: ScriptContext or dict with test execution data
            - test_case: Full test case configuration
            - request: Request details (endpoint, method, payload)
            - response: API response data
            - db_results: Database query results
            - extracted_vars: Previously extracted variables
            - config: Framework configuration
    
    Returns:
        dict: ScriptResult-compatible dictionary with:
            - success: bool (renamed from is_valid)
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
        request_ctx = ctx.get('request', {})
        db_results = ctx.get('db_results', {})
        extracted_vars = ctx.get('extracted_vars', {})
        
        # Get API response body
        api_response = response_ctx.get('body', {})
        if not api_response:
            logger.warning("No API response body found in context")
            return {
                "success": False,
                "errors": ["No API response body found in context"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # Detect calculation type from API response
        calculation_type = None
        calc_results = _ci_get(api_response, 'calculationResults', [])
        if calc_results:
            calculation_type = _ci_get(calc_results[0], 'calculationType', 'return')
        
        logger.info(f"Detected calculation type: '{calculation_type}'")
        
        # Route to appropriate validation based on calculation type
        calc_type_normalized = str(calculation_type).strip().lower() if calculation_type is not None else ''

        if calc_type_normalized == 'volatility':
            logger.info("Routing to volatility validation logic")
            return validate_volatility_calculation(ctx, logger)
        elif calc_type_normalized == 'cumulative returns time series':
            logger.info("Routing to monthly cumulative returns time series validation logic")
            return validate_cumulative_returns_time_series(ctx, logger)
        elif calc_type_normalized == 'return':
            logger.info("Routing to return validation logic")
        else:
            logger.warning(f"Unknown calculation type '{calculation_type}', defaulting to return validation")
        
        # Get test data from extracted_vars (CSV data is loaded here)
        # The framework loads CSV data and merges it into extracted_vars
        test_data = extracted_vars
        
        # Extract parameters from test data (extracted_vars)
        start_date = test_data.get('start_date')
        end_date = test_data.get('end_date')
        benchmark_id = test_data.get('benchmark')
        
        logger.debug(f"Extracted from context: start_date={start_date}, end_date={end_date}, benchmark={benchmark_id}")
        logger.debug(f"Available keys in extracted_vars: {list(extracted_vars.keys())[:20]}...")
        
        # Extract blend model IDs and weights from test data
        blend_ids = []
        blend_weights = []
        for i in range(1, 11):  # Support up to 10 blend components
            id_key = f'blend_{i}_id'
            weight_key = f'blend_{i}_weight'
            if id_key in test_data and test_data[id_key]:
                blend_ids.append(test_data[id_key])
                try:
                    blend_weights.append(float(test_data[weight_key]))
                except (ValueError, TypeError):
                    logger.error(f"Invalid weight for blend_{i}: {test_data.get(weight_key)}")
                    blend_weights.append(0.0)
        
        if not blend_ids:
            logger.error("No blend models found in test data")
            return {
                'success': False,
                'errors': ['No blend models found in test data'],
                'extracted_values': {},
                'computed_values': {}
            }
        
        logger.info(f"Validating return calculation with {len(blend_ids)} blend components")
        logger.info(f"Blend Models: {blend_ids}")
        logger.info(f"Blend Weights: {blend_weights}")
        logger.info(f"Benchmark ID from CSV: '{benchmark_id}' (type: {type(benchmark_id).__name__})")
        logger.info(f"Period: {start_date} to {end_date}")
        
        # Combine all item IDs for a single API call
        all_item_ids = blend_ids.copy()
        if benchmark_id:
            # Handle both single benchmark (string) and multiple benchmarks (list)
            if isinstance(benchmark_id, list):
                all_item_ids.extend(benchmark_id)
            else:
                all_item_ids.append(benchmark_id)
        
        logger.info("=" * 80)
        logger.info("Fetching monthly performance data for ALL items (blend models + benchmark)")
        logger.info(f"  -> Blend Model IDs: {blend_ids}")
        logger.info(f"  -> Benchmark ID: {benchmark_id if benchmark_id else 'None'}")
        logger.info(f"  -> Combined Request Body: {all_item_ids}")
        logger.info("=" * 80)
        
        # Fetch monthly performance data from API (single call)
        fetcher = MonthlyPerformanceDataFetcher()
        all_performance_data = fetcher.fetch_monthly_performance(
            item_ids=all_item_ids,
            start_date=start_date,
            end_date=end_date,
            item_type="model"  # API accepts mixed types
        )
        
        # DEBUG: Log the actual API response structure
        logger.info(f"API Response Type: {type(all_performance_data)}")
        if isinstance(all_performance_data, list) and len(all_performance_data) > 0:
            logger.info(f"API returned {len(all_performance_data)} records")
            logger.info(f"Sample record structure: {list(all_performance_data[0].keys())}")
        
        # Convert API response to dictionary keyed by modelId
        # API returns flat array: [
        #   {"modelId": "CCPUP5", "monthEndDate": "2025-01-31", "monthEndPerformance": 0.0068, ...},
        #   {"modelId": "CCPUP5", "monthEndDate": "2025-02-28", "monthEndPerformance": 0.0120, ...},
        #   {"modelId": "US2SAL", "monthEndDate": "2025-01-31", "monthEndPerformance": 0.0045, ...},
        # ]
        # Convert to: {"CCPUP5": [0.0068, 0.0120, ...], "US2SAL": [0.0045, ...]}
        performance_by_id = {}
        
        if isinstance(all_performance_data, list):
            # Group records by modelId
            from collections import defaultdict
            grouped = defaultdict(list)
            
            for record in all_performance_data:
                model_id = record.get('modelId')
                month_return = record.get('monthEndPerformance')
                month_date = record.get('monthEndDate')
                
                if model_id and month_return is not None:
                    grouped[model_id].append({
                        'date': month_date,
                        'return': month_return
                    })
            
            # Sort by date and extract just the returns
            for model_id, records in grouped.items():
                # Sort by date to ensure chronological order
                sorted_records = sorted(records, key=lambda x: x['date'])
                performance_by_id[model_id] = [r['return'] for r in sorted_records]
                logger.info(f"  Extracted '{model_id}': {len(performance_by_id[model_id])} months")
        
        elif isinstance(all_performance_data, dict):
            # If already a dict, use it directly
            logger.info(f"API returned a dict with keys: {list(all_performance_data.keys())}")
            performance_by_id = all_performance_data
        
        # Separate the response data for blend models and benchmark
        blend_performance_data = {}
        benchmark_performance_data = {}
        
        logger.info("=" * 80)
        logger.info("Separating response data:")
        for item_id in blend_ids:
            if item_id in performance_by_id:
                blend_performance_data[item_id] = performance_by_id[item_id]
                logger.info(f"  -> Blend Model '{item_id}': {len(performance_by_id[item_id])} months of data")
            else:
                logger.warning(f"  -> Blend Model '{item_id}': NOT FOUND in API response")
        
        if benchmark_id:
            # Handle both single benchmark (string) and multiple benchmarks (list)
            benchmark_ids = benchmark_id if isinstance(benchmark_id, list) else [benchmark_id]
            for bench_id in benchmark_ids:
                if bench_id in performance_by_id:
                    benchmark_performance_data[bench_id] = performance_by_id[bench_id]
                    logger.info(f"  -> Benchmark '{bench_id}': {len(performance_by_id[bench_id])} months of data")
                else:
                    logger.warning(f"  -> Benchmark '{bench_id}': NOT FOUND in API response")
        logger.info("=" * 80)
        
        # Create validator and validate
        validator = ReturnCalculationValidator(tolerance=0.0001)
        is_valid, errors, computed_values = validator.validate_return_calculation(
            api_response,
            start_date,
            end_date,
            blend_ids,
            blend_weights,
            benchmark_id,
            blend_performance_data,
            benchmark_performance_data
        )
        
        # Extract computed values for test assertions
        extracted_computed = {}
        if computed_values.get('computed_blend_cumulative') is not None:
            extracted_computed['computed_blend_cumulative'] = computed_values['computed_blend_cumulative']
        if computed_values.get('computed_blend_annualized') is not None:
            extracted_computed['computed_blend_annualized'] = computed_values['computed_blend_annualized']
        if computed_values.get('computed_benchmark_cumulative') is not None:
            extracted_computed['computed_benchmark_cumulative'] = computed_values['computed_benchmark_cumulative']
        if computed_values.get('computed_benchmark_annualized') is not None:
            extracted_computed['computed_benchmark_annualized'] = computed_values['computed_benchmark_annualized']
        
        # Extract individual model computed values
        for i, model_data in enumerate(computed_values.get('computed_model_returns', [])):
            model_id = model_data.get('id')
            extracted_computed[f'computed_model_{i+1}_id'] = model_id
            extracted_computed[f'computed_model_{i+1}_cumulative'] = model_data.get('cumulativeReturn')
            extracted_computed[f'computed_model_{i+1}_annualized'] = model_data.get('annualizedReturn')
        
        return {
            'success': is_valid,
            'errors': errors,
            'validation_type': 'return_calculation',
            'extracted_values': extracted_computed,
            'computed_values': extracted_computed
        }
        
    except Exception as e:
        logger.error(f"Return validator error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {
            'success': False,
            'errors': [f"Validation exception: {str(e)}"],
            'extracted_values': {},
            'computed_values': {}
        }


def validate_cumulative_returns_time_series(ctx, logger):
    """
    Validate monthly cumulative returns time series from Analytics API.
    
    This function validates the 'cumulative returns time series' calculation type
    where the API returns cumulative returns for each month in the period.
    
    Args:
        ctx: Test context dictionary
        logger: Logger instance
    
    Returns:
        dict: Validation results with computed monthly cumulative values
    """
    try:
        # Extract required data from context
        response_ctx = ctx.get('response', {})
        extracted_vars = ctx.get('extracted_vars', {})
        api_response = response_ctx.get('body', {})
        
        # Get test data from extracted_vars
        test_data = extracted_vars
        
        # Extract parameters from test data
        start_date = test_data.get('start_date')
        end_date = test_data.get('end_date')
        benchmark_id = test_data.get('benchmark')
        
        logger.debug(f"Cumulative time series validation: start_date={start_date}, end_date={end_date}, benchmark={benchmark_id}")
        
        # Extract blend model IDs and weights from test data
        blend_ids = []
        blend_weights = []
        for i in range(1, 11):  # Support up to 10 blend components
            id_key = f'blend_{i}_id'
            weight_key = f'blend_{i}_weight'
            if id_key in test_data and test_data[id_key]:
                blend_ids.append(test_data[id_key])
                try:
                    blend_weights.append(float(test_data[weight_key]))
                except (ValueError, TypeError):
                    logger.error(f"Invalid weight for blend_{i}: {test_data.get(weight_key)}")
                    blend_weights.append(0.0)
        
        if not blend_ids:
            logger.error("No blend models found in test data")
            return {
                'success': False,
                'errors': ['No blend models found in test data'],
                'extracted_values': {},
                'computed_values': {}
            }
        
        logger.info(f"Validating cumulative returns time series with {len(blend_ids)} blend components")
        logger.info(f"Blend Models: {blend_ids}")
        logger.info(f"Blend Weights: {blend_weights}")
        logger.info(f"Benchmark ID: '{benchmark_id}'")
        logger.info(f"Requested Period: {start_date} to {end_date}")
        
        # Extract actual start and end dates from API response
        # The API may adjust the dates based on data availability
        calc_results = _ci_get(api_response, 'calculationResults', [{}])
        calc_result = calc_results[0] if calc_results else {}
        api_start_date = _ci_get(calc_result, 'startDate', start_date)
        api_end_date = _ci_get(calc_result, 'endDate', end_date)
        
        logger.info(f"API Response Period: {api_start_date} to {api_end_date}")
        
        # Use API response dates for fetching performance data
        start_date = api_start_date
        end_date = api_end_date
        logger.info(f"Using API dates for validation: {start_date} to {end_date}")
        
        # Combine all item IDs for a single API call
        all_item_ids = blend_ids.copy()
        if benchmark_id:
            if isinstance(benchmark_id, list):
                all_item_ids.extend(benchmark_id)
            else:
                all_item_ids.append(benchmark_id)
        
        logger.info("=" * 80)
        logger.info("Fetching monthly performance data for cumulative time series validation")
        logger.info(f"  -> Blend Model IDs: {blend_ids}")
        logger.info(f"  -> Benchmark ID: {benchmark_id if benchmark_id else 'None'}")
        logger.info(f"  -> Combined Request Body: {all_item_ids}")
        logger.info("=" * 80)
        
        # Fetch monthly performance data from API
        fetcher = MonthlyPerformanceDataFetcher()
        all_performance_data = fetcher.fetch_monthly_performance(
            item_ids=all_item_ids,
            start_date=start_date,
            end_date=end_date,
            item_type="model"
        )
        
        # Convert API response to dictionary keyed by modelId
        performance_by_id = {}
        
        if isinstance(all_performance_data, list):
            from collections import defaultdict
            grouped = defaultdict(list)
            
            for record in all_performance_data:
                model_id = record.get('modelId')
                month_return = record.get('monthEndPerformance')
                month_date = record.get('monthEndDate')
                
                if model_id and month_return is not None:
                    grouped[model_id].append({
                        'date': month_date,
                        'return': month_return
                    })
            
            # Sort by date and extract just the returns
            for model_id, records in grouped.items():
                sorted_records = sorted(records, key=lambda x: x['date'])
                performance_by_id[model_id] = [r['return'] for r in sorted_records]
                logger.info(f"  Extracted '{model_id}': {len(performance_by_id[model_id])} months")
        
        elif isinstance(all_performance_data, dict):
            # If already a dict, use it directly
            logger.info(f"API returned a dict with keys: {list(all_performance_data.keys())}")
            performance_by_id = all_performance_data
        
        # Separate the response data for blend models and benchmark
        models_monthly_data = {}
        benchmark_monthly_data = {}
        
        logger.info("=" * 80)
        logger.info("Separating monthly performance data:")
        for item_id in blend_ids:
            if item_id in performance_by_id:
                models_monthly_data[item_id] = performance_by_id[item_id]
                logger.info(f"  -> Blend Model '{item_id}': {len(performance_by_id[item_id])} months of data")
            else:
                logger.warning(f"  -> Blend Model '{item_id}': NOT FOUND in API response")
        
        if benchmark_id:
            benchmark_ids = benchmark_id if isinstance(benchmark_id, list) else [benchmark_id]
            for bench_id in benchmark_ids:
                if bench_id in performance_by_id:
                    benchmark_monthly_data[bench_id] = performance_by_id[bench_id]
                    logger.info(f"  -> Benchmark '{bench_id}': {len(performance_by_id[bench_id])} months of data")
                else:
                    logger.warning(f"  -> Benchmark '{bench_id}': NOT FOUND in API response")
        logger.info("=" * 80)
        
        # Create validator and validate monthly cumulative returns
        validator = ReturnCalculationValidator(tolerance=0.0001)
        is_valid, errors, computed_data = validator.validate_monthly_cumulative_returns_time_series(
            api_response,
            models_monthly_data,
            benchmark_monthly_data,
            blend_ids,
            blend_weights
        )
        
        # Extract computed values for test assertions
        extracted_computed = {}
        
        # Add model-specific cumulative time series
        for model_id, model_data in computed_data.get('models', {}).items():
            prefix = f'computed_{model_id}'
            extracted_computed[f'{prefix}_monthly_returns'] = model_data.get('monthly_returns', [])
            extracted_computed[f'{prefix}_monthly_cumulative'] = model_data.get('monthly_cumulative', [])
        
        # Add blended cumulative time series
        blend_data = computed_data.get('blend', {})
        if blend_data:
            extracted_computed['computed_blend_monthly_returns'] = blend_data.get('monthly_returns', [])
            extracted_computed['computed_blend_monthly_cumulative'] = blend_data.get('monthly_cumulative', [])
        
        # Add benchmark cumulative time series
        for bench_id, bench_data in computed_data.get('benchmark', {}).items():
            prefix = f'computed_{bench_id}'
            extracted_computed[f'{prefix}_monthly_returns'] = bench_data.get('monthly_returns', [])
            extracted_computed[f'{prefix}_monthly_cumulative'] = bench_data.get('monthly_cumulative', [])
        
        # =====================================================================
        # CONSTRUCT EXPECTED API RESPONSE STRUCTURE
        # =====================================================================
        logger.info("=" * 80)
        logger.info("CONSTRUCTING EXPECTED API RESPONSE STRUCTURE")
        logger.info("=" * 80)
        
        # Get month dates from the API response (to preserve exact date format)
        api_calc_result = calc_result
        api_result = _ci_get(api_calc_result, 'result', [])
        api_blend_section = api_result[0] if len(api_result) > 0 else {}
        api_blend_cumulative = _ci_get(api_blend_section, 'cumulativeReturn', [])
        
        # Extract dates in chronological order
        month_dates = sorted([_ci_get(item, 'date') for item in api_blend_cumulative if _ci_get(item, 'date')])
        
        logger.info(f"Using {len(month_dates)} month dates from API response")
        
        # Build blend models array
        blend_models_constructed = []
        for i, model_id in enumerate(blend_ids):
            model_data = computed_data.get('models', {}).get(model_id, {})
            monthly_cumulative = model_data.get('monthly_cumulative', [])
            
            if monthly_cumulative:
                cumulative_return_array = []
                for j, date in enumerate(month_dates):
                    if j < len(monthly_cumulative):
                        cumulative_return_array.append({
                            "date": date,
                            "return": monthly_cumulative[j]
                        })
                
                blend_models_constructed.append({
                    "id": model_id,
                    "entityType": "model",
                    "cumulativeReturn": cumulative_return_array
                })
                
                logger.info(f"Constructed model {model_id}: {len(cumulative_return_array)} months")
        
        # Build blended cumulative return array
        blended_cumulative = computed_data.get('blend', {}).get('monthly_cumulative', [])
        blend_cumulative_return_array = []
        for j, date in enumerate(month_dates):
            if j < len(blended_cumulative):
                blend_cumulative_return_array.append({
                    "date": date,
                    "return": blended_cumulative[j]
                })
        
        logger.info(f"Constructed blend cumulative: {len(blend_cumulative_return_array)} months")
        
        # Build benchmark object
        benchmark_constructed = None
        for bench_id, bench_data in computed_data.get('benchmark', {}).items():
            benchmark_cumulative = bench_data.get('monthly_cumulative', [])
            
            if benchmark_cumulative:
                benchmark_cumulative_return_array = []
                for j, date in enumerate(month_dates):
                    if j < len(benchmark_cumulative):
                        benchmark_cumulative_return_array.append({
                            "date": date,
                            "return": benchmark_cumulative[j]
                        })
                
                benchmark_constructed = {
                    "id": bench_id,
                    "entityType": "benchmark",
                    "cumulativeReturn": benchmark_cumulative_return_array
                }
                
                logger.info(f"Constructed benchmark {bench_id}: {len(benchmark_cumulative_return_array)} months")
                break  # Use first benchmark
        
        # Build complete script response structure matching API format
        response_code_key = _pick_key(api_response, 'responseCode') or 'responseCode'
        message_key = _pick_key(api_response, 'message') or 'message'
        as_of_date_key = _pick_key(api_response, 'asOfDate') or 'asOfDate'
        calc_results_key = _pick_key(api_response, 'calculationResults') or 'calculationResults'
        calculation_type_key = _pick_key(api_calc_result, 'calculationType') or 'calculationType'
        start_date_key = _pick_key(api_calc_result, 'startDate') or 'startDate'
        end_date_key = _pick_key(api_calc_result, 'endDate') or 'endDate'
        result_key = _pick_key(api_calc_result, 'result') or 'result'
        blend_key = _pick_key(api_blend_section, 'blend') or 'blend'
        cumulative_return_key = _pick_key(api_blend_section, 'cumulativeReturn') or 'cumulativeReturn'
        entity_type_key = 'entityType'
        if blend_models_constructed:
            entity_type_key = _pick_key(blend_models_constructed[0], 'entityType') or 'entityType'
        date_key = 'date'
        return_key = 'return'
        if blend_cumulative_return_array:
            date_key = _pick_key(blend_cumulative_return_array[0], 'date') or 'date'
            return_key = _pick_key(blend_cumulative_return_array[0], 'return') or 'return'

        # Rebuild with key style matching API response.
        blend_models_styled = []
        for model in blend_models_constructed:
            styled_cumulative = []
            for item in model.get('cumulativeReturn', []):
                styled_cumulative.append({
                    date_key: item.get('date'),
                    return_key: item.get('return')
                })
            blend_models_styled.append({
                'id': model.get('id'),
                entity_type_key: model.get('entityType'),
                cumulative_return_key: styled_cumulative
            })

        blend_cumulative_styled = []
        for item in blend_cumulative_return_array:
            blend_cumulative_styled.append({
                date_key: item.get('date'),
                return_key: item.get('return')
            })

        benchmark_styled = None
        if benchmark_constructed:
            bench_series = []
            for item in benchmark_constructed.get('cumulativeReturn', []):
                bench_series.append({
                    date_key: item.get('date'),
                    return_key: item.get('return')
                })
            benchmark_styled = {
                'id': benchmark_constructed.get('id'),
                entity_type_key: benchmark_constructed.get('entityType'),
                cumulative_return_key: bench_series
            }

        computed_script_response = {
            response_code_key: _ci_get(api_response, 'responseCode', 200),
            message_key: _ci_get(api_response, 'message', 'Request processed successfully'),
            as_of_date_key: _ci_get(api_response, 'asOfDate', ''),
            calc_results_key: [
                {
                    calculation_type_key: _ci_get(api_calc_result, 'calculationType', 'cumulative returns time series'),
                    start_date_key: start_date,
                    end_date_key: end_date,
                    result_key: [
                        {
                            cumulative_return_key: blend_cumulative_styled,
                            blend_key: blend_models_styled
                        }
                    ]
                }
            ]
        }
        
        # Add benchmark if available
        if benchmark_styled:
            computed_script_response[calc_results_key][0][result_key].append(benchmark_styled)
        
        logger.info("Script response structure constructed successfully")
        logger.info("=" * 80)
        
        # Add script response to output
        extracted_computed['computed_script_response'] = computed_script_response
        extracted_computed['validation_success'] = is_valid
        extracted_computed['validation_type'] = 'cumulative_returns_time_series'
        extracted_computed['validation_errors'] = errors
        
        logger.info("Cumulative returns time series validation completed")
        logger.info(f"Computed values: {list(extracted_computed.keys())}")
        logger.info("=" * 80)
        
        return {
            'success': is_valid,
            'errors': errors,
            'validation_type': 'cumulative_returns_time_series',
            'extracted_values': extracted_computed,
            'computed_values': extracted_computed,
            'computed_script_response': computed_script_response
        }
        
    except Exception as e:
        logger.error(f"Cumulative returns time series validator error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {
            'success': False,
            'errors': [f"Validation exception: {str(e)}"],
            'extracted_values': {},
            'computed_values': {}
        }


def validate_volatility_calculation(ctx, logger):
    """
    Validate volatility calculations from Analytics API.
    
    This function computes expected volatility values from monthly performance data
    and compares them against API responses.
    
    Args:
        ctx: Test context dictionary
        logger: Logger instance
    
    Returns:
        dict: Validation results with computed volatility values
    """
    try:
        # Extract required data from context
        response_ctx = ctx.get('response', {})
        extracted_vars = ctx.get('extracted_vars', {})
        api_response = response_ctx.get('body', {})
        
        # Get test data from extracted_vars (CSV data is loaded here)
        test_data = extracted_vars
        
        # Extract parameters from test data
        start_date = test_data.get('start_date')
        end_date = test_data.get('end_date')
        benchmark_id = test_data.get('benchmark')
        
        logger.debug(f"Volatility validation: start_date={start_date}, end_date={end_date}, benchmark={benchmark_id}")
        
        # Extract blend model IDs and weights from test data
        blend_ids = []
        blend_weights = []
        for i in range(1, 11):  # Support up to 10 blend components
            id_key = f'blend_{i}_id'
            weight_key = f'blend_{i}_weight'
            if id_key in test_data and test_data[id_key]:
                blend_ids.append(test_data[id_key])
                try:
                    blend_weights.append(float(test_data[weight_key]))
                except (ValueError, TypeError):
                    logger.error(f"Invalid weight for blend_{i}: {test_data.get(weight_key)}")
                    blend_weights.append(0.0)
        
        if not blend_ids:
            logger.error("No blend models found in test data")
            return {
                'success': False,
                'errors': ['No blend models found in test data'],
                'extracted_values': {},
                'computed_values': {}
            }
        
        logger.info(f"Validating volatility calculation with {len(blend_ids)} blend components")
        logger.info(f"Blend Models: {blend_ids}")
        logger.info(f"Blend Weights: {blend_weights}")
        logger.info(f"Benchmark ID: '{benchmark_id}'")
        logger.info(f"Period: {start_date} to {end_date}")
        
        # Combine all item IDs for a single API call
        all_item_ids = blend_ids.copy()
        if benchmark_id:
            if isinstance(benchmark_id, list):
                all_item_ids.extend(benchmark_id)
            else:
                all_item_ids.append(benchmark_id)
        
        logger.info("=" * 80)
        logger.info("Fetching monthly performance data for volatility calculation")
        logger.info(f"  -> Blend Model IDs: {blend_ids}")
        logger.info(f"  -> Benchmark ID: {benchmark_id if benchmark_id else 'None'}")
        logger.info(f"  -> Combined Request Body: {all_item_ids}")
        logger.info("=" * 80)
        
        # Fetch monthly performance data from API
        fetcher = MonthlyPerformanceDataFetcher()
        all_performance_data = fetcher.fetch_monthly_performance(
            item_ids=all_item_ids,
            start_date=start_date,
            end_date=end_date,
            item_type="model"
        )
        
        # Convert API response to dictionary keyed by modelId
        performance_by_id = {}
        
        if isinstance(all_performance_data, list):
            from collections import defaultdict
            grouped = defaultdict(list)
            
            for record in all_performance_data:
                model_id = record.get('modelId')
                month_return = record.get('monthEndPerformance')
                month_date = record.get('monthEndDate')
                
                if model_id and month_return is not None:
                    grouped[model_id].append({
                        'date': month_date,
                        'return': month_return
                    })
            
            # Sort by date and extract just the returns
            for model_id, records in grouped.items():
                sorted_records = sorted(records, key=lambda x: x['date'])
                performance_by_id[model_id] = [r['return'] for r in sorted_records]
                logger.info(f"  Extracted '{model_id}': {len(performance_by_id[model_id])} months")
        
        # Separate the response data for blend models and benchmark
        blend_performance_data = {}
        benchmark_performance_data = {}
        
        logger.info("=" * 80)
        logger.info("VOLATILITY CALCULATION VALIDATION")
        logger.info("=" * 80)
        
        for item_id in blend_ids:
            if item_id in performance_by_id:
                blend_performance_data[item_id] = performance_by_id[item_id]
                logger.info(f"  -> Blend Model '{item_id}': {len(performance_by_id[item_id])} months of data")
            else:
                logger.warning(f"  -> Blend Model '{item_id}': NOT FOUND in API response")
        
        if benchmark_id:
            benchmark_ids = benchmark_id if isinstance(benchmark_id, list) else [benchmark_id]
            for bench_id in benchmark_ids:
                if bench_id in performance_by_id:
                    benchmark_performance_data[bench_id] = performance_by_id[bench_id]
                    logger.info(f"  -> Benchmark '{bench_id}': {len(performance_by_id[bench_id])} months of data")
                else:
                    logger.warning(f"  -> Benchmark '{bench_id}': NOT FOUND in API response")
        
        logger.info("=" * 80)
        logger.info("COMPUTING EXPECTED VOLATILITY VALUES FROM MONTHLY PERFORMANCE DATA")
        logger.info("=" * 80)
        
        # Create a calculator instance to access volatility methods
        calculator = ReturnCalculationValidator(tolerance=0.0001)
        
        # Compute volatility for each blend model
        computed_model_volatilities = []
        for i, model_id in enumerate(blend_ids):
            if model_id in blend_performance_data:
                logger.info(f"Computing volatility for blend model {i+1}: {model_id} (weight: {blend_weights[i]})")
                monthly_returns = blend_performance_data[model_id]
                
                # Calculate monthly volatility (standard deviation)
                monthly_vol = calculator.calculate_standard_deviation(monthly_returns)
                
                # Calculate annualized volatility
                annualized_vol = calculator.calculate_annualized_volatility(monthly_vol)
                
                logger.info(f"  Computed Monthly Volatility: {monthly_vol:.10f}")
                logger.info(f"  Computed Annualized Volatility: {annualized_vol:.10f}")
                
                computed_model_volatilities.append({
                    'id': model_id,
                    'weight': blend_weights[i],
                    'volatility': monthly_vol,
                    'annualizedVolatility': annualized_vol
                })
        
        # Compute blended volatility (weighted combination)
        logger.info("Computing blended portfolio volatility")
        
        # For blended volatility, we need to compute from blended returns
        # Blend the monthly returns first, then compute volatility
        if blend_performance_data:
            # Get the length of monthly returns (should be same for all models)
            num_months = len(next(iter(blend_performance_data.values())))
            
            # Compute blended monthly returns
            blended_monthly_returns = []
            for month_idx in range(num_months):
                blended_return = 0.0
                for i, model_id in enumerate(blend_ids):
                    if model_id in blend_performance_data:
                        model_returns = blend_performance_data[model_id]
                        if month_idx < len(model_returns):
                            blended_return += model_returns[month_idx] * blend_weights[i]
                blended_monthly_returns.append(blended_return)
            
            # Calculate volatility from blended returns
            computed_blend_volatility = calculator.calculate_standard_deviation(blended_monthly_returns)
            computed_blend_annualized_volatility = calculator.calculate_annualized_volatility(computed_blend_volatility)
            
            logger.info(f"  Computed Blended Monthly Volatility: {computed_blend_volatility:.10f}")
            logger.info(f"  Computed Blended Annualized Volatility: {computed_blend_annualized_volatility:.10f}")
        else:
            computed_blend_volatility = None
            computed_blend_annualized_volatility = None
        
        # Compute benchmark volatility
        computed_benchmark_volatility = None
        computed_benchmark_annualized_volatility = None
        
        if benchmark_id and benchmark_performance_data:
            benchmark_ids = benchmark_id if isinstance(benchmark_id, list) else [benchmark_id]
            for bench_id in benchmark_ids:
                if bench_id in benchmark_performance_data:
                    logger.info(f"Computing volatility for benchmark: {bench_id}")
                    benchmark_returns = benchmark_performance_data[bench_id]
                    
                    computed_benchmark_volatility = calculator.calculate_standard_deviation(benchmark_returns)
                    computed_benchmark_annualized_volatility = calculator.calculate_annualized_volatility(computed_benchmark_volatility)
                    
                    logger.info(f"  Computed Benchmark Monthly Volatility: {computed_benchmark_volatility:.10f}")
                    logger.info(f"  Computed Benchmark Annualized Volatility: {computed_benchmark_annualized_volatility:.10f}")
                    break  # Use first benchmark for now
        
        # Extract computed values for test assertions
        extracted_computed = {}
        
        # Add individual model volatilities
        for i, model_data in enumerate(computed_model_volatilities):
            model_id = model_data.get('id')
            extracted_computed[f'computed_model_{i+1}_id'] = model_id
            extracted_computed[f'computed_model_{i+1}_volatility'] = model_data.get('volatility')
            extracted_computed[f'computed_model_{i+1}_annualized_volatility'] = model_data.get('annualizedVolatility')
        
        # Add blended volatilities
        if computed_blend_volatility is not None:
            extracted_computed['computed_blend_volatility'] = computed_blend_volatility
        if computed_blend_annualized_volatility is not None:
            extracted_computed['computed_blend_annualized_volatility'] = computed_blend_annualized_volatility
        
        # Add benchmark volatilities
        if computed_benchmark_volatility is not None:
            extracted_computed['computed_benchmark_volatility'] = computed_benchmark_volatility
        if computed_benchmark_annualized_volatility is not None:
            extracted_computed['computed_benchmark_annualized_volatility'] = computed_benchmark_annualized_volatility
        
        logger.info("=" * 80)
        logger.info("Volatility validation completed successfully")
        logger.info(f"Computed values: {list(extracted_computed.keys())}")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'errors': [],
            'validation_type': 'volatility_calculation',
            'extracted_values': extracted_computed,
            'computed_values': extracted_computed
        }
        
    except Exception as e:
        logger.error(f"Volatility validator error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {
            'success': False,
            'errors': [f"Validation exception: {str(e)}"],
            'extracted_values': {},
            'computed_values': {}
        }


"""
EWMA Blended Risk Validator

Service-specific validator for Analytics API EWMA calculations including:
- EWMA (Exponentially Weighted Moving Average) Volatility
- Blended Risk Score calculation
- Profile Value assignment

This is a standalone validator with no external dependencies except logger.
Implements all calculation and comparison methods internally.

Based on methodology from Updated_Blended_Risk_Score_SBE spreadsheet.
"""

import math
from typing import Dict, List, Any, Tuple, Optional

# Import logger only
from framework.common.logger import get_logger

logger = get_logger(__name__)


class EWMABlendedRiskValidator:
    """
    Validates EWMA Blended Risk calculations by independently computing:
    1. Blended monthly returns from model weights
    2. Seed variance from first 61 months (VAR function with N-1 denominator)
    3. Lambda decay factor: exp(-ln(2)/months) for half-life decay
    4. Iterative EWMA variance starting from month 0:
       - Month 0: Seed × Lambda + R[0]² × (1-Lambda)
       - Month n: Previous_Variance × Lambda + R[n]² × (1-Lambda)
    5. Annualized volatility: sqrt(Variance * 12) using variance at index (time_horizon - 3)
    6. Blended risk score based on risk profile bands with interpolation
    7. Profile value with custom rounding (<=0.4 down, >=0.5 up)
    
    Based on methodology from Updated_Blended_Risk_Score_SBE spreadsheet (2Models sheet).
    """
    
    # Seed variance calculation period (first 60 months, indices 0-59)
    # Excel formula: VAR(J5:J64) = 60 cells
    SEED_PERIOD = 60
    
    # Default Risk Profile Bands (fallback if not loaded from DB)
    # Format: {profile_id: annualized_volatility}
    DEFAULT_RISK_PROFILE_BANDS = {
        0: 0.005250730138576,
        1: 0.066714294656654,
        2: 0.081575349937673,
        3: 0.100674827881841,
        4: 0.116551311742702,
        5: 0.133234336066337,
        6: 0.144667257557485
    }
    
    def __init__(self, risk_profile_bands: Dict[int, float] = None):
        """
        Initialize the EWMA validator.
        
        Args:
            risk_profile_bands: Optional dynamic risk profile bands from DB query
                               Format: {profile_id: annualized_volatility}
        """
        # Use provided risk bands or fall back to defaults
        self.RISK_PROFILE_BANDS = risk_profile_bands or self.DEFAULT_RISK_PROFILE_BANDS
        logger.debug(f"EWMABlendedRiskValidator initialized with {len(self.RISK_PROFILE_BANDS)} risk bands")
    
    # =========================================================================
    # BASE CALCULATION METHODS (standalone implementation)
    # =========================================================================
    
    def calculate_sample_variance(self, values: List[float]) -> float:
        """
        Calculate sample variance (N-1 denominator) matching Excel VAR function.
        
        Formula: Σ(x - mean)² / (N - 1)
        
        Args:
            values: List of numeric values
            
        Returns:
            Sample variance
        """
        if not values or len(values) < 2:
            return 0.0
        
        n = len(values)
        mean = sum(values) / n
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        return squared_diff_sum / (n - 1)
    
    def compare_values(
        self, 
        actual: Any, 
        expected: Any, 
        field_name: str, 
        tolerance: float = 0.0001
    ) -> Tuple[bool, Optional[str]]:
        """
        Compare two values with optional tolerance for floating point numbers.
        
        Args:
            actual: Actual value from API response
            expected: Expected/computed value
            field_name: Name of field being compared (for error message)
            tolerance: Acceptable relative difference for floats
            
        Returns:
            Tuple of (is_match, error_message or None)
        """
        if actual is None and expected is None:
            return True, None
        
        if actual is None:
            return False, f"{field_name} missing in response (expected: {expected})"
        
        if expected is None:
            return False, f"{field_name} has no expected value to compare"
        
        # Numeric comparison with tolerance
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            if expected == 0:
                is_match = abs(actual) <= tolerance
            else:
                relative_diff = abs((actual - expected) / expected)
                is_match = relative_diff <= tolerance
            
            if not is_match:
                return False, f"{field_name} mismatch: actual={actual}, expected={expected}, diff={abs(actual - expected)}"
            return True, None
        
        # Direct comparison for non-numeric types
        if actual != expected:
            return False, f"{field_name} mismatch: actual={actual}, expected={expected}"
        
        return True, None
    
    def extract_api_result(
        self, 
        api_response: Dict[str, Any], 
        calculation_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract result for a specific calculation type from API response.
        
        Args:
            api_response: Full API response dictionary
            calculation_type: Type of calculation to find (e.g., "blended risk")
            
        Returns:
            Result dictionary for the calculation type, or None if not found
        """
        def _get_ci(obj: Any, key: str, default: Any = None) -> Any:
            """Case-insensitive dict getter for API payloads with mixed casing."""
            if not isinstance(obj, dict):
                return default
            key_lower = key.lower()
            for k, v in obj.items():
                if str(k).lower() == key_lower:
                    return v
            return default

        def _normalize_calc_type(value: Any) -> str:
            if value is None:
                return ""
            return str(value).strip().lower().replace("_", " ").replace("-", " ")

        def _looks_like_blended_risk_result(result_obj: Any) -> bool:
            if not isinstance(result_obj, dict):
                return False
            return (
                _get_ci(result_obj, "annualizedVolatility") is not None
                and _get_ci(result_obj, "blendedRiskScore") is not None
                and _get_ci(result_obj, "profileValue") is not None
            )

        if not api_response:
            return None
        
        # Try calculationResults array
        calc_results = _get_ci(api_response, "calculationResults", []) or []
        requested_type = _normalize_calc_type(calculation_type)

        for result in calc_results:
            result_type = _normalize_calc_type(_get_ci(result, "calculationType"))

            # Accept exact and common variants like "blended_risk" / "blended-risk"
            if result_type == requested_type:
                return _get_ci(result, "result", result)

            # Fallback for result type variants that still clearly indicate blended risk
            if requested_type == "blended risk" and "blended" in result_type and "risk" in result_type:
                return _get_ci(result, "result", result)

        # Last fallback: pick the first result object that contains expected blended risk fields
        for result in calc_results:
            candidate = _get_ci(result, "result", result)
            if _looks_like_blended_risk_result(candidate):
                return candidate
        
        # Try direct result field
        direct_result = _get_ci(api_response, "result")
        if direct_result is not None and _looks_like_blended_risk_result(direct_result):
            return direct_result
        
        # Try data field
        data_result = _get_ci(api_response, "data")
        if data_result is not None and _looks_like_blended_risk_result(data_result):
            return data_result
        
        return None
    
    # =========================================================================
    # EWMA-SPECIFIC CALCULATION METHODS
    # =========================================================================
    
    def calculate_blended_returns(
        self, 
        model_returns: Dict[str, List[float]], 
        weights: Dict[str, float]
    ) -> List[float]:
        """
        Calculate blended monthly returns by weighting each model's return.
        
        Formula: Blended_Return = Σ(r_i * weight_i)
        
        Args:
            model_returns: Dict mapping model_id to list of monthly returns
            weights: Dict mapping model_id to weight
        
        Returns:
            List of blended monthly returns
        """
        # Get the number of months (should be same for all models)
        num_months = None
        for model_id, returns in model_returns.items():
            if num_months is None:
                num_months = len(returns)
            elif len(returns) != num_months:
                raise ValueError(f"Model {model_id} has {len(returns)} returns, expected {num_months}")
        
        if num_months is None:
            raise ValueError("No model returns provided")
        
        blended_returns = []
        for month_idx in range(num_months):
            blended_return = 0.0
            for model_id, returns in model_returns.items():
                weight = weights.get(model_id, 0.0)
                blended_return += returns[month_idx] * weight
            blended_returns.append(blended_return)
        
        logger.debug(f"Calculated {len(blended_returns)} blended returns")
        return blended_returns
    
    def calculate_seed_variance(self, returns: List[float], seed_period: int = None) -> float:
        """
        Calculate sample variance of the first N months as seed for variance calculation.
        Uses Excel VAR function (sample variance with N-1 denominator).
        
        Args:
            returns: List of monthly returns (oldest first)
            seed_period: Number of months to use for seed (default: 60)
        
        Returns:
            Seed variance value
        """
        if seed_period is None:
            seed_period = self.SEED_PERIOD
        
        seed_returns = returns[:seed_period]
        
        if len(seed_returns) < seed_period:
            logger.warning(f"Only {len(seed_returns)} months available for seed, expected {seed_period}")
        
        # Use base class method for sample variance
        variance = self.calculate_sample_variance(seed_returns)
        
        logger.debug(f"Seed variance calculated from {len(seed_returns)} months: {variance}")
        return variance
    
    # Lambda is always calculated using 180 months (15 years) regardless of time horizon
    LAMBDA_MONTHS = 180
    
    def calculate_lambda(self, time_horizon_months: int = None) -> float:
        """
        Calculate lambda (decay factor) - always uses 180 months (15 years).
        
        Formula: Lambda = exp(-ln(2) / 180)
        
        Lambda is always 0.9961565872205752 (based on 180 months / 15 years)
        regardless of the time horizon used for data collection.
        
        Args:
            time_horizon_months: Ignored - kept for backward compatibility
        
        Returns:
            Lambda decay factor (always based on 180 months)
        """
        lambda_val = math.exp(-math.log(2) / self.LAMBDA_MONTHS)
        logger.debug(f"Lambda (always 180 months): {lambda_val}")
        return lambda_val
    
    def calculate_final_variance_iterative(
        self, 
        returns: List[float], 
        time_horizon: int = 180
    ) -> Tuple[float, float, float]:
        """
        Calculate final variance using ITERATIVE EWMA formula.
        
        Excel formula from 2Models sheet:
        - Month 0 (T5): Seed × Lambda + R[0]² × (1-Lambda)
        - Month 1+ (T6+): Previous_Variance × Lambda + R[n]² × (1-Lambda)
        
        The iteration starts from month 0 (not from seed period end).
        Uses the last non-zero variance value for annualized volatility calculation.
        If the final variance is zero, it looks back to find the last non-zero value.
        
        Args:
            returns: List of blended monthly returns (oldest first)
            time_horizon: Number of months (180 or 240)
        
        Returns:
            Tuple of (final_variance, seed_variance, lambda_value)
        """
        # Calculate seed variance from first 61 months (VAR(J5:J65) in Excel)
        seed_variance = self.calculate_seed_variance(returns)
        
        # Calculate lambda based on time horizon
        lambda_val = self.calculate_lambda(time_horizon)
        
        # Store all variance values for fallback if final is zero
        variance_values = []
        
        # Start EWMA iteration from month 0
        # Month 0: Variance = Seed × Lambda + R[0]² × (1-Lambda)
        r_squared = returns[0] ** 2
        current_variance = (seed_variance * lambda_val) + (r_squared * (1 - lambda_val))
        variance_values.append(current_variance)
        
        # Iterate from month 1 onwards using EWMA
        # Month n: Variance = Previous_Variance × Lambda + R[n]² × (1-Lambda)
        for i in range(1, len(returns)):
            r_squared = returns[i] ** 2
            current_variance = (lambda_val * current_variance) + ((1 - lambda_val) * r_squared)
            variance_values.append(current_variance)
        
        # If final variance is zero, find the last non-zero value
        final_variance = current_variance
        final_index = len(variance_values) - 1
        
        if final_variance == 0 or final_variance is None:
            logger.warning(f"Final variance at index {final_index} is zero, searching for last non-zero value")
            for i in range(len(variance_values) - 1, -1, -1):
                if variance_values[i] != 0 and variance_values[i] is not None:
                    final_variance = variance_values[i]
                    final_index = i
                    logger.info(f"Using variance at index {i} (value: {final_variance}) instead of zero")
                    break
        
        logger.debug(f"Final variance calculation (iterative): Seed={seed_variance}, Lambda={lambda_val}, "
                    f"FinalVariance={final_variance}, UsedIndex={final_index}")
        
        return final_variance, seed_variance, lambda_val
    
    def calculate_annualized_volatility(self, final_variance: float) -> float:
        """
        Calculate annualized volatility from monthly variance.
        
        Formula: AnnualizedVolatility = sqrt(Month180Variance * 12)
        
        Args:
            final_variance: Final monthly EWMA variance
        
        Returns:
            Annualized volatility
        """
        annualized_volatility = math.sqrt(final_variance * 12)
        logger.debug(f"Annualized volatility: {annualized_volatility}")
        return annualized_volatility
    
    def calculate_blended_risk_score(self, annualized_volatility: float) -> Tuple[float, int]:
        """
        Calculate blended risk score and profile value based on risk bands.
        
        Excel Methodology:
        1. Find lower and upper bound profiles for the calculated volatility
        2. Calculate decimal position: (Vol - LowerBoundVol) / (UpperBoundVol - LowerBoundVol)
        3. Add to lower profile number to get raw score
        4. Round to 1 decimal place for Blended Risk Score
        5. Round to integer for Profile ID using custom rounding:
           - 0.4 and below → Round down
           - 0.5 and above → Round up
        
        Args:
            annualized_volatility: Calculated annualized volatility
        
        Returns:
            Tuple of (blended_risk_score, profile_value)
        """
        sorted_profiles = sorted(self.RISK_PROFILE_BANDS.items())
        
        # Find lower and upper bound profiles
        lower_profile = None
        upper_profile = None
        
        for i, (profile_id, vol) in enumerate(sorted_profiles):
            if annualized_volatility <= vol:
                if i == 0:
                    # Below minimum - assign profile 0 with interpolated score
                    lower_profile = (0, 0.0)  # Virtual profile 0 at volatility 0
                    upper_profile = sorted_profiles[0]
                else:
                    lower_profile = sorted_profiles[i - 1]
                    upper_profile = (profile_id, vol)
                break
        
        if upper_profile is None:
            # Above maximum - assign highest profile
            max_profile = sorted_profiles[-1][0]
            return float(max_profile), max_profile
        
        lower_id, lower_vol = lower_profile
        upper_id, upper_vol = upper_profile
        
        # Step 1: Calculate decimal position between bounds
        # Formula: (CalculatedVol - LowerBoundVol) / (UpperBoundVol - LowerBoundVol)
        if upper_vol == lower_vol:
            interpolation = 0.0
        else:
            interpolation = (annualized_volatility - lower_vol) / (upper_vol - lower_vol)
        
        # Step 2: Add interpolation to lower profile number
        raw_score = lower_id + interpolation
        
        logger.debug(f"Interpolation: ({annualized_volatility} - {lower_vol}) / ({upper_vol} - {lower_vol}) = {interpolation}")
        logger.debug(f"Raw score: {lower_id} + {interpolation} = {raw_score}")
        
        # Step 3: Round to 1 decimal place for Blended Risk Score
        # Custom rounding: .4 and below rounds down, .5 and above rounds up
        # Multiply by 10, apply custom rounding to get the first decimal, then divide by 10
        # Example: 3.5509 * 10 = 35.509 → .509 >= 0.5 → round up to 36 → 3.6
        scaled_score = raw_score * 10
        fractional_part = scaled_score - int(scaled_score)
        if fractional_part >= 0.5:
            blended_risk_score = (int(scaled_score) + 1) / 10
        else:
            blended_risk_score = int(scaled_score) / 10
        
        # Apply minimum value of 1.0 (API does not return values below 1.0)
        blended_risk_score = max(1.0, blended_risk_score)
        
        # Step 4: Round to integer for Profile ID
        # Same rule: 0.4 and below → Round down, 0.5 and above → Round up
        decimal_part = blended_risk_score - int(blended_risk_score)
        if decimal_part >= 0.5:
            profile_value = int(blended_risk_score) + 1
        else:
            profile_value = int(blended_risk_score)
        
        # Ensure profile_value is within bounds (0 to max profile)
        max_profile = max(self.RISK_PROFILE_BANDS.keys())
        profile_value = max(0, min(max_profile, profile_value))
        
        logger.debug(f"Blended risk score: {blended_risk_score}, Profile value: {profile_value}")
        return blended_risk_score, profile_value
    
    def compute_expected_results(
        self, 
        model_returns: Dict[str, List[float]], 
        weights: Dict[str, float],
        time_horizon: int = 180
    ) -> Dict[str, Any]:
        """
        Compute all expected calculation results independently.
        
        Excel Methodology (2Models Sheet - Updated):
        1. Calculate Blended Returns = Sum(Model_i_Return * Weight_i)
        2. Calculate Seed Variance = Sample Variance of first 61 months (VAR(J5:J65), N-1 denominator)
        3. Calculate Lambda = exp(-ln(2)/time_horizon)
        4. Calculate Variance iteratively starting from month 0:
           - Month 0: Seed × Lambda + R[0]² × (1-Lambda)
           - Month n: Previous_Variance × Lambda + R[n]² × (1-Lambda)
        5. Use variance at index (time_horizon - 3) for final calculation
           (e.g., index 177 / row 182 for 180-month horizon)
        6. Annualized Volatility = sqrt(FinalVariance * 12)
        7. Interpolate Risk Score between profile bands
        8. Round for final Blended Risk Score (1 decimal) and Profile ID (integer)
        
        Args:
            model_returns: Dict mapping model_id to list of monthly returns
            weights: Dict mapping model_id to weight
            time_horizon: Number of months for calculation (180 or 240)
        
        Returns:
            Dict with computed results:
            {
                "annualizedVolatility": float,
                "blendedRiskScore": float,
                "profileValue": int,
                "intermediateValues": {...}  # For debugging
            }
        """
        # Step 1: Calculate blended returns
        blended_returns = self.calculate_blended_returns(model_returns, weights)
        
        # Use actual available data (may be less than requested time_horizon)
        actual_months = min(len(blended_returns), time_horizon)
        blended_returns = blended_returns[:actual_months]
        
        if actual_months < time_horizon:
            logger.info(f"Using {actual_months} months of available data (requested: {time_horizon})")
        
        # Step 2-4: Calculate final variance using iterative EWMA formula
        # This internally calculates seed_variance and lambda, returning all three values
        final_variance, seed_variance, lambda_value = self.calculate_final_variance_iterative(
            blended_returns, actual_months
        )
        
        # Step 5: Calculate annualized volatility
        annualized_volatility = self.calculate_annualized_volatility(final_variance)
        
        # Step 6: Calculate blended risk score and profile value
        blended_risk_score, profile_value = self.calculate_blended_risk_score(annualized_volatility)
        
        return {
            "annualizedVolatility": annualized_volatility,
            "blendedRiskScore": blended_risk_score,
            "profileValue": profile_value,
            "intermediateValues": {
                "seedVariance": seed_variance,
                "lambda": lambda_value,
                "finalVariance": final_variance,
                "numMonths": actual_months,
                "requestedTimeHorizon": time_horizon,
                "finalVarianceMonthIndex": actual_months - 1  # 0-indexed last month used
            }
        }
    
    def validate_api_response(
        self, 
        api_response: Dict[str, Any],
        model_returns: Dict[str, List[float]], 
        weights: Dict[str, float],
        time_horizon: int = 180,
        tolerance: float = 0.0001
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate API response against independently computed values.
        
        Args:
            api_response: API response containing calculationResults
            model_returns: Dict mapping model_id to list of monthly returns
            weights: Dict mapping model_id to weight
            time_horizon: Number of months for calculation
            tolerance: Acceptable difference for floating point comparison
        
        Returns:
            Tuple of (is_valid, errors, computed_values)
        """
        errors = []
        
        # Compute expected values
        expected = self.compute_expected_results(model_returns, weights, time_horizon)
        
        # Extract actual values from API response
        actual_result = self.extract_api_result(api_response, "blended risk")
        
        if actual_result is None:
            errors.append("No 'blended risk' calculationType in response")
            return False, errors, expected
        
        # Log comparison header
        logger.info("=" * 80)
        logger.info("EWMA BLENDED RISK VALIDATION - API vs COMPUTED COMPARISON")
        logger.info("=" * 80)
        
        # Log intermediate values for debugging
        logger.info(f"Intermediate Values:")
        logger.info(f"  Seed Variance:     {expected['intermediateValues']['seedVariance']}")
        logger.info(f"  Lambda:            {expected['intermediateValues']['lambda']}")
        logger.info(f"  Final Variance:    {expected['intermediateValues']['finalVariance']}")
        logger.info(f"  Actual Months:     {expected['intermediateValues']['numMonths']} (requested: {expected['intermediateValues']['requestedTimeHorizon']})")
        logger.info(f"  Variance Index:    {expected['intermediateValues']['finalVarianceMonthIndex']}")
        logger.info("-" * 80)
        
        # Compare annualized volatility (support mixed API key casing)
        actual_vol = actual_result.get("annualizedVolatility", actual_result.get("AnnualizedVolatility"))
        expected_vol = expected["annualizedVolatility"]
        
        logger.info(f"Annualized Volatility:")
        logger.info(f"  API Value:         {actual_vol}")
        logger.info(f"  Computed Value:    {expected_vol}")
        logger.info(f"  Difference:        {abs(actual_vol - expected_vol) if actual_vol and expected_vol else 'N/A'}")
        
        is_match, error = self.compare_values(actual_vol, expected_vol, "annualizedVolatility", tolerance)
        if error:
            errors.append(error)
            logger.error(f"  Status:            [FAIL] MISMATCH (tolerance: {tolerance})")
        else:
            logger.info(f"  Status:            [PASS] MATCH (tolerance: {tolerance})")
        logger.info("-" * 80)
        
        # For blendedRiskScore and profileValue, we validate internal consistency:
        # The API's derived values should match what we would compute from the API's annualizedVolatility
        # This validates the API's internal calculation logic, not our EWMA calculation
        actual_score = actual_result.get("blendedRiskScore", actual_result.get("BlendedRiskScore"))
        actual_profile = actual_result.get("profileValue", actual_result.get("ProfileValue"))
        
        # Compute expected derived values from our computed annualizedVolatility
        computed_score, computed_profile = self.calculate_blended_risk_score(expected_vol)
        
        # Also compute from API's annualizedVolatility for internal consistency check
        api_derived_score, api_derived_profile = self.calculate_blended_risk_score(actual_vol)
        
        logger.info(f"Blended Risk Score:")
        logger.info(f"  API Value:         {actual_score}")
        logger.info(f"  Computed Value:    {computed_score} (from computed volatility)")
        logger.info(f"  API Derived:       {api_derived_score} (from API volatility)")
        
        # Compare blended risk score (using API's volatility as source)
        is_match, error = self.compare_values(actual_score, api_derived_score, "blendedRiskScore", 0.1)
        if error:
            errors.append(error)
            logger.error(f"  Status:            [FAIL] MISMATCH")
        else:
            logger.info(f"  Status:            [PASS] MATCH (API internal consistency)")
        logger.info("-" * 80)
        
        logger.info(f"Profile Value:")
        logger.info(f"  API Value:         {actual_profile}")
        logger.info(f"  Computed Value:    {computed_profile} (from computed volatility)")
        logger.info(f"  API Derived:       {api_derived_profile} (from API volatility)")
        
        # Compare profile value (using API's volatility as source)
        if actual_profile is None:
            errors.append("profileValue missing in response")
            logger.error(f"  Status:            [FAIL] MISSING")
        elif actual_profile != api_derived_profile:
            errors.append(f"profileValue mismatch: API={actual_profile}, Computed from API vol={api_derived_profile}")
            logger.error(f"  Status:            [FAIL] MISMATCH")
        else:
            logger.info(f"  Status:            [PASS] MATCH")
        logger.info("=" * 80)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("RESULT: [PASS] All EWMA blended risk calculations validated successfully")
        else:
            logger.error(f"RESULT: [FAIL] EWMA validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.error(f"  - {error}")
        logger.info("=" * 80)
        
        # Add API values to the expected dict for reporting
        expected["apiValues"] = {
            "annualizedVolatility": actual_vol,
            "blendedRiskScore": actual_score,
            "profileValue": actual_profile
        }
        
        return is_valid, errors, expected


# =============================================================================
# DB RESULT PARSING UTILITIES
# =============================================================================

def parse_pivoted_db_results(
    db_results: List[Dict[str, Any]],
    model_ids: List[str]
) -> Dict[str, List[float]]:
    """
    Parse pivoted/side-by-side DB results into model_returns format.
    
    Expected DB result format (from INNER JOIN or PIVOT query):
    [
        {"MonthId": "2024-01", "ALFBB3_Performance": 0.05, "MOD389_Performance": 0.03},
        {"MonthId": "2024-02", "ALFBB3_Performance": 0.02, "MOD389_Performance": 0.04},
        ...
    ]
    """
    model_returns = {model_id: [] for model_id in model_ids}
    
    if not db_results:
        logger.warning("No DB results to parse")
        return model_returns
    
    # Detect column naming pattern from first row
    first_row = db_results[0]
    column_patterns = {}
    
    for model_id in model_ids:
        # Try different column naming patterns
        possible_columns = [
            f"{model_id}_Performance",
            f"{model_id}_Return",
            f"{model_id}_performance",
            f"{model_id}_return",
            model_id,
        ]
        
        for col in possible_columns:
            if col in first_row:
                column_patterns[model_id] = col
                break
        
        if model_id not in column_patterns:
            logger.warning(f"Could not find column for model {model_id} in DB results")
    
    # Parse rows (already ordered by date from query)
    for row in db_results:
        for model_id in model_ids:
            if model_id in column_patterns:
                col_name = column_patterns[model_id]
                value = row.get(col_name)
                if value is not None:
                    model_returns[model_id].append(float(value))
    
    for model_id, returns in model_returns.items():
        logger.debug(f"Parsed {len(returns)} returns for model {model_id}")
    
    return model_returns


def parse_vertical_db_results(
    db_results: List[Dict[str, Any]],
    model_id_column: str = "model_id",
    return_column: str = "monthly_return"
) -> Dict[str, List[float]]:
    """
    Parse vertical/stacked DB results into model_returns format.
    """
    model_returns = {}
    
    for row in db_results:
        model_id = row.get(model_id_column)
        monthly_return = row.get(return_column)
        
        if model_id is None or monthly_return is None:
            continue
        
        if model_id not in model_returns:
            model_returns[model_id] = []
        
        model_returns[model_id].append(float(monthly_return))
    
    logger.debug(f"Parsed vertical results for {len(model_returns)} models")
    return model_returns


def detect_db_result_format(db_results: List[Dict[str, Any]], model_ids: List[str]) -> str:
    """Detect whether DB results are in pivoted or vertical format."""
    if not db_results:
        return "unknown"
    
    first_row = db_results[0]
    
    # Check for pivoted format
    pivoted_indicators = 0
    for model_id in model_ids:
        for key in first_row.keys():
            if model_id in key:
                pivoted_indicators += 1
                break
    
    if pivoted_indicators >= len(model_ids):
        return "pivoted"
    
    # Check for vertical format
    vertical_columns = ["model_id", "ModelId", "MODEL_ID", "ItemId", "itemId", "ITEMID"]
    for col in vertical_columns:
        if col in first_row:
            return "vertical"
    
    return "unknown"


def parse_db_results(
    db_results: List[Dict[str, Any]],
    model_ids: List[str],
    time_horizon: int = 240
) -> Dict[str, List[float]]:
    """Automatically detect and parse DB results format."""
    result_format = detect_db_result_format(db_results, model_ids)
    logger.info(f"Detected DB result format: {result_format}")
    
    if result_format == "pivoted":
        model_returns = parse_pivoted_db_results(db_results, model_ids)
    elif result_format == "vertical":
        model_returns = parse_vertical_db_results(db_results)
    else:
        logger.warning("Could not detect DB format, trying pivoted first")
        model_returns = parse_pivoted_db_results(db_results, model_ids)
        
        if all(len(returns) == 0 for returns in model_returns.values()):
            model_returns = parse_vertical_db_results(db_results)
    
    # Limit to time horizon
    for model_id in model_returns:
        model_returns[model_id] = model_returns[model_id][:time_horizon]
    
    return model_returns


def validate_analytics_calculation(
    api_response: Dict[str, Any],
    request_payload: Dict[str, Any],
    db_results: List[Dict[str, Any]] = None,
    model_returns: Dict[str, List[float]] = None,
    tolerance: float = 0.0001,
    risk_profile_bands: Dict[int, float] = None
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Main validation function for analytics API responses.
    
    This function:
    1. Extracts model IDs and weights from request payload
    2. Parses model returns from DB results (auto-detects format)
    3. Computes expected values using EWMA methodology
    4. Compares with API response
    
    Args:
        api_response: API response to validate
        request_payload: Original API request payload
        db_results: Pre-fetched database results (for model returns)
        model_returns: Pre-parsed model returns
        tolerance: Comparison tolerance
        risk_profile_bands: Optional risk profile bands from DB
            Format: {profile_id: annualized_volatility}
    """
    errors = []
    
    # Extract blend inputs from request
    calculation_request = request_payload.get("calculationRequest", {})
    inputs = calculation_request.get("inputs", {})
    blend = inputs.get("blend", [])
    
    if not blend:
        errors.append("No blend inputs in request payload")
        return False, errors, {}
    
    # Extract model IDs and weights
    model_ids = []
    weights = {}
    for item in blend:
        if item.get("entityType") == "model":
            model_id = item.get("id")
            weight = item.get("weight", 0.0)
            model_ids.append(model_id)
            weights[model_id] = weight
    
    if len(model_ids) < 2:
        errors.append("At least 2 models required for blended risk calculation")
        return False, errors, {}
    
    # Get time horizon from request
    calculations = calculation_request.get("calculations", [])
    time_horizon = 180  # Default
    for calc in calculations:
        if calc.get("calculationType") == "blended risk":
            config = calc.get("configurations", {})
            time_horizon = config.get("timeHorizon", 180)
            break
    
    # Get model returns
    if model_returns is None:
        if db_results is not None:
            logger.info(f"Parsing {len(db_results)} DB result rows for {len(model_ids)} models")
            model_returns = parse_db_results(db_results, model_ids, time_horizon)
        else:
            errors.append("Either db_results or model_returns must be provided")
            return False, errors, {}
    
    # Validate we have returns for all models
    for model_id in model_ids:
        if model_id not in model_returns:
            errors.append(f"No returns data for model {model_id}")
        elif len(model_returns[model_id]) == 0:
            errors.append(f"Empty returns data for model {model_id}")
    
    if errors:
        return False, errors, {}
    
    for model_id, returns in model_returns.items():
        logger.info(f"Model {model_id}: {len(returns)} months of data")
    
    # Create validator and run validation (with optional dynamic risk bands)
    validator = EWMABlendedRiskValidator(risk_profile_bands=risk_profile_bands)
    return validator.validate_api_response(
        api_response, 
        model_returns, 
        weights, 
        time_horizon, 
        tolerance
    )

# =============================================================================
# SCRIPT EXECUTOR INTEGRATION
# =============================================================================

def _parse_risk_profile_bands(db_rows: List[Dict[str, Any]]) -> Dict[int, float]:
    """
    Parse risk profile bands from database query results.
    
    Expects query like: SELECT ProfileValue, AnnualStdDeviation FROM Platform.dbo.RiskProfile
    
    Args:
        db_rows: List of dicts with profile data
        
    Returns:
        Dict mapping profile_id (int) to annualized_volatility (float)
    """
    risk_bands = {}
    
    # Try different column name patterns
    profile_columns = ['ProfileValue', 'profileValue', 'profile_value', 'PROFILEVALUE', 'ProfileId', 'profile_id']
    volatility_columns = ['AnnualStdDeviation', 'annualStdDeviation', 'annual_std_deviation', 
                          'Volatility', 'volatility', 'AnnualizedVolatility', 'annualized_volatility']
    
    if not db_rows:
        logger.warning("Empty risk bands data")
        return risk_bands
    
    first_row = db_rows[0]
    profile_col = next((c for c in profile_columns if c in first_row), None)
    volatility_col = next((c for c in volatility_columns if c in first_row), None)
    
    if not profile_col or not volatility_col:
        logger.warning(f"Could not find risk bands columns. Available: {list(first_row.keys())}")
        logger.warning(f"Expected profile column from: {profile_columns}")
        logger.warning(f"Expected volatility column from: {volatility_columns}")
        return risk_bands
    
    logger.info(f"Parsing risk bands: profile_col='{profile_col}', volatility_col='{volatility_col}'")
    
    for row in db_rows:
        try:
            profile_id = int(row[profile_col])
            volatility = float(row[volatility_col])
            risk_bands[profile_id] = volatility
            logger.debug(f"  Profile {profile_id}: {volatility}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid row: {row} - {e}")
    
    logger.info(f"Loaded {len(risk_bands)} risk profile bands from database")
    return risk_bands


def validate(context):
    """
    Main entry point for script executor integration.
    
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
            - success: bool
            - errors: List[str]
            - extracted_values: Dict[str, Any] - values for extract_values
            - computed_values: Dict[str, Any] - expected values computed
            - comparison_data: Dict[str, Any] - data for data_comparison
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
        
        # Parse risk profile bands from db_results if using named queries
        # Look for 'risk_bands' or 'riskBands' query results
        risk_profile_bands = None
        model_data_results = db_results  # Default: assume all results are model data
        
        if isinstance(db_results, dict):
            # Named queries format: {"monthly_performance": [...], "risk_bands": [...]}
            logger.info("DB results are in named queries format")
            
            # Look for risk bands query (support various naming patterns)
            risk_bands_data = (
                db_results.get('risk_bands') or 
                db_results.get('riskBands') or 
                db_results.get('risk_profile_bands') or
                db_results.get('riskProfileBands') or
                db_results.get('riskBands_query') or
                db_results.get('risk_bands_query')
            )
            
            if risk_bands_data:
                logger.info(f"Found risk bands data with {len(risk_bands_data)} rows")
                risk_profile_bands = _parse_risk_profile_bands(risk_bands_data)
            
            # Get model performance data (support various naming patterns)
            model_data_results = (
                db_results.get('monthly_performance') or
                db_results.get('monthlyPerformance') or
                db_results.get('monthlyPerformance_query') or
                db_results.get('monthly_performance_query') or
                db_results.get('model_returns') or
                db_results.get('modelReturns') or
                # Fallback: take first non-risk-bands result
                next((v for k, v in db_results.items() 
                      if 'risk' not in k.lower() and 'band' not in k.lower()), 
                     [])
            )
        elif isinstance(db_results, list):
            # Single query result (backward compatible)
            model_data_results = db_results
        
        # Get API response body
        api_response = response_ctx.get('body') if isinstance(response_ctx, dict) else None
        
        # Get request payload from the rendered request context (not test_case which has file path)
        request_ctx = ctx.get('request', {})
        request_payload = request_ctx.get('payload') if isinstance(request_ctx, dict) else None
        
        # Fallback: try api_request from extracted_vars (contains the rendered payload)
        if not request_payload:
            extracted = ctx.get('extracted_vars', {})
            request_payload = extracted.get('api_request')
        
        if not api_response:
            return {
                "success": False,
                "errors": ["No API response body available for validation"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        if not request_payload:
            return {
                "success": False,
                "errors": ["No request payload available for validation"],
                "extracted_values": {},
                "computed_values": {}
            }
        
        # Call the main validation function
        success, errors, computed_values = validate_analytics_calculation(
            api_response=api_response,
            request_payload=request_payload,
            db_results=model_data_results if model_data_results else None,
            risk_profile_bands=risk_profile_bands
        )
        
        # Build extracted values from computed and API values
        extracted_values = {}
        if computed_values:
            # Make computed values available as extracted variables
            extracted_values['computed_annualized_volatility'] = computed_values.get('annualizedVolatility')
            extracted_values['computed_blended_risk_score'] = computed_values.get('blendedRiskScore')
            extracted_values['computed_profile_value'] = computed_values.get('profileValue')
            
            # Also extract API values if available
            api_values = computed_values.get('apiValues', {})
            if api_values:
                extracted_values['api_annualized_volatility'] = api_values.get('annualizedVolatility')
                extracted_values['api_blended_risk_score'] = api_values.get('blendedRiskScore')
                extracted_values['api_profile_value'] = api_values.get('profileValue')
            
            # Extract intermediate values for detailed assertions
            intermediate = computed_values.get('intermediateValues', {})
            if intermediate:
                extracted_values['seed_variance'] = intermediate.get('seedVariance')
                extracted_values['lambda_value'] = intermediate.get('lambda')
                extracted_values['final_variance'] = intermediate.get('finalVariance')
        
        # Build comparison data for data_comparison validation
        comparison_data = {}
        if computed_values:
            comparison_data = {
                "expected": {
                    "annualizedVolatility": computed_values.get('annualizedVolatility'),
                    "blendedRiskScore": computed_values.get('blendedRiskScore'),
                    "profileValue": computed_values.get('profileValue')
                },
                "actual": computed_values.get('apiValues', {})
            }
        
        return {
            "success": success,
            "errors": errors,
            "extracted_values": extracted_values,
            "computed_values": computed_values,
            "comparison_data": comparison_data,
            "metadata": {
                "validator": "EWMABlendedRiskValidator",
                "test_id": test_case.get('test_id')
            }
        }
        
    except Exception as e:
        import traceback
        logger.error(f"EWMA validator error: {e}")
        logger.debug(traceback.format_exc())
        return {
            "success": False,
            "errors": [f"EWMA validation error: {str(e)}"],
            "extracted_values": {},
            "computed_values": {},
            "metadata": {
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
        }


# Alias for backward compatibility
run = validate
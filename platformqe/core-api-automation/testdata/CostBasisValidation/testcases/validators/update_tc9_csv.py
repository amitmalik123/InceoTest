"""
Update TC009 CSV with TransferID from create transfer response.
"""

import csv
import os
from pathlib import Path
from typing import Any, Dict

from framework.common.logger import get_logger
from framework.validators.script_executor import ScriptResult

logger = get_logger(__name__)


def _find_key_recursive(data: Any, target_keys) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in target_keys:
                return value
            found = _find_key_recursive(value, target_keys)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_key_recursive(item, target_keys)
            if found is not None:
                return found
    return None


def _resolve_testdata_path(test_data_file: str) -> str:
    if not test_data_file:
        return ""

    norm = test_data_file.replace("\\", os.sep).replace("/", os.sep)

    # Project root = core-api-automation
    root = Path(__file__).resolve().parents[4]

    if os.path.isabs(norm):
        return os.path.normpath(norm)

    if norm.lower().startswith("testdata" + os.sep):
        rel_path = norm
    else:
        rel_path = os.path.join("testdata", norm)

    return os.path.normpath(os.path.join(root, rel_path))


def validate(context) -> Dict[str, Any]:
    """
    Script entry point. Updates TransferID in the TC9 CSV file using
    transferInfoId from the create transfer response.
    """
    response_body = getattr(context.response, "body", None)
    transfer_id = _find_key_recursive(
        response_body,
        {"transferInfoId", "transferInfoID", "transferId", "transferID"},
    )

    if transfer_id in (None, ""):
        return ScriptResult(
            success=False,
            errors=["transferInfoId not found in response body"],
            extracted_values={},
        ).to_dict()

    test_data_file = context.test_case.get("test_data_file")
    csv_path = _resolve_testdata_path(test_data_file)
    if not csv_path or not os.path.exists(csv_path):
        return ScriptResult(
            success=False,
            errors=[f"CSV file not found: {csv_path}"],
            extracted_values={},
        ).to_dict()

    external_id = str(context.extracted_vars.get("ExternalID", "") or "").strip()
    env_value = str(context.extracted_vars.get("environment", "") or "").strip()

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if "TransferID" not in fieldnames:
        fieldnames.append("TransferID")

    if not rows:
        return ScriptResult(
            success=False,
            errors=["CSV file has no rows to update"],
            extracted_values={},
        ).to_dict()

    row_index = None
    if external_id:
        for idx, row in enumerate(rows):
            if row.get("ExternalID") == external_id:
                if not env_value or row.get("environment") == env_value:
                    row_index = idx
                    break

    if row_index is None:
        row_index = 0

    rows[row_index]["TransferID"] = str(transfer_id)

    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Updated TransferID in CSV: {csv_path} -> {transfer_id}")

    return ScriptResult(
        success=True,
        errors=[],
        extracted_values={"TransferID": transfer_id},
    ).to_dict()

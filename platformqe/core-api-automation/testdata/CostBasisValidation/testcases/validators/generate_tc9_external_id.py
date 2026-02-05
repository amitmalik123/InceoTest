"""Generate a new ExternalID for TC009 and update the CSV before create transfer."""

import csv
import os
import random
from pathlib import Path
from typing import Any, Dict

from framework.common.logger import get_logger
from framework.validators.script_executor import ScriptResult

logger = get_logger(__name__)


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


def _generate_external_id(prefix: str = "B", length: int = 9) -> str:
    digits = "".join(random.choice("0123456789") for _ in range(length))
    return f"{prefix}{digits}"


def validate(context) -> Dict[str, Any]:
    test_data_file = context.test_case.get("test_data_file")
    csv_path = _resolve_testdata_path(test_data_file)

    if not csv_path or not os.path.exists(csv_path):
        return ScriptResult(
            success=False,
            errors=[f"CSV file not found: {csv_path}"],
            extracted_values={},
        ).to_dict()

    new_external_id = _generate_external_id("B", 9)

    env_value = str(context.extracted_vars.get("environment", "") or os.environ.get("ENV_NAME", "")).strip()

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        return ScriptResult(
            success=False,
            errors=["CSV file has no rows to update"],
            extracted_values={},
        ).to_dict()

    row_index = None
    for idx, row in enumerate(rows):
        if not env_value or row.get("environment") == env_value:
            row_index = idx
            break

    if row_index is None:
        row_index = 0

    rows[row_index]["ExternalID"] = new_external_id

    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Generated ExternalID {new_external_id} and updated CSV: {csv_path}")

    return ScriptResult(
        success=True,
        errors=[],
        extracted_values={"ExternalID": new_external_id},
    ).to_dict()

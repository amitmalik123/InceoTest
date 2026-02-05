"""Generate a new ExternalID in the TC009 CSV (Postman-style: B999 + 6 random digits)."""

import csv
import os
import random
from pathlib import Path


def _resolve_csv_path() -> str:
    # project root = core-api-automation
    root = Path(__file__).resolve().parents[4]
    return os.path.normpath(
        os.path.join(root, "testdata", "CostBasisValidation", "data_driven", "Data_cost_basis_validation_tc9.csv")
    )


def _generate_external_id() -> str:
    return "B999" + str(random.randint(100000, 999999))


def main() -> None:
    csv_path = _resolve_csv_path()
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    env_name = os.environ.get("ENV_NAME", "")

    required_fields = ["ExternalID", "AccountNumber", "CostBasisExternalID", "environment", "TransferID"]
    if not fieldnames:
        fieldnames = required_fields
    else:
        for field in required_fields:
            if field not in fieldnames:
                fieldnames.append(field)

    if not rows:
        rows = [{
            "ExternalID": "B999000000",
            "AccountNumber": "13477321",
            "CostBasisExternalID": "B888238988",
            "environment": env_name or "T11",
            "TransferID": ""
        }]

    # Update first matching row for env, else first row
    row_index = 0
    if env_name:
        for idx, row in enumerate(rows):
            if row.get("environment") == env_name:
                row_index = idx
                break

    new_external_id = _generate_external_id()
    rows[row_index]["ExternalID"] = new_external_id
    rows[row_index]["AccountNumber"] = rows[row_index].get("AccountNumber") or "13477321"
    rows[row_index]["CostBasisExternalID"] = rows[row_index].get("CostBasisExternalID") or "B888238988"
    rows[row_index]["environment"] = rows[row_index].get("environment") or (env_name or "T11")
    rows[row_index]["TransferID"] = rows[row_index].get("TransferID", "")

    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated ExternalID to {new_external_id} in {csv_path}")


if __name__ == "__main__":
    main()

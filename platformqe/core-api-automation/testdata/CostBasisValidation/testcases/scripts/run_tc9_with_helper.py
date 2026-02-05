"""Run ExternalID helper first, then execute TC009 pytest run."""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=None, help="Environment name (e.g., T11)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[4]
    helper = root / "testdata" / "CostBasisValidation" / "testcases" / "validators" / "generate_externalid_csv.py"
    testcase = root / "testdata" / "CostBasisValidation" / "testcases" / "TestCase_cost_basis_validation_tc9.json"
    test_file = root / "tests" / "test_api_generic.py"

    if not helper.exists():
        print(f"Helper not found: {helper}")
        return 1

    if not testcase.exists():
        print(f"Testcase file not found: {testcase}")
        return 1

    result = subprocess.run([sys.executable, str(helper)], cwd=str(root))
    if result.returncode != 0:
        return result.returncode

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-sv",
        str(test_file.relative_to(root)),
        "--testcase-file",
        str(testcase.relative_to(root)),
    ]
    if args.env:
        cmd.extend(["--env", args.env])

    return subprocess.call(cmd, cwd=str(root))


if __name__ == "__main__":
    raise SystemExit(main())

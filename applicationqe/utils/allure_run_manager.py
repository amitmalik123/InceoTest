"""
Allure Run Manager: Handles timestamped scenario-based run organization and metadata.

Provides utilities for:
- Generating scenario slugs from BDD scenario titles
- Creating and updating run manifests with metadata
- Managing latest run pointers
- Organizing Allure artifacts in timestamp/flow/scenario hierarchy
"""

import json
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class AllureRunManager:
    """Manages timestamped Allure run organization and metadata."""
    
    RUNS_BASE_DIR = Path("reports/runs")
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    DISPLAY_FORMAT = "%Y-%m-%d_%H-%M-%S"
    
    @staticmethod
    def generate_run_timestamp() -> str:
        """Generate a run timestamp in YYYYMMDD_HHMMSS format."""
        return datetime.now().strftime(AllureRunManager.TIMESTAMP_FORMAT)
    
    @staticmethod
    def scenario_title_to_slug(scenario_title: str) -> str:
        """
        Convert BDD scenario title to a filesystem-safe slug.
        
        Example:
            "Complete E2E journal portion transfer" -> "complete_e2e_journal_portion_transfer"
            "Error handling during journal portion transfer" -> "error_handling_during_journal_portion"
        
        Args:
            scenario_title: Original BDD scenario title
            
        Returns:
            Lowercase slug with spaces/special chars replaced by underscores, max 80 chars
        """
        # Convert to lowercase
        slug = scenario_title.lower()
        
        # Replace spaces and hyphens with underscores
        slug = re.sub(r'[\s\-]+', '_', slug)
        
        # Remove special characters, keep only alphanumeric and underscores
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        
        # Remove duplicate underscores
        slug = re.sub(r'_+', '_', slug)
        
        # Remove leading/trailing underscores
        slug = slug.strip('_')
        
        # Limit to 80 characters (leave room for hash suffix if needed)
        slug = slug[:80]
        
        return slug
    
    @staticmethod
    def add_slug_collision_suffix(slug: str, existing_slugs: List[str]) -> str:
        """
        Add a hash suffix to slug if collision detected.
        
        Args:
            slug: The base scenario slug
            existing_slugs: List of already-used slugs in this run
            
        Returns:
            Original slug if no collision, otherwise slug_HASH[:6]
        """
        if slug not in existing_slugs:
            return slug
        
        # Create a short hash suffix to disambiguate
        hash_suffix = hashlib.md5(slug.encode()).hexdigest()[:6]
        return f"{slug}_{hash_suffix}"
    
    @staticmethod
    def get_run_dir(run_timestamp: Optional[str] = None) -> Path:
        """
        Get or create the run root directory.
        
        Args:
            run_timestamp: Optional timestamp override; if None, uses current time
            
        Returns:
            Path to reports/runs/{timestamp}/
        """
        if run_timestamp is None:
            run_timestamp = AllureRunManager.generate_run_timestamp()
        
        run_dir = AllureRunManager.RUNS_BASE_DIR / run_timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        
        return run_dir
    
    @staticmethod
    def get_scenario_dir(run_timestamp: str, flow_name: str, scenario_slug: str) -> Path:
        """
        Get or create the scenario-specific artifact directory.
        
        Path: reports/runs/{timestamp}/{flow}/{scenario}/
        
        Args:
            run_timestamp: Run timestamp (YYYYMMDD_HHMMSS)
            flow_name: Flow name (e.g., 'like2like', 'ira', 'roth')
            scenario_slug: Filesystem-safe scenario slug
            
        Returns:
            Path to reports/runs/{timestamp}/{flow}/{scenario}/
        """
        scenario_dir = AllureRunManager.get_run_dir(run_timestamp) / flow_name / scenario_slug
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        return scenario_dir
    
    @staticmethod
    def create_run_manifest(
        run_timestamp: str,
        flows: Dict[str, List[Dict[str, Any]]],
        environment: str = "test11",
        command: str = "",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        status: str = "in_progress"
    ) -> Dict[str, Any]:
        """
        Create and write a run manifest file.
        
        Manifest structure:
        {
            "timestamp": "20260501_143000",
            "display_timestamp": "2026-05-01_14-30-00",
            "environment": "test11",
            "status": "completed",
            "start_time": "2026-05-01T14:30:00Z",
            "end_time": "2026-05-01T14:45:30Z",
            "command": "python run_journal_flows.py test11",
            "flows": {
                "like2like": [
                    {
                        "scenario_title": "Complete E2E journal portion transfer",
                        "scenario_slug": "complete_e2e_journal_portion_transfer",
                        "tags": ["journal_transfer_smoke", "e2e", "screenshots"],
                        "status": "passed",
                        "duration_ms": 45000,
                        "allure_report_path": "like2like/complete_e2e_journal_portion_transfer/allure-report/index.html"
                    }
                ],
                "ira": [...],
                "roth": [...]
            }
        }
        
        Args:
            run_timestamp: Run timestamp (YYYYMMDD_HHMMSS)
            flows: Dict mapping flow names to list of scenario metadata
            environment: Test environment (test11, test12, prod, silo)
            command: Original command used to run the flow
            start_time: ISO format start time
            end_time: ISO format end time
            status: Run status (in_progress, completed, failed)
            
        Returns:
            Manifest dict written to reports/runs/{timestamp}/run_manifest.json
        """
        run_dir = AllureRunManager.get_run_dir(run_timestamp)
        
        manifest = {
            "timestamp": run_timestamp,
            "display_timestamp": datetime.strptime(run_timestamp, AllureRunManager.TIMESTAMP_FORMAT).strftime(AllureRunManager.DISPLAY_FORMAT),
            "environment": environment,
            "status": status,
            "start_time": start_time or datetime.utcnow().isoformat() + "Z",
            "end_time": end_time or "",
            "command": command,
            "flows": flows
        }
        
        manifest_path = run_dir / "run_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    @staticmethod
    def update_latest_pointer(run_timestamp: str, manifest: Dict[str, Any]) -> None:
        """
        Create or update reports/runs/latest.json pointer to newest run.
        
        Format:
        {
            "timestamp": "20260501_143000",
            "display_timestamp": "2026-05-01_14-30-00",
            "path": "reports/runs/20260501_143000",
            "manifest_path": "reports/runs/20260501_143000/run_manifest.json",
            "flows": ["like2like", "ira", "roth"],
            "total_scenarios": 12,
            "completed_scenarios": 11,
            "passed_scenarios": 10,
            "failed_scenarios": 1
        }
        
        Args:
            run_timestamp: Run timestamp of the latest run
            manifest: The run manifest dict
        """
        runs_base = AllureRunManager.RUNS_BASE_DIR
        runs_base.mkdir(parents=True, exist_ok=True)
        
        # Count scenarios and statuses
        flows = manifest.get("flows", {})
        flow_list = list(flows.keys())
        scenarios = [s for flow_scenarios in flows.values() for s in flow_scenarios]
        completed_count = len([s for s in scenarios if s.get("status") in ["passed", "failed"]])
        passed_count = len([s for s in scenarios if s.get("status") == "passed"])
        failed_count = len([s for s in scenarios if s.get("status") == "failed"])
        
        latest_pointer = {
            "timestamp": run_timestamp,
            "display_timestamp": manifest.get("display_timestamp"),
            "path": f"reports/runs/{run_timestamp}",
            "manifest_path": f"reports/runs/{run_timestamp}/run_manifest.json",
            "flows": flow_list,
            "total_scenarios": len(scenarios),
            "completed_scenarios": completed_count,
            "passed_scenarios": passed_count,
            "failed_scenarios": failed_count
        }
        
        latest_path = runs_base / "latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(latest_pointer, f, indent=2)
    
    @staticmethod
    def load_latest_run() -> Optional[Dict[str, Any]]:
        """Load the latest run pointer from reports/runs/latest.json."""
        latest_path = AllureRunManager.RUNS_BASE_DIR / "latest.json"
        
        if not latest_path.exists():
            return None
        
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def load_run_manifest(run_timestamp: str) -> Optional[Dict[str, Any]]:
        """Load the manifest for a specific run."""
        manifest_path = AllureRunManager.get_run_dir(run_timestamp) / "run_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def list_all_runs() -> List[Dict[str, str]]:
        """
        List all run timestamps in chronological order (newest first).
        
        Returns:
            List of dicts with timestamp, display_timestamp, and path
        """
        if not AllureRunManager.RUNS_BASE_DIR.exists():
            return []
        
        runs = []
        for item in sorted(AllureRunManager.RUNS_BASE_DIR.iterdir(), reverse=True):
            if item.is_dir() and item.name not in [".gitkeep"]:
                try:
                    # Validate timestamp format
                    datetime.strptime(item.name, AllureRunManager.TIMESTAMP_FORMAT)
                    display_ts = datetime.strptime(item.name, AllureRunManager.TIMESTAMP_FORMAT).strftime(AllureRunManager.DISPLAY_FORMAT)
                    runs.append({
                        "timestamp": item.name,
                        "display_timestamp": display_ts,
                        "path": f"reports/runs/{item.name}"
                    })
                except ValueError:
                    # Skip directories that don't match timestamp format
                    pass
        
        return runs


class ScenarioMetadata:
    """Helper for building scenario metadata within a run."""
    
    def __init__(self, scenario_title: str, scenario_slug: str):
        """
        Initialize scenario metadata.
        
        Args:
            scenario_title: Original BDD scenario title
            scenario_slug: Filesystem-safe slug
        """
        self.scenario_title = scenario_title
        self.scenario_slug = scenario_slug
        self.tags: List[str] = []
        self.status: str = "pending"  # pending, passed, failed, skipped
        self.duration_ms: int = 0
        self.allure_report_path: str = ""
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for manifest."""
        return {
            "scenario_title": self.scenario_title,
            "scenario_slug": self.scenario_slug,
            "tags": self.tags,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "allure_report_path": self.allure_report_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_message": self.error_message
        }

#!/usr/bin/env python3
"""
Service Matrix Manager

This script helps manage the services-matrix.yaml configuration and validate the matrix setup.

Usage:
    python manage_matrix.py list                          # List all services
    python manage_matrix.py validate                      # Validate configuration
    python manage_matrix.py enable <service_name>         # Enable a service
    python manage_matrix.py disable <service_name>        # Disable a service
    python manage_matrix.py simulate-pr                   # Simulate PR run
    python manage_matrix.py simulate-push                 # Simulate push run
    python manage_matrix.py simulate-schedule             # Simulate scheduled run
    python manage_matrix.py export-services               # Export services list for pipeline
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml


class ServiceMatrixManager:
    """Manager for services-matrix.yaml configuration"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load the services matrix configuration"""
        if not self.config_path.exists():
            print(f"❌ Error: Configuration file not found: {self.config_path}")
            sys.exit(1)

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_config(self):
        """Save the services matrix configuration"""

        class NoAliasDumper(yaml.SafeDumper):
            """Custom YAML dumper that disables aliases to avoid &id001 and *id001"""

            def ignore_aliases(self, data):
                return True

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, Dumper=NoAliasDumper, default_flow_style=False, sort_keys=False)
        print(f"[OK] Configuration saved to {self.config_path}")

    def list_services(self, filter_enabled: bool | None = None):
        """List all services with their configuration"""
        services = self.config.get("services", {})

        print("\n" + "=" * 80)
        print("📋 SERVICES CONFIGURATION")
        print("=" * 80)

        for service_name, service_config in services.items():
            enabled = service_config.get("enabled", True)

            if filter_enabled is not None and enabled != filter_enabled:
                continue

            status_icon = "✅" if enabled else "❌"
            priority = service_config.get("priority", "N/A")
            display_name = service_config.get("displayName", service_name)
            test_type = service_config.get("testType", "functional")

            print(f"\n{status_icon} {service_name}")
            print(f"   Display Name: {display_name}")
            print(f"   Enabled: {enabled}")
            print(f"   Priority: {priority}")
            print(f"   Test Type: {test_type}")
            print(f"   Run on PR: {service_config.get('runOnPR', False)}")
            print(f"   Run on Push: {service_config.get('runOnPush', True)}")
            print(f"   Run on Schedule: {service_config.get('runOnSchedule', True)}")
            print(f"   Environments: {', '.join(service_config.get('environments', []))}")

            schedules = service_config.get("schedules", [])
            if schedules:
                print("   Schedules:")
                for schedule in schedules:
                    print(f"      - {schedule.get('displayName', 'Unnamed')}: {schedule.get('cron', 'N/A')}")

            email = service_config.get("emailRecipients", {})
            if email:
                print(f"   Email: {email.get('to', 'N/A')}")

        print("\n" + "=" * 80)

    def validate(self) -> bool:
        """Validate the configuration"""
        print("\n" + "=" * 80)
        print("🔍 VALIDATING CONFIGURATION")
        print("=" * 80)

        errors = []
        warnings = []
        services = self.config.get("services", {})

        if not services:
            errors.append("No services defined in configuration")

        required_fields = ["displayName", "enabled", "testType"]
        optional_but_recommended = ["runOnPR", "runOnPush", "runOnSchedule", "priority", "environments"]

        for service_name, service_config in services.items():
            for field in required_fields:
                if field not in service_config:
                    errors.append(f"Service '{service_name}': Missing required field '{field}'")

            for field in optional_but_recommended:
                if field not in service_config:
                    warnings.append(f"Service '{service_name}': Missing recommended field '{field}'")

            valid_test_types = ["functional", "non-functional", "both"]
            test_type = service_config.get("testType", "")
            if test_type and test_type not in valid_test_types:
                errors.append(
                    f"Service '{service_name}': Invalid testType '{test_type}'. Must be one of {valid_test_types}"
                )

            priority = service_config.get("priority")
            if priority is not None and (not isinstance(priority, int) or priority < 1):
                errors.append(f"Service '{service_name}': Priority must be a positive integer")

            schedules = service_config.get("schedules", [])
            for schedule in schedules:
                if "cron" not in schedule:
                    errors.append(f"Service '{service_name}': Schedule missing 'cron' field")
                if "displayName" not in schedule:
                    warnings.append(f"Service '{service_name}': Schedule missing 'displayName' field")

        print("\n📊 Validation Results:")
        print(f"   Total Services: {len(services)}")
        print(f"   Enabled Services: {sum(1 for s in services.values() if s.get('enabled', True))}")
        print(f"   Disabled Services: {sum(1 for s in services.values() if not s.get('enabled', True))}")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")

        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"   - {error}")

        if warnings:
            print("\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")

        if not errors and not warnings:
            print("\n✅ Configuration is valid!")
        elif not errors:
            print("\n✅ Configuration is valid (with warnings)")
        else:
            print("\n❌ Configuration has errors")

        print("=" * 80 + "\n")

        return len(errors) == 0

    def enable_service(self, service_name: str):
        """Enable a service"""
        services = self.config.get("services", {})

        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return

        services[service_name]["enabled"] = True
        self._save_config()
        print(f"[+] Service '{service_name}' enabled")

    def disable_service(self, service_name: str):
        """Disable a service"""
        services = self.config.get("services", {})

        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return

        services[service_name]["enabled"] = False
        self._save_config()
        print(f"[-] Service '{service_name}' disabled")

    def set_flag(self, service_name: str, flag_name: str, value: bool):
        """Set a boolean flag on a service"""
        services = self.config.get("services", {})

        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return

        if flag_name not in services[service_name]:
            print(f"❌ Error: Flag '{flag_name}' not found for service '{service_name}'")
            return

        services[service_name][flag_name] = value
        self._save_config()
        print(f"[+] Set {flag_name} = {value} for service '{service_name}'")

    def set_all_flags(self, service_name: str, enabled: bool, run_on_pr: bool, run_on_push: bool, run_on_schedule: bool):
        """Set all boolean flags for a service"""
        services = self.config.get("services", {})

        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return

        services[service_name]["enabled"] = enabled
        services[service_name]["runOnPR"] = run_on_pr
        services[service_name]["runOnPush"] = run_on_push
        services[service_name]["runOnSchedule"] = run_on_schedule
        self._save_config()
        print(f"[+] Updated all flags for service '{service_name}'")

    def simulate_run(self, run_type: str, env: str = None):
        """Simulate a pipeline run"""
        services = self.config.get("services", {})

        # Filter services based on run type
        filtered_services = {}
        for name, config in services.items():
            if run_type == "pr" and config.get("runOnPR", False):
                filtered_services[name] = config
            elif run_type == "push" and config.get("runOnPush", False):
                filtered_services[name] = config
            elif run_type == "schedule" and config.get("runOnSchedule", False):
                filtered_services[name] = config

        if not filtered_services:
            print(f"No services configured to run on {run_type}")
            return

        # Generate matrix
        matrix = []
        for service_name, config in filtered_services.items():
            for env_name in config.get("environments", []):
                if env and env_name != env:
                    continue
                matrix.append({
                    "service": service_name,
                    "environment": env_name,
                    "testType": config.get("testType", "functional"),
                    "displayName": config.get("displayName", service_name)
                })

        # Display matrix
        print("\n" + "=" * 80)
        print(f"📊 SIMULATED {run_type.upper()} RUN MATRIX")
        print("=" * 80)
        print(f"Total jobs: {len(matrix)}")

        for job in matrix:
            print(f"- {job['displayName']} ({job['service']}) on {job['environment']} [{job['testType']}]")

        print("=" * 80 + "\n")

        # Save matrix to file
        output_file = Path(f"matrix_{run_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(matrix, f, indent=2)

        print(f"[OK] Matrix saved to {output_file}")

    def export_services(self, output_file: str):
        """Export services list to file"""
        services = self.config.get("services", {})
        service_list = list(services.keys())

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(service_list, f, indent=2)

        print(f"[OK] Services list exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Service Matrix Manager")
    parser.add_argument("command", choices=[
        "list", "validate", "enable", "disable", "set-flag", "set-all-flags", "simulate-pr",
        "simulate-push", "simulate-schedule", "export-services"
    ])
    parser.add_argument("service_name", nargs="?")
    parser.add_argument("flag_name", nargs="?")
    parser.add_argument("flag_value", nargs="?")
    parser.add_argument("--env", help="Environment name")
    parser.add_argument("--output", help="Output file for export-services")

    args = parser.parse_args()

    # Determine config file path
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir.parents[2] / "config" / "services-matrix.yaml"

    manager = ServiceMatrixManager(config_path)

    if args.command == "list":
        manager.list_services()
    elif args.command == "validate":
        manager.validate()
    elif args.command == "enable":
        manager.enable_service(args.service_name)
    elif args.command == "disable":
        manager.disable_service(args.service_name)
    elif args.command == "set-flag":
        manager.set_flag(args.service_name, args.flag_name, args.flag_value.lower() == "true")
    elif args.command == "set-all-flags":
        # Use default values for flags not provided
        enabled = args.flag_value.lower() == "true" if args.flag_value else True
        manager.set_all_flags(args.service_name, enabled, True, True, True)
    elif args.command == "simulate-pr":
        manager.simulate_run("pr", args.env)
    elif args.command == "simulate-push":
        manager.simulate_run("push", args.env)
    elif args.command == "simulate-schedule":
        manager.simulate_run("schedule", args.env)
    elif args.command == "export-services":
        if not args.output:
            print("Please specify --output for export-services")
            return 1
        manager.export_services(args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ServiceMatrixManager:
    """Manager for services-matrix.yaml configuration"""
    
    def __init__(self, config_path: str = "config/services-matrix.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the services matrix configuration"""
        if not self.config_path.exists():
            print(f"❌ Error: Configuration file not found: {self.config_path}")
            sys.exit(1)
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _save_config(self):
        """Save the services matrix configuration"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        print(f"[OK] Configuration saved to {self.config_path}")
    
    def list_services(self, filter_enabled: bool = None):
        """List all services with their configuration"""
        services = self.config.get('services', {})
        
        print("\n" + "="*80)
        print("📋 SERVICES CONFIGURATION")
        print("="*80)
        
        for service_name, service_config in services.items():
            enabled = service_config.get('enabled', True)
            
            # Apply filter if specified
            if filter_enabled is not None and enabled != filter_enabled:
                continue
            
            status_icon = "✅" if enabled else "❌"
            priority = service_config.get('priority', 'N/A')
            display_name = service_config.get('displayName', service_name)
            test_type = service_config.get('testType', 'functional')
            
            print(f"\n{status_icon} {service_name}")
            print(f"   Display Name: {display_name}")
            print(f"   Enabled: {enabled}")
            print(f"   Priority: {priority}")
            print(f"   Test Type: {test_type}")
            print(f"   Run on PR: {service_config.get('runOnPR', False)}")
            print(f"   Run on Push: {service_config.get('runOnPush', True)}")
            print(f"   Run on Schedule: {service_config.get('runOnSchedule', True)}")
            print(f"   Environments: {', '.join(service_config.get('environments', []))}")
            
            # Schedules
            schedules = service_config.get('schedules', [])
            if schedules:
                print(f"   Schedules:")
                for schedule in schedules:
                    print(f"      - {schedule.get('displayName', 'Unnamed')}: {schedule.get('cron', 'N/A')}")
            
            # Email
            email = service_config.get('emailRecipients', {})
            if email:
                print(f"   Email: {email.get('to', 'N/A')}")
        
        print("\n" + "="*80)
    
    def validate(self) -> bool:
        """Validate the configuration"""
        print("\n" + "="*80)
        print("🔍 VALIDATING CONFIGURATION")
        print("="*80)
        
        errors = []
        warnings = []
        services = self.config.get('services', {})
        
        if not services:
            errors.append("No services defined in configuration")
        
        required_fields = ['displayName', 'enabled', 'testType']
        optional_but_recommended = ['runOnPR', 'runOnPush', 'runOnSchedule', 'priority', 'environments']
        
        for service_name, service_config in services.items():
            # Check required fields
            for field in required_fields:
                if field not in service_config:
                    errors.append(f"Service '{service_name}': Missing required field '{field}'")
            
            # Check optional but recommended fields
            for field in optional_but_recommended:
                if field not in service_config:
                    warnings.append(f"Service '{service_name}': Missing recommended field '{field}'")
            
            # Validate test type
            valid_test_types = ['functional', 'non-functional', 'both']
            test_type = service_config.get('testType', '')
            if test_type and test_type not in valid_test_types:
                errors.append(f"Service '{service_name}': Invalid testType '{test_type}'. Must be one of {valid_test_types}")
            
            # Validate priority
            priority = service_config.get('priority')
            if priority is not None and (not isinstance(priority, int) or priority < 1):
                errors.append(f"Service '{service_name}': Priority must be a positive integer")
            
            # Validate cron schedules
            schedules = service_config.get('schedules', [])
            for schedule in schedules:
                if 'cron' not in schedule:
                    errors.append(f"Service '{service_name}': Schedule missing 'cron' field")
                if 'displayName' not in schedule:
                    warnings.append(f"Service '{service_name}': Schedule missing 'displayName' field")
        
        # Print results
        print(f"\n📊 Validation Results:")
        print(f"   Total Services: {len(services)}")
        print(f"   Enabled Services: {sum(1 for s in services.values() if s.get('enabled', True))}")
        print(f"   Disabled Services: {sum(1 for s in services.values() if not s.get('enabled', True))}")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")
        
        if errors:
            print(f"\n❌ ERRORS:")
            for error in errors:
                print(f"   - {error}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")
        
        if not errors and not warnings:
            print(f"\n✅ Configuration is valid!")
        elif not errors:
            print(f"\n✅ Configuration is valid (with warnings)")
        else:
            print(f"\n❌ Configuration has errors")
        
        print("="*80 + "\n")
        
        return len(errors) == 0
    
    def enable_service(self, service_name: str):
        """Enable a service"""
        services = self.config.get('services', {})
        
        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return
        
        services[service_name]['enabled'] = True
        self._save_config()
        print(f"[+] Service '{service_name}' enabled")
    
    def disable_service(self, service_name: str):
        """Disable a service"""
        services = self.config.get('services', {})
        
        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return
        
        services[service_name]['enabled'] = False
        self._save_config()
        print(f"[-] Service '{service_name}' disabled")
    
    def set_flag(self, service_name: str, flag_name: str, value: bool):
        """Set a boolean flag for a service (enabled, runOnPR, runOnPush, runOnSchedule)"""
        services = self.config.get('services', {})
        
        if service_name not in services:
            print(f"❌ Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}")
            return
        
        valid_flags = ['enabled', 'runOnPR', 'runOnPush', 'runOnSchedule']
        if flag_name not in valid_flags:
            print(f"❌ Error: Invalid flag '{flag_name}'")
            print(f"Valid flags: {', '.join(valid_flags)}")
            return
        
        services[service_name][flag_name] = value
        self._save_config()
        
        status_icon = "+" if value else "-"
        print(f"[{status_icon}] Service '{service_name}': {flag_name} = {value}")
    
    def set_all_flags(self, service_name: str, all_value: bool = None,
                     enabled: bool = None, run_on_pr: bool = None, 
                     run_on_push: bool = None, run_on_schedule: bool = None,
                     _skip_save: bool = False):
        """Set multiple flags for a service at once"""
        services = self.config.get('services', {})
        
        # Check if 'all' keyword is used to apply to all services
        if service_name.lower() in ['all', 'all-services']:
            print(f"\n{'='*80}")
            print(f"Setting flags for ALL services")
            print(f"{'='*80}\n")
            
            for svc_name in services.keys():
                self.set_all_flags(svc_name, all_value, enabled, run_on_pr, run_on_push, run_on_schedule, _skip_save=True)
            
            # Save once after all updates
            self._save_config()
            print(f"\n[OK] All services updated successfully!")
            return
        
        if service_name not in services:
            print(f"Error: Service '{service_name}' not found")
            print(f"Available services: {', '.join(services.keys())}, all")
            return
        
        updated_flags = []
        
        # If all_value is specified, set all flags to that value
        if all_value is not None:
            services[service_name]['enabled'] = all_value
            services[service_name]['runOnPR'] = all_value
            services[service_name]['runOnPush'] = all_value
            services[service_name]['runOnSchedule'] = all_value
            updated_flags = [
                f"enabled={all_value}",
                f"runOnPR={all_value}",
                f"runOnPush={all_value}",
                f"runOnSchedule={all_value}"
            ]
        else:
            # Individual flag updates
            if enabled is not None:
                services[service_name]['enabled'] = enabled
                updated_flags.append(f"enabled={enabled}")
            
            if run_on_pr is not None:
                services[service_name]['runOnPR'] = run_on_pr
                updated_flags.append(f"runOnPR={run_on_pr}")
            
            if run_on_push is not None:
                services[service_name]['runOnPush'] = run_on_push
                updated_flags.append(f"runOnPush={run_on_push}")
            
            if run_on_schedule is not None:
                services[service_name]['runOnSchedule'] = run_on_schedule
                updated_flags.append(f"runOnSchedule={run_on_schedule}")
        
        if updated_flags:
            if not _skip_save:
                self._save_config()
            status_icon = "+" if (all_value or any([enabled, run_on_pr, run_on_push, run_on_schedule])) else "-"
            print(f"[{status_icon}] Service '{service_name}' updated:")
            for flag in updated_flags:
                print(f"   - {flag}")
        else:
            print(f"Warning: No flags specified to update")
    
    def simulate_run(self, run_type: str, environment: str = "DEV"):
        """Simulate a pipeline run to see which services would execute"""
        services = self.config.get('services', {})
        
        print("\n" + "="*80)
        print(f"🎭 SIMULATING {run_type.upper()} RUN")
        print(f"   Environment: {environment}")
        print("="*80)
        
        services_to_run = []
        
        for service_name, service_config in services.items():
            should_run = False
            reason = ""
            
            # Check if enabled
            if not service_config.get('enabled', True):
                continue
            
            # Check if environment is supported
            supported_envs = service_config.get('environments', ['DEV'])
            if environment not in supported_envs:
                continue
            
            # Check run conditions based on type
            if run_type == 'pr':
                should_run = service_config.get('runOnPR', False)
                reason = "runOnPR: true"
            elif run_type == 'push':
                should_run = service_config.get('runOnPush', True)
                reason = "runOnPush: true"
            elif run_type == 'schedule':
                should_run = service_config.get('runOnSchedule', True)
                reason = "runOnSchedule: true"
            elif run_type == 'manual':
                should_run = True
                reason = "Manual execution"
            
            if should_run:
                services_to_run.append({
                    'name': service_name,
                    'displayName': service_config.get('displayName', service_name),
                    'testType': service_config.get('testType', 'functional'),
                    'priority': service_config.get('priority', 2),
                    'reason': reason
                })
        
        # Sort by priority
        services_to_run.sort(key=lambda x: x['priority'])
        
        print(f"\n📊 Results: {len(services_to_run)} service(s) will run\n")
        
        if services_to_run:
            for i, service in enumerate(services_to_run, 1):
                print(f"{i}. ✅ {service['name']}")
                print(f"      Display: {service['displayName']}")
                print(f"      Test Type: {service['testType']}")
                print(f"      Priority: {service['priority']}")
                print(f"      Reason: {service['reason']}")
                print()
        else:
            print("⚠️ No services would run with current configuration\n")
        
        print("="*80 + "\n")
    
    def export_services_list(self, output_format: str = 'json'):
        """Export list of service names for pipeline consumption"""
        services = self.config.get('services', {})
        enabled_services = [name for name, config in services.items() if config.get('enabled', True)]
        
        if output_format == 'json':
            print(json.dumps(enabled_services, indent=2))
        elif output_format == 'comma':
            print(','.join(enabled_services))
        elif output_format == 'yaml':
            print(yaml.dump(enabled_services, default_flow_style=False))
        else:
            for service in enabled_services:
                print(service)
    
    def generate_summary_report(self):
        """Generate a summary report of the configuration"""
        services = self.config.get('services', {})
        
        total = len(services)
        enabled = sum(1 for s in services.values() if s.get('enabled', True))
        disabled = total - enabled
        
        run_on_pr = sum(1 for s in services.values() if s.get('runOnPR', False) and s.get('enabled', True))
        run_on_push = sum(1 for s in services.values() if s.get('runOnPush', True) and s.get('enabled', True))
        run_on_schedule = sum(1 for s in services.values() if s.get('runOnSchedule', True) and s.get('enabled', True))
        
        test_types = {}
        for service in services.values():
            if service.get('enabled', True):
                test_type = service.get('testType', 'functional')
                test_types[test_type] = test_types.get(test_type, 0) + 1
        
        print("\n" + "="*80)
        print("📊 SERVICE MATRIX SUMMARY REPORT")
        print("="*80)
        print(f"\n📈 Statistics:")
        print(f"   Total Services: {total}")
        print(f"   Enabled: {enabled} ({enabled/total*100:.1f}%)")
        print(f"   Disabled: {disabled} ({disabled/total*100:.1f}%)")
        print(f"\n🎯 Trigger Configuration:")
        print(f"   Run on PR: {run_on_pr} services")
        print(f"   Run on Push: {run_on_push} services")
        print(f"   Run on Schedule: {run_on_schedule} services")
        print(f"\n🧪 Test Types:")
        for test_type, count in test_types.items():
            print(f"   {test_type}: {count} services")
        print("\n" + "="*80 + "\n")
    
    def generate_pipeline_matrix(self, execution_mode: str = 'auto', 
                                 manual_services: str = '', 
                                 manual_environments: str = '',
                                 override_enabled: bool = False,
                                 test_type: str = 'functional',
                                 trigger_reason: str = 'Manual'):
        """
        Generate pipeline matrix for Azure DevOps dynamic job execution
        
        Args:
            execution_mode: 'auto' or 'manual'
            manual_services: Comma-separated list of services to run
            manual_environments: Comma-separated list of environments
            override_enabled: Run disabled services too
            test_type: 'functional', 'non-functional', or 'both'
            trigger_reason: Azure DevOps BUILD_REASON value
        """
        services_config = self.config.get('services', {})
        
        # Determine trigger type
        is_pr = trigger_reason == 'PullRequest'
        is_push = trigger_reason in ['IndividualCI', 'BatchedCI']
        is_schedule = trigger_reason == 'Schedule'
        is_manual = trigger_reason == 'Manual'
        
        print(f"Execution Mode: {execution_mode}")
        print(f"Trigger Reason: {trigger_reason}")
        print(f"Is PR: {is_pr}")
        print(f"Is Push: {is_push}")
        print(f"Is Schedule: {is_schedule}")
        print(f"Is Manual: {is_manual}")
        print(f"Override Enabled: {override_enabled}")
        print(f"Test Type: {test_type}")
        
        services_to_run = []
        
        # Parse manual selections
        selected_services = []
        if manual_services:
            selected_services = [s.strip() for s in manual_services.split(',') if s.strip()]
            print(f"Selected Services: {selected_services}")
        
        selected_environments = []
        if manual_environments:
            selected_environments = [e.strip() for e in manual_environments.split(',') if e.strip()]
            print(f"Selected Environments: {selected_environments}")
        
        # Iterate through services and determine which should run
        for service_name, service_config in services_config.items():
            enabled = service_config.get('enabled', True)
            run_on_pr = service_config.get('runOnPR', False)
            run_on_push = service_config.get('runOnPush', True)
            run_on_schedule = service_config.get('runOnSchedule', True)
            service_environments = service_config.get('environments', [])
            priority = service_config.get('priority', 2)
            
            should_run = False
            reason = ""
            
            # Check if service should run based on execution mode and trigger
            if execution_mode == 'manual' or is_manual:
                # Manual execution
                if selected_services:
                    # Run only selected services
                    if service_name in selected_services:
                        should_run = True
                        reason = "Manual selection"
                else:
                    # Run all enabled services (or all if override)
                    if enabled or override_enabled:
                        should_run = True
                        reason = "Manual run (all services)"
            else:
                # Automatic execution based on trigger
                if not enabled and not override_enabled:
                    should_run = False
                    reason = "Service disabled"
                elif is_pr and run_on_pr:
                    should_run = True
                    reason = "PR trigger"
                elif is_push and run_on_push:
                    should_run = True
                    reason = "Push trigger"
                elif is_schedule and run_on_schedule:
                    should_run = True
                    reason = "Schedule trigger"
            
            if should_run:
                # Determine environments to run
                envs_to_run = selected_environments if selected_environments else service_environments
                
                if not envs_to_run:
                    envs_to_run = ['TSADEV']  # Default fallback
                
                # Get test arguments
                functional_args = service_config.get('functionalTestArgs', '')
                non_functional_args = service_config.get('nonFunctionalTestArgs', '')
                service_test_type = service_config.get('testType', 'functional')
                
                # Determine actual test type to run
                if test_type == 'both':
                    actual_test_type = 'both'
                elif test_type in ['functional', 'non-functional']:
                    actual_test_type = test_type
                else:
                    actual_test_type = service_test_type
                
                # Create entries for each environment
                for env in envs_to_run:
                    # Substitute environment placeholders in test arguments
                    functional_args_resolved = functional_args.replace('{environment}', env)
                    non_functional_args_resolved = non_functional_args.replace('{environment}', env)
                    
                    service_info = {
                        'name': service_name,
                        'displayName': service_config.get('displayName', service_name),
                        'environment': env,
                        'priority': priority,
                        'testType': actual_test_type,
                        'functionalTestArgs': functional_args_resolved,
                        'nonFunctionalTestArgs': non_functional_args_resolved,
                        'reason': reason
                    }
                    
                    services_to_run.append(service_info)
                    print(f"✅ {service_name} [{env}]: {reason}")
        
        # Sort by priority
        services_to_run.sort(key=lambda x: x['priority'])
        
        print(f"\n{'='*60}")
        print(f"Total Service-Environment Combinations to Run: {len(services_to_run)}")
        print(f"{'='*60}")
        
        # Output for Azure DevOps
        if services_to_run:
            # Create matrix format for Azure DevOps
            # Azure DevOps matrix needs unique keys for each combination
            matrix_dict = {}
            for idx, service in enumerate(services_to_run):
                # Create unique key: servicename_environment
                matrix_key = f"{service['name']}_{service['environment']}"
                matrix_dict[matrix_key] = service
            
            matrix_json = json.dumps(matrix_dict, indent=2)
            print(f"\nServices Matrix (Azure DevOps format):\n{matrix_json}")
            
            # Set pipeline variables for Azure DevOps
            print(f"\n##vso[task.setvariable variable=servicesMatrix;isOutput=true]{json.dumps(matrix_dict)}")
            print(f"##vso[task.setvariable variable=hasServices;isOutput=true]true")
            print(f"##vso[task.setvariable variable=serviceCount;isOutput=true]{len(services_to_run)}")
            
            return True
        else:
            print("⚠️ No services to run based on current configuration and trigger")
            print(f"##vso[task.setvariable variable=hasServices;isOutput=true]false")
            print(f"##vso[task.setvariable variable=serviceCount;isOutput=true]0")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Service Matrix Manager - Manage services-matrix.yaml configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_matrix.py list
  python manage_matrix.py list --enabled-only
  python manage_matrix.py validate
  python manage_matrix.py enable work_item_notification
  python manage_matrix.py disable models
  python manage_matrix.py set-flag parties runOnPR true
  python manage_matrix.py set-flag movemoney runOnSchedule false
  python manage_matrix.py set-all-flags parties true
  python manage_matrix.py set-all-flags securities false
  python manage_matrix.py set-all-flags all true
  python manage_matrix.py set-all-flags all false
  python manage_matrix.py set-all-flags parties --enabled true --run-on-pr true --run-on-push true
  python manage_matrix.py simulate-pr
  python manage_matrix.py simulate-push --env TEST
  python manage_matrix.py export-services --format json
  python manage_matrix.py summary
  python manage_matrix.py generate-pipeline-matrix --trigger-reason PullRequest
  python manage_matrix.py generate-pipeline-matrix --execution-mode manual --services parties,movemoney
        """
    )
    
    parser.add_argument('command', 
                       choices=['list', 'validate', 'enable', 'disable', 'set-flag', 'set-all-flags',
                               'simulate-pr', 'simulate-push', 'simulate-schedule', 'simulate-manual',
                               'export-services', 'summary', 'generate-pipeline-matrix'],
                       help='Command to execute')
    
    parser.add_argument('service_name', nargs='?', help='Service name (for enable/disable/set-flag/set-all-flags commands)')
    parser.add_argument('flag_name', nargs='?', help='Flag name for set-flag command OR true/false for set-all-flags (enabled, runOnPR, runOnPush, runOnSchedule)')
    parser.add_argument('flag_value', nargs='?', help='Flag value for set-flag command (true/false)')
    parser.add_argument('--enabled-only', action='store_true', help='List only enabled services')
    parser.add_argument('--disabled-only', action='store_true', help='List only disabled services')
    parser.add_argument('--env', default='DEV', help='Environment for simulation (default: DEV)')
    parser.add_argument('--format', choices=['json', 'comma', 'yaml', 'list'], default='json',
                       help='Output format for export-services (default: json)')
    parser.add_argument('--config', default='config/services-matrix.yaml',
                       help='Path to services-matrix.yaml (default: config/services-matrix.yaml)')
    
    # Flags for set-all-flags command
    parser.add_argument('--enabled', type=lambda x: x.lower() == 'true', default=None,
                       help='Set enabled flag (true/false)')
    parser.add_argument('--run-on-pr', type=lambda x: x.lower() == 'true', default=None,
                       help='Set runOnPR flag (true/false)')
    parser.add_argument('--run-on-push', type=lambda x: x.lower() == 'true', default=None,
                       help='Set runOnPush flag (true/false)')
    parser.add_argument('--run-on-schedule', type=lambda x: x.lower() == 'true', default=None,
                       help='Set runOnSchedule flag (true/false)')
    
    # Pipeline-specific arguments
    parser.add_argument('--execution-mode', default='auto', choices=['auto', 'manual'],
                       help='Pipeline execution mode (default: auto)')
    parser.add_argument('--services', default='',
                       help='Comma-separated list of services to run (for manual mode)')
    parser.add_argument('--environments', default='',
                       help='Comma-separated list of environments (overrides service defaults)')
    parser.add_argument('--override-enabled', action='store_true',
                       help='Run disabled services too')
    parser.add_argument('--test-type', default='functional', 
                       choices=['functional', 'non-functional', 'both'],
                       help='Test type to run (default: functional)')
    parser.add_argument('--trigger-reason', default='Manual',
                       help='Azure DevOps BUILD_REASON (e.g., PullRequest, IndividualCI, Schedule, Manual)')
    
    args = parser.parse_args()
    
    manager = ServiceMatrixManager(config_path=args.config)
    
    if args.command == 'list':
        if args.enabled_only:
            manager.list_services(filter_enabled=True)
        elif args.disabled_only:
            manager.list_services(filter_enabled=False)
        else:
            manager.list_services()
    
    elif args.command == 'validate':
        is_valid = manager.validate()
        sys.exit(0 if is_valid else 1)
    
    elif args.command == 'enable':
        if not args.service_name:
            print("❌ Error: Service name required for enable command")
            sys.exit(1)
        manager.enable_service(args.service_name)
    
    elif args.command == 'disable':
        if not args.service_name:
            print("❌ Error: Service name required for disable command")
            sys.exit(1)
        manager.disable_service(args.service_name)
    
    elif args.command == 'set-flag':
        if not args.service_name or not args.flag_name or not args.flag_value:
            print("❌ Error: set-flag requires service_name, flag_name, and flag_value")
            print("Usage: python manage_matrix.py set-flag <service> <flag> <true|false>")
            print("Flags: enabled, runOnPR, runOnPush, runOnSchedule")
            sys.exit(1)
        
        value = args.flag_value.lower() == 'true'
        manager.set_flag(args.service_name, args.flag_name, value)
    
    elif args.command == 'set-all-flags':
        if not args.service_name:
            print("Error: Service name required for set-all-flags command")
            print("Usage: python manage_matrix.py set-all-flags <service> <true|false>")
            print("   OR: python manage_matrix.py set-all-flags <service> [--enabled true] [--run-on-pr true] [--run-on-push false] [--run-on-schedule true]")
            sys.exit(1)
        
        # Check if a simple true/false value was provided as second argument (flag_name position)
        all_value = None
        if args.flag_name and args.flag_name.lower() in ['true', 'false']:
            all_value = args.flag_name.lower() == 'true'
        
        manager.set_all_flags(
            args.service_name,
            all_value=all_value,
            enabled=args.enabled,
            run_on_pr=args.run_on_pr,
            run_on_push=args.run_on_push,
            run_on_schedule=args.run_on_schedule
        )
    
    elif args.command == 'simulate-pr':
        manager.simulate_run('pr', environment=args.env)
    
    elif args.command == 'simulate-push':
        manager.simulate_run('push', environment=args.env)
    
    elif args.command == 'simulate-schedule':
        manager.simulate_run('schedule', environment=args.env)
    
    elif args.command == 'simulate-manual':
        manager.simulate_run('manual', environment=args.env)
    
    elif args.command == 'export-services':
        manager.export_services_list(output_format=args.format)
    
    elif args.command == 'summary':
        manager.generate_summary_report()
    
    elif args.command == 'generate-pipeline-matrix':
        has_services = manager.generate_pipeline_matrix(
            execution_mode=args.execution_mode,
            manual_services=args.services,
            manual_environments=args.environments,
            override_enabled=args.override_enabled,
            test_type=args.test_type,
            trigger_reason=args.trigger_reason
        )
        sys.exit(0 if has_services else 0)  # Always exit 0, hasServices variable controls flow


if __name__ == '__main__':
    main()

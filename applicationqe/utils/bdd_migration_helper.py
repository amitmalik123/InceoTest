"""
Migration utility to update existing BDD step definitions to use orchestrated flows
Helps convert individual step-by-step actions to orchestrated workflow calls
"""
import os
import re
import logging
from typing import List, Tuple, Dict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BDDOrchestrationMigrator:
    """Migrates existing BDD step definitions to use orchestrated flows"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.steps_dir = os.path.join(project_root, 'tests', 'bdd', 'steps')
        
        # Mapping of individual actions to orchestrated flow methods
        self.action_mappings = {
            # Login Flow Actions
            'handle.*cookie.*consent': 'execute_login_flow',
            'enter.*username.*password': 'execute_login_flow', 
            'click.*sign.*in': 'execute_login_flow',
            'authenticate.*user': 'execute_login_flow',
            
            # Landing Page Actions
            'click.*journal.*transfer': 'execute_landing_page_flow',
            'navigate.*journal.*transfer': 'execute_landing_page_flow',
            'select.*journal.*transfer': 'execute_landing_page_flow',
            
            # Transfer Configuration Actions
            'select.*from.*account': 'execute_transfer_page_flow',
            'select.*to.*account': 'execute_transfer_page_flow',
            'configure.*transfer.*settings': 'execute_transfer_page_flow',
            'click.*next.*transfer': 'execute_transfer_page_flow',
            
            # Transaction Details Actions
            'enter.*asset.*details': 'execute_transaction_details_flow',
            'select.*portion.*transfer': 'execute_transaction_details_flow',
            'configure.*transaction': 'execute_transaction_details_flow',
            'click.*next.*transaction': 'execute_transaction_details_flow',
            
            # Request Summary Actions
            'review.*request.*summary': 'execute_request_summary_flow',
            'validate.*summary.*details': 'execute_request_summary_flow',
            'click.*next.*summary': 'execute_request_summary_flow',
            
            # Review and Submission Actions
            'review.*final.*details': 'execute_review_summary_flow',
            'submit.*request': 'execute_final_submission_flow',
            'handle.*esignature': 'execute_esignature_flow',
            'handle.*docusign': 'execute_docusign_flow',
            
            # Confirmation Actions
            'capture.*request.*number': 'execute_confirmation_flow',
            'validate.*confirmation': 'execute_confirmation_flow',
            
            # Tracking Actions
            'navigate.*tracking.*center': 'execute_tracking_center_flow',
            'search.*request.*status': 'execute_tracking_center_flow'
        }
    
    def find_step_files(self) -> List[str]:
        """Find all step definition files"""
        step_files = []
        if os.path.exists(self.steps_dir):
            for file in os.listdir(self.steps_dir):
                if file.endswith('_steps.py') and file != 'orchestrated_flow_steps.py':
                    step_files.append(os.path.join(self.steps_dir, file))
        return step_files
    
    def analyze_step_file(self, file_path: str) -> Dict[str, List[str]]:
        """Analyze a step file for migration opportunities"""
        analysis = {
            'individual_actions': [],
            'potential_orchestrations': [],
            'complex_steps': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find step definitions
            step_pattern = r'@(?:given|when|then)\s*\([\'\"](.*?)[\'\"]'
            steps = re.findall(step_pattern, content, re.IGNORECASE)
            
            for step in steps:
                # Check if step matches individual actions
                for action_pattern, orchestrated_method in self.action_mappings.items():
                    if re.search(action_pattern, step, re.IGNORECASE):
                        analysis['individual_actions'].append(step)
                        analysis['potential_orchestrations'].append(orchestrated_method)
                        break
                else:
                    # Complex step that might need manual review
                    if len(step) > 50 or 'click' in step.lower() or 'enter' in step.lower():
                        analysis['complex_steps'].append(step)
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
        
        return analysis
    
    def generate_migration_suggestions(self, file_path: str) -> List[str]:
        """Generate migration suggestions for a step file"""
        analysis = self.analyze_step_file(file_path)
        suggestions = []
        
        if analysis['individual_actions']:
            suggestions.append(f"File: {os.path.basename(file_path)}")
            suggestions.append("=" * 50)
            suggestions.append("")
            
            suggestions.append("Individual actions that can be orchestrated:")
            for i, action in enumerate(analysis['individual_actions']):
                orchestrated = analysis['potential_orchestrations'][i]
                suggestions.append(f"  • '{action}' → {orchestrated}()")
            
            suggestions.append("")
        
        if analysis['complex_steps']:
            suggestions.append("Complex steps requiring manual review:")
            for step in analysis['complex_steps']:
                suggestions.append(f"  • '{step}'")
            suggestions.append("")
        
        return suggestions
    
    def create_migration_report(self) -> str:
        """Create a comprehensive migration report"""
        report_lines = []
        report_lines.append("BDD ORCHESTRATION MIGRATION REPORT")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        step_files = self.find_step_files()
        
        if not step_files:
            report_lines.append("No step files found for migration.")
            return "\n".join(report_lines)
        
        total_individual_actions = 0
        
        for file_path in step_files:
            suggestions = self.generate_migration_suggestions(file_path)
            if suggestions:
                report_lines.extend(suggestions)
                
                # Count individual actions  
                analysis = self.analyze_step_file(file_path)
                total_individual_actions += len(analysis['individual_actions'])
        
        # Summary
        report_lines.append("MIGRATION SUMMARY")
        report_lines.append("=" * 50)
        report_lines.append(f"Files analyzed: {len(step_files)}")
        report_lines.append(f"Individual actions found: {total_individual_actions}")
        report_lines.append("")
        report_lines.append("RECOMMENDED ACTIONS:")
        report_lines.append("1. Replace individual actions with orchestrated flow calls")
        report_lines.append("2. Use orchestrated_flow_steps.py as the new step definitions")
        report_lines.append("3. Update feature files to use orchestrated scenarios")
        report_lines.append("4. Test with run_orchestrated_tests.bat")
        report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_migration_report(self, output_path: str = None) -> str:
        """Save migration report to file"""
        if not output_path:
            output_path = os.path.join(self.project_root, 'docs', 'BDD_ORCHESTRATION_MIGRATION_REPORT.md')
        
        report = self.create_migration_report()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Migration report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving migration report: {str(e)}")
            return None


def main():
    """Main execution function"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logger.info("Starting BDD Orchestration Migration Analysis...")
    logger.info(f"Project root: {project_root}")
    
    migrator = BDDOrchestrationMigrator(project_root)
    
    # Generate and save migration report
    report_path = migrator.save_migration_report()
    
    if report_path:
        logger.info("Migration analysis completed successfully!")
        logger.info(f"Review the migration report: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("BDD ORCHESTRATION MIGRATION ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Report saved to: {report_path}")
        print("\nNext Steps:")
        print("1. Review the migration report")
        print("2. Update feature files to use orchestrated scenarios")
        print("3. Run tests with: run_orchestrated_tests.bat")
        print("=" * 60)
    else:
        logger.error("Migration analysis failed!")


if __name__ == "__main__":
    main()
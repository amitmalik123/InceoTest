"""
Journal Transfer Request Flow - Orchestrates transfer request page operations
Handles transaction configuration workflows combining transfer request actions
"""
from playwright.sync_api import Page
from pages.ewm.transaction_details_page import TransactionDetailsPage
from typing import Dict, Any, List

class JournalTransferRequestFlow:
    """Flow orchestrating journal transfer request page operations"""

    def __init__(self, page: Page):
        self.page = page
        self.transfer_request_page = TransactionDetailsPage(page)

    def execute_journal_portion_configuration(self, amount: str, portion_type: str = "$ Amount") -> Dict[str, Any]:
        """Configure journal portion transfer with comprehensive settings"""
        results = {
            "success": False,
            "distribution_type": "Journal Portion of Account",
            "portion_type": portion_type,
            "amount": amount
        }
        
        try:
            # Select distribution type
            self.transfer_request_page.select_distribution_type("Journal Portion of Account")
            
            # Configure portion details
            self.transfer_request_page.configure_journal_portion(amount, portion_type)
            
            results.update({
                "success": True,
                "configuration_completed": True
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def execute_journal_securities_configuration(self, securities_count: int = 2) -> Dict[str, Any]:
        """Configure journal securities transfer"""
        results = {
            "success": False,
            "distribution_type": "Journal Securities", 
            "securities_selected": []
        }
        
        try:
            # Select distribution type
            self.transfer_request_page.select_distribution_type("Journal Securities")
            
            # Select securities
            selection_results = self.transfer_request_page.select_all_securities(securities_count)
            
            results.update({
                "success": True,
                "securities_selected": selection_results,
                "securities_count": len([r for r in selection_results if r]),
                "configuration_completed": True
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def execute_signature_configuration(self, signature_option: str) -> Dict[str, Any]:
        """Configure signature option"""
        results = {
            "success": False,
            "signature_option": signature_option
        }
        
        try:
            self.transfer_request_page.select_signature_option(signature_option)
            
            results.update({
                "success": True,
                "signature_configured": True
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def execute_complete_transaction_configuration(self, transaction_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete transaction configuration workflow"""
        results = {
            "success": False,
            "steps_completed": [],
            "final_configuration": {}
        }
        
        try:
            completed_steps = []
            
            # Configure distribution based on type
            distribution_type = transaction_config.get("distribution_type", "Journal Portion of Account")
            
            if distribution_type == "Journal Portion of Account":
                portion_results = self.execute_journal_portion_configuration(
                    transaction_config.get("amount", "45.00"),
                    transaction_config.get("portion_type", "$ Amount")
                )
                results["distribution_results"] = portion_results
                completed_steps.append("distribution_configuration")
                
            elif distribution_type == "Journal Securities":
                securities_results = self.execute_journal_securities_configuration(
                    transaction_config.get("securities_count", 2)
                )
                results["distribution_results"] = securities_results
                completed_steps.append("distribution_configuration")
            
            # Configure signature
            if "signature_option" in transaction_config:
                signature_results = self.execute_signature_configuration(
                    transaction_config["signature_option"]
                )
                results["signature_results"] = signature_results
                completed_steps.append("signature_configuration")
            
            results.update({
                "success": True,
                "steps_completed": completed_steps,
                "final_configuration": transaction_config
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def proceed_to_review(self) -> Dict[str, Any]:
        """Proceed from transfer request to review page"""
        results = {
            "success": False,
            "navigation_completed": False
        }
        
        try:
            self.transfer_request_page.click_next_button()
            results.update({
                "success": True,
                "navigation_completed": True
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def return_to_landing(self) -> Dict[str, Any]:
        """Return from transfer request to landing page"""
        results = {
            "success": False,
            "navigation_completed": False
        }
        
        try:
            self.transfer_request_page.click_back_button()
            results.update({
                "success": True,
                "navigation_completed": True
            })
            
        except Exception as e:
            results["error"] = str(e)
            
        return results
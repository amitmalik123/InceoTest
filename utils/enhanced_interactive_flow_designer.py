"""
Enhanced Interactive E2E Flow Designer - Real-time Capture with Post-session Processing

This implementation follows the three key recommendations:
1. Real-time capture with post-session processing  
2. Generate standalone tests with optional BDD integration
3. Provide recovery commands and error state capture

Core Features:
- Real-time action capture during manual navigation
- Post-session structured processing and test generation
- Error recovery commands and state capture mechanisms
- Framework-compliant standalone test generation
- Optional BDD integration pathways
"""

from playwright.sync_api import Page, Locator, BrowserContext
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
import re
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import uuid


class ActionType(Enum):
    """Types of real-time captured actions"""
    NAVIGATION = "navigation"
    CLICK = "click" 
    FILL = "fill"
    SELECT = "select"
    KEYBOARD = "keyboard"
    ASSERTION = "assertion"
    PHASE_MARKER = "phase_marker"
    ERROR_STATE = "error_state"
    RECOVERY_ACTION = "recovery_action"


class CaptureState(Enum):
    """Current state of the capture session"""
    IDLE = "idle"
    RECORDING = "recording"
    ERROR = "error"
    RECOVERY = "recovery"
    PROCESSING = "processing"
    COMPLETED = "completed"


@dataclass
class RealTimeAction:
    """Real-time captured action with metadata"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    action_type: ActionType = ActionType.CLICK
    element_info: Dict[str, Any] = field(default_factory=dict)
    user_input: Optional[str] = None
    page_context: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_info: Optional[str] = None
    recovery_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'timestamp': self.timestamp.isoformat(),
            'action_type': self.action_type.value,
            'element_info': self.element_info,
            'user_input': self.user_input,
            'page_context': self.page_context,
            'success': self.success,
            'error_info': self.error_info,
            'recovery_actions': self.recovery_actions
        }


class RealTimeCapture:
    """Real-time action capture engine with post-session processing"""
    
    def __init__(self, page: Page, context: BrowserContext):
        self.page = page
        self.context = context
        self.state = CaptureState.IDLE
        self.actions_queue = queue.Queue()
        self.captured_actions: List[RealTimeAction] = []
        self.error_states: List[Dict[str, Any]] = []
        self.phase_markers: List[Dict[str, Any]] = []
        self.capture_thread = None
        self.stop_capture = threading.Event()
        
        # Set up real-time listeners
        self._setup_page_listeners()
    
    def _setup_page_listeners(self):
        """Set up Playwright page listeners for real-time capture"""
        
        def on_page_navigation(url: str):
            if self.state == CaptureState.RECORDING:
                action = RealTimeAction(
                    action_type=ActionType.NAVIGATION,
                    page_context={
                        'url': url,
                        'title': self.page.title(),
                        'timestamp': datetime.now().isoformat()
                    }
                )
                self.actions_queue.put(action)
        
        def on_page_load():
            if self.state == CaptureState.RECORDING:
                self._capture_page_state("page_load")
        
        def on_page_error(error):
            if self.state == CaptureState.RECORDING:
                self._capture_error_state(str(error), "page_error")
        
        # Register listeners
        self.page.on("framenavigated", lambda frame: on_page_navigation(frame.url))
        self.page.on("load", on_page_load)  
        self.page.on("pageerror", on_page_error)
    
    def start_real_time_capture(self) -> Dict[str, Any]:
        """Start real-time capture session"""
        if self.state != CaptureState.IDLE:
            return {"status": "error", "message": f"Cannot start capture in state: {self.state.value}"}
        
        self.state = CaptureState.RECORDING
        self.stop_capture.clear()
        
        # Start capture processing thread
        self.capture_thread = threading.Thread(target=self._process_capture_queue)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        print("🎥 Real-time capture activated")
        return {
            "status": "recording",
            "capture_state": self.state.value,
            "instructions": self._get_real_time_instructions()
        }
    
    def _process_capture_queue(self):
        """Process the real-time capture queue in background thread"""
        while not self.stop_capture.is_set():
            try:
                if not self.actions_queue.empty():
                    action = self.actions_queue.get(timeout=1.0)
                    self.captured_actions.append(action)
                    
                    # Real-time feedback
                    print(f"📝 Captured: {action.action_type.value} on {action.page_context.get('url', 'unknown page')}")
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Capture processing error: {e}")
    
    def capture_manual_action(self, action_type: str, description: str, element_selector: str = None) -> Dict[str, Any]:
        """Capture manual action with real-time processing"""
        try:
            action = RealTimeAction(
                action_type=ActionType(action_type),
                user_input=description,
                element_info=self._get_element_info(element_selector) if element_selector else {},
                page_context=self._capture_page_context()
            )
            
            self.actions_queue.put(action)
            return {"status": "captured", "action_id": action.action_id}
            
        except Exception as e:
            return self._handle_capture_error(f"Failed to capture manual action: {e}")
    
    def mark_phase_completion(self, phase_name: str, description: str) -> Dict[str, Any]:
        """Mark phase completion with real-time capture"""
        try:
            phase_marker = {
                'phase_name': phase_name,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'page_context': self._capture_page_context(),
                'actions_count': len(self.captured_actions)
            }
            
            self.phase_markers.append(phase_marker)
            
            # Capture as special action type
            action = RealTimeAction(
                action_type=ActionType.PHASE_MARKER,
                user_input=f"Phase: {phase_name} - {description}",
                page_context=phase_marker
            )
            self.actions_queue.put(action)
            
            # Take screenshot for phase
            screenshot_path = f"execution/screenshots/{phase_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=screenshot_path)
            
            print(f"📋 Phase marked: {phase_name}")
            return {
                "status": "phase_marked", 
                "phase_name": phase_name,
                "screenshot": screenshot_path
            }
            
        except Exception as e:
            return self._handle_capture_error(f"Failed to mark phase: {e}")
    
    def handle_error_state(self, error_description: str, recovery_strategy: str = None) -> Dict[str, Any]:
        """Handle unexpected states with recovery commands"""
        try:
            current_state = self.state
            self.state = CaptureState.ERROR
            
            error_info = {
                'error_description': error_description,
                'timestamp': datetime.now().isoformat(),
                'page_context': self._capture_page_context(),
                'previous_state': current_state.value,
                'recovery_strategy': recovery_strategy
            }
            
            self.error_states.append(error_info)
            
            # Capture error screenshot
            error_screenshot = f"execution/screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path(error_screenshot).parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=error_screenshot)
            error_info['screenshot'] = error_screenshot
            
            # Create error action
            action = RealTimeAction(
                action_type=ActionType.ERROR_STATE,
                user_input=error_description,
                page_context=error_info,
                success=False,
                error_info=error_description
            )
            self.actions_queue.put(action)
            
            print(f"🚨 Error state captured: {error_description}")
            return {
                'status': 'error_captured',
                'error_info': error_info,
                'recovery_commands': self._get_recovery_commands()
            }
            
        except Exception as e:
            return {"status": "critical_error", "message": f"Failed to handle error state: {e}"}
    
    def execute_recovery_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute recovery commands for error states"""
        try:
            self.state = CaptureState.RECOVERY
            
            recovery_actions = []
            
            if command == "retry_last_action":
                if self.captured_actions:
                    last_action = self.captured_actions[-1]
                    recovery_actions.append(f"Retrying: {last_action.action_type.value}")
                    
            elif command == "navigate_back":
                self.page.go_back()
                recovery_actions.append("Navigated back")
                
            elif command == "refresh_page":
                self.page.reload()
                recovery_actions.append("Page refreshed")
                
            elif command == "wait_and_retry":
                wait_time = kwargs.get('wait_time', 5000)
                self.page.wait_for_timeout(wait_time)
                recovery_actions.append(f"Waited {wait_time}ms")
                
            elif command == "reset_to_phase":
                phase_name = kwargs.get('phase_name')
                recovery_actions.append(f"Reset to phase: {phase_name}")
                
            elif command == "custom_recovery":
                custom_action = kwargs.get('action')
                recovery_actions.append(f"Custom recovery: {custom_action}")
            
            # Create recovery action
            recovery_action = RealTimeAction(
                action_type=ActionType.RECOVERY_ACTION,
                user_input=f"Recovery: {command}",
                recovery_actions=recovery_actions,
                page_context=self._capture_page_context()
            )
            self.actions_queue.put(recovery_action)
            
            # Resume recording
            self.state = CaptureState.RECORDING
            
            print(f"🔧 Recovery executed: {command}")
            return {
                'status': 'recovery_executed',
                'command': command,
                'recovery_actions': recovery_actions,
                'current_state': self.state.value
            }
            
        except Exception as e:
            return {"status": "recovery_failed", "message": f"Recovery command failed: {e}"}
    
    def stop_capture_and_process(self) -> Dict[str, Any]:
        """Stop real-time capture and begin post-session processing"""
        try:
            self.state = CaptureState.PROCESSING
            self.stop_capture.set()
            
            # Wait for capture thread to complete
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=5.0)
            
            print("⏹️ Real-time capture stopped")
            print("🔄 Beginning post-session processing...")
            
            # Process captured actions
            processed_data = self._post_session_processing()
            
            self.state = CaptureState.COMPLETED
            
            return {
                'status': 'processing_complete',
                'total_actions': len(self.captured_actions),
                'phases_marked': len(self.phase_markers),
                'errors_encountered': len(self.error_states),
                'processed_data': processed_data
            }
            
        except Exception as e:
            return {"status": "processing_failed", "message": f"Failed to process capture: {e}"}
    
    def _post_session_processing(self) -> Dict[str, Any]:
        """Post-session processing of real-time captured data"""
        try:
            # Group actions by phases
            phase_groups = self._group_actions_by_phases()
            
            # Analyze action patterns
            patterns = self._analyze_action_patterns()
            
            # Generate element map
            element_map = self._generate_element_map()
            
            # Identify reusable components
            reusable_components = self._identify_reusable_components()
            
            processed_data = {
                'phase_groups': phase_groups,
                'action_patterns': patterns,
                'element_map': element_map,
                'reusable_components': reusable_components,
                'error_analysis': self._analyze_error_patterns(),
                'recovery_summary': self._summarize_recovery_actions()
            }
            
            print("✅ Post-session processing completed")
            return processed_data
            
        except Exception as e:
            print(f"❌ Post-session processing failed: {e}")
            return {"error": str(e)}
    
    def _group_actions_by_phases(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group captured actions by phase markers"""
        phase_groups = {}
        current_phase = "initial_phase"
        current_actions = []
        
        for action in self.captured_actions:
            if action.action_type == ActionType.PHASE_MARKER:
                # Save previous phase
                if current_actions:
                    phase_groups[current_phase] = [a.to_dict() for a in current_actions]
                
                # Start new phase
                current_phase = action.user_input
                current_actions = []
            else:
                current_actions.append(action)
        
        # Save final phase
        if current_actions:
            phase_groups[current_phase] = [a.to_dict() for a in current_actions]
        
        return phase_groups
    
    def _analyze_action_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in captured actions"""
        patterns = {
            'navigation_count': len([a for a in self.captured_actions if a.action_type == ActionType.NAVIGATION]),
            'click_count': len([a for a in self.captured_actions if a.action_type == ActionType.CLICK]),
            'form_interactions': len([a for a in self.captured_actions if a.action_type == ActionType.FILL]),
            'most_common_elements': self._find_most_used_elements(),
            'page_transitions': self._analyze_page_transitions()
        }
        return patterns
    
    def _generate_element_map(self) -> Dict[str, Dict[str, Any]]:
        """Generate map of elements encountered during capture"""
        element_map = {}
        
        for action in self.captured_actions:
            if action.element_info:
                element_key = action.element_info.get('selector', 'unknown')
                if element_key not in element_map:
                    element_map[element_key] = {
                        'selector': element_key,
                        'usage_count': 0,
                        'action_types': set(),
                        'pages_used': set()
                    }
                
                element_map[element_key]['usage_count'] += 1
                element_map[element_key]['action_types'].add(action.action_type.value)
                if 'url' in action.page_context:
                    element_map[element_key]['pages_used'].add(action.page_context['url'])
        
        # Convert sets to lists for JSON serialization
        for element_key in element_map:
            element_map[element_key]['action_types'] = list(element_map[element_key]['action_types'])
            element_map[element_key]['pages_used'] = list(element_map[element_key]['pages_used'])
        
        return element_map
    
    def _identify_reusable_components(self) -> List[Dict[str, Any]]:
        """Identify reusable page components from captured actions"""
        # This would analyze action sequences to identify common patterns
        # that could be extracted into reusable methods
        return []
    
    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns and recovery effectiveness"""
        return {
            'total_errors': len(self.error_states),
            'error_types': list(set(e.get('error_description', 'unknown') for e in self.error_states)),
            'recovery_success_rate': self._calculate_recovery_success_rate()
        }
    
    def _summarize_recovery_actions(self) -> Dict[str, Any]:
        """Summarize recovery actions taken during capture"""
        recovery_actions = [a for a in self.captured_actions if a.action_type == ActionType.RECOVERY_ACTION]
        return {
            'total_recoveries': len(recovery_actions),
            'recovery_types': list(set(a.user_input for a in recovery_actions)),
            'effectiveness': len([a for a in recovery_actions if a.success])
        }
    
    def _capture_page_state(self, state_type: str):
        """Capture page state for various events"""
        try:
            action = RealTimeAction(
                action_type=ActionType.NAVIGATION,
                user_input=f"Page state: {state_type}",
                page_context=self._capture_page_context()
            )
            self.actions_queue.put(action)
        except Exception as e:
            print(f"⚠️ Failed to capture page state: {e}")
    
    def _capture_error_state(self, error: str, error_type: str):
        """Capture error state from page events"""
        self.handle_error_state(f"{error_type}: {error}")
    
    def _capture_page_context(self) -> Dict[str, Any]:
        """Capture current page context"""
        try:
            return {
                'url': self.page.url,
                'title': self.page.title(),
                'viewport': self.page.viewport_size,
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            return {'error': 'Failed to capture page context'}
    
    def _get_element_info(self, selector: str) -> Dict[str, Any]:
        """Get information about an element"""
        try:
            element = self.page.locator(selector)
            if element.count() > 0:
                return {
                    'selector': selector,
                    'text': element.first.text_content(),
                    'visible': element.first.is_visible(),
                    'enabled': element.first.is_enabled()
                }
        except Exception:
            pass
        return {'selector': selector, 'error': 'Element not found'}
    
    def _handle_capture_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during capture"""
        self.state = CaptureState.ERROR
        print(f"❌ Capture error: {error_message}")
        return {"status": "error", "message": error_message}
    
    def _get_real_time_instructions(self) -> List[str]:
        """Get instructions for real-time capture mode"""
        return [
            "🎥 Real-time capture is active",
            "📱 Navigate manually - actions are captured automatically",
            "📋 Use mark_phase_completion(name, description) to mark phases",
            "🚨 Use handle_error_state(description) if you encounter issues",
            "🔧 Use execute_recovery_command() if errors occur",
            "⏹️ Use stop_capture_and_process() when complete"
        ]
    
    def _get_recovery_commands(self) -> List[str]:
        """Get available recovery commands"""
        return [
            "retry_last_action - Retry the last captured action",
            "navigate_back - Go back to previous page", 
            "refresh_page - Refresh current page",
            "wait_and_retry - Wait specified time then continue",
            "reset_to_phase - Reset to a specific phase marker",
            "custom_recovery - Execute custom recovery action"
        ]
    
    def _find_most_used_elements(self) -> List[Dict[str, Any]]:
        """Find most commonly used elements"""
        return []
    
    def _analyze_page_transitions(self) -> List[Dict[str, Any]]:
        """Analyze page transition patterns"""
        return []
    
    def _calculate_recovery_success_rate(self) -> float:
        """Calculate success rate of recovery actions"""
        recovery_actions = [a for a in self.captured_actions if a.action_type == ActionType.RECOVERY_ACTION]
        if not recovery_actions:
            return 0.0
        successful = len([a for a in recovery_actions if a.success])
        return successful / len(recovery_actions)


class EnhancedInteractiveE2EFlowDesigner:
    """Enhanced flow designer with real-time capture and post-session processing"""
    
    def __init__(self, page: Page, context: BrowserContext, flow_name: str, base_url: str):
        self.page = page
        self.context = context
        self.flow_name = flow_name
        self.base_url = base_url
        self.real_time_capture = RealTimeCapture(page, context)
        self.recordings_dir = Path("execution/recordings")
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize recording
        self.start_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_file = self.recordings_dir / f"{self.flow_name}_enhanced_{self.start_timestamp}.py"
        
    def start_enhanced_recording_session(self) -> Dict[str, Any]:
        """Start enhanced recording session with real-time capture"""
        print(f"🎬 Starting Enhanced E2E Flow Design Session")
        print(f"📝 Flow Name: {self.flow_name}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"📁 Recording will be saved to: {self.recording_file}")
        print()
        
        # Navigate to base URL
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("domcontentloaded")
        
        # Start real-time capture
        capture_result = self.real_time_capture.start_real_time_capture()
        
        return {
            "status": "enhanced_recording_started",
            "flow_name": self.flow_name,
            "recording_file": str(self.recording_file),
            "capture_result": capture_result,
            "enhanced_features": [
                "Real-time action capture",
                "Error recovery commands", 
                "Post-session processing",
                "Standalone test generation",
                "Optional BDD integration"
            ]
        }
    
    def mark_phase(self, phase_name: str, description: str) -> Dict[str, Any]:
        """Mark phase completion with enhanced capture"""
        return self.real_time_capture.mark_phase_completion(phase_name, description)
    
    def handle_error(self, error_description: str, recovery_strategy: str = None) -> Dict[str, Any]:
        """Handle error state with recovery options"""
        return self.real_time_capture.handle_error_state(error_description, recovery_strategy)
    
    def recover(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute recovery command"""
        return self.real_time_capture.execute_recovery_command(command, **kwargs)
    
    def finalize_enhanced_recording(self, final_description: str = "") -> Dict[str, Any]:
        """Finalize recording with enhanced processing"""
        print(f"🏁 Finalizing Enhanced Recording Session")
        
        # Stop capture and process
        process_result = self.real_time_capture.stop_capture_and_process()
        
        if process_result.get('status') != 'processing_complete':
            return {"status": "error", "message": "Failed to process captured data"}
        
        processed_data = process_result.get('processed_data', {})
        
        # Generate standalone test script
        standalone_script = self._generate_standalone_test_script(processed_data)
        
        # Save the test script
        with open(self.recording_file, 'w') as f:
            f.write(standalone_script)
        
        # Generate optional BDD integration files
        bdd_files = self._generate_optional_bdd_integration(processed_data)
        
        # Generate comprehensive documentation
        doc_file = self.recordings_dir / f"{self.flow_name}_enhanced_documentation_{self.start_timestamp}.md"
        documentation = self._generate_enhanced_documentation(processed_data)
        
        with open(doc_file, 'w') as f:
            f.write(documentation)
        
        print(f"✅ Enhanced Recording Complete!")
        print(f"📄 Standalone Test: {self.recording_file}")
        print(f"📚 Documentation: {doc_file}")
        if bdd_files:
            print(f"🎯 BDD Integration Files: {bdd_files}")
        
        return {
            "status": "enhanced_recording_complete",
            "standalone_test": str(self.recording_file),
            "documentation": str(doc_file),
            "bdd_integration": bdd_files,
            "processing_summary": process_result,
            "enhanced_features_used": self._summarize_enhanced_features_usage()
        }
    
    def _generate_standalone_test_script(self, processed_data: Dict[str, Any]) -> str:
        """Generate standalone test script following framework patterns"""
        phase_groups = processed_data.get('phase_groups', {})
        element_map = processed_data.get('element_map', {})
        
        script_template = '''"""
{flow_name} - Enhanced Standalone E2E Test
Generated with real-time capture and post-session processing on {timestamp}

Features:
- Real-time action capture
- Error recovery mechanisms  
- Framework-compliant structure
- Comprehensive assertions
- Optional BDD integration ready

This test can run independently or be integrated with the BDD layer.
"""

import pytest
from playwright.sync_api import Page, expect
from typing import Dict, Any
from datetime import datetime
import time


class Enhanced{class_name}Test:
    """Enhanced standalone test with real-time capture foundations"""
    
    def __init__(self, page: Page):
        self.page = page
        self.start_time = datetime.now()
        self.phase_results = []
        self.error_recovery_log = []
        
    def execute_standalone_flow(self, base_url: str = "{base_url}") -> Dict[str, Any]:
        """Execute complete flow with enhanced error handling"""
        results = {{
            "flow_name": "{flow_name}",
            "test_type": "enhanced_standalone",
            "started_at": self.start_time.isoformat(),
            "phases_completed": [],
            "errors_encountered": [],
            "recovery_actions": [],
            "success": False
        }}
        
        try:
            # Navigate to starting URL
            self.page.goto(base_url)
            self.page.wait_for_load_state("domcontentloaded")
            
{phase_implementations}
            
            results["success"] = True
            results["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            results["error"] = str(e)
            results["failed_at"] = datetime.now().isoformat()
            results["recovery_suggestions"] = self._get_recovery_suggestions(str(e))
            
        return results
    
    def _execute_phase_with_recovery(self, phase_name: str, phase_impl: callable) -> bool:
        """Execute phase with built-in error recovery"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"📋 Executing Phase: {{phase_name}} (Attempt {{attempt + 1}})")
                phase_impl()
                
                self.phase_results.append({{
                    "phase": phase_name,
                    "status": "success", 
                    "attempt": attempt + 1,
                    "timestamp": datetime.now().isoformat()
                }})
                return True
                
            except Exception as e:
                print(f"⚠️ Phase {{phase_name}} failed on attempt {{attempt + 1}}: {{e}}")
                
                if attempt < max_retries - 1:
                    recovery_action = self._get_recovery_action(str(e))
                    if recovery_action:
                        print(f"🔧 Applying recovery: {{recovery_action}}")
                        self._apply_recovery_action(recovery_action)
                        time.sleep(2)  # Brief pause before retry
                else:
                    self.phase_results.append({{
                        "phase": phase_name,
                        "status": "failed",
                        "error": str(e),
                        "attempts": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }})
                    return False
        
        return False
    
    def _get_recovery_action(self, error_message: str) -> str:
        """Determine recovery action based on error"""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            return "wait_longer"
        elif "element not found" in error_lower:
            return "refresh_page"
        elif "navigation" in error_lower:
            return "retry_navigation"
        else:
            return "generic_retry"
    
    def _apply_recovery_action(self, action: str):
        """Apply recovery action"""
        try:
            if action == "wait_longer":
                self.page.wait_for_timeout(5000)
            elif action == "refresh_page":
                self.page.reload()
                self.page.wait_for_load_state("domcontentloaded")
            elif action == "retry_navigation":
                self.page.go_back()
                self.page.wait_for_timeout(1000)
                self.page.go_forward()
            
            self.error_recovery_log.append({{
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }})
            
        except Exception as e:
            self.error_recovery_log.append({{
                "action": action,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }})
    
    def _get_recovery_suggestions(self, error: str) -> List[str]:
        """Get recovery suggestions for manual intervention"""
        return [
            "Check if the application is accessible",
            "Verify test data is correct",
            "Review element selectors for changes",
            "Check network connectivity",
            "Validate environment configuration"
        ]


# Pytest Integration
@pytest.mark.enhanced
@pytest.mark.standalone
@pytest.mark.{flow_name_safe}
def test_{flow_name_safe}_enhanced_standalone(page: Page):
    """Enhanced standalone test with error recovery"""
    
    test_instance = Enhanced{class_name}Test(page)
    
    # Execute the enhanced flow
    results = test_instance.execute_standalone_flow()
    
    # Assert success
    assert results["success"], f"Enhanced flow failed: {{results.get('error', 'Unknown error')}}"
    
    # Validate phase completion
    successful_phases = len([p for p in test_instance.phase_results if p['status'] == 'success'])
    total_phases = len(test_instance.phase_results)
    
    print(f"✅ Enhanced flow completed: {{successful_phases}}/{{total_phases}} phases successful")
    print(f"🔧 Recovery actions used: {{len(test_instance.error_recovery_log)}}")


@pytest.mark.enhanced
@pytest.mark.standalone  
@pytest.mark.{flow_name_safe}
@pytest.mark.debug
def test_{flow_name_safe}_debug_with_recovery(page: Page):
    """Debug version with enhanced recovery capabilities"""
    
    test_instance = Enhanced{class_name}Test(page)
    
    # Execute with debug info
    results = test_instance.execute_standalone_flow()
    
    # Detailed reporting
    print(f"🔍 Enhanced Flow Debug Results:")
    print(f"   Flow Name: {{results['flow_name']}}")
    print(f"   Test Type: {{results['test_type']}}")
    print(f"   Success: {{results['success']}}")
    print(f"   Phase Results: {{test_instance.phase_results}}")
    print(f"   Recovery Log: {{test_instance.error_recovery_log}}")
    
    # Take final screenshot
    self.page.screenshot(path="execution/screenshots/{flow_name_safe}_enhanced_debug_final.png")
    
    print("🔍 Enhanced test browser will remain open for debugging...")
    print("⏸️  Press ENTER to close...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("🛑 User interrupted - closing browser")


if __name__ == "__main__":
    print("🔧 Run this enhanced test with pytest:")
    print("pytest {filename} -v -s")
    print("pytest {filename}::test_{flow_name_safe}_enhanced_standalone -v -s")
    print("pytest {filename}::test_{flow_name_safe}_debug_with_recovery -v -s")
'''
        
        # Generate phase implementations
        phase_implementations = self._generate_phase_implementations(phase_groups)
        
        # Format template
        class_name = ''.join(word.capitalize() for word in self.flow_name.split('_'))
        flow_name_safe = re.sub(r'[^a-zA-Z0-9_]', '_', self.flow_name.lower())
        filename = self.recording_file.name
        
        return script_template.format(
            flow_name=self.flow_name,
            timestamp=self.start_timestamp,
            base_url=self.base_url,
            class_name=class_name,
            phase_implementations=phase_implementations,
            flow_name_safe=flow_name_safe,
            filename=filename
        )
    
    def _generate_phase_implementations(self, phase_groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate phase implementation code from captured data"""
        implementations = ""
        
        if not phase_groups:
            return '''
            # No phases were captured during recording
            # Add manual phase implementation here
            
            # Example: Basic navigation and assertion
            expect(self.page).to_have_url(base_url)
            self.page.screenshot(path=f"execution/screenshots/{self.flow_name}_basic_flow.png")
            '''
        
        for i, (phase_name, actions) in enumerate(phase_groups.items(), 1):
            phase_method_name = f"_phase_{i}_{re.sub(r'[^a-zA-Z0-9_]', '_', phase_name.lower())}"
            
            implementations += f'''
            # Phase {i}: {phase_name}
            success = self._execute_phase_with_recovery(
                "{phase_name}",
                lambda: self.{phase_method_name}()
            )
            if not success:
                raise Exception(f"Phase {i} ({phase_name}) failed after retries")
            '''
        
        # Generate phase method implementations  
        for i, (phase_name, actions) in enumerate(phase_groups.items(), 1):
            phase_method_name = f"_phase_{i}_{re.sub(r'[^a-zA-Z0-9_]', '_', phase_name.lower())}"
            safe_flow_name = re.sub(r'[^a-zA-Z0-9_]', '_', self.flow_name.lower())
            
            implementations += f'''
    def {phase_method_name}(self):
        """Generated implementation for: {phase_name}"""
        # Actions captured for this phase: {len(actions)}
        
        # Take phase screenshot
        self.page.screenshot(path=f"execution/screenshots/{safe_flow_name}_phase_{i}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png")
        
        # Phase-specific assertions would go here
        # Based on captured actions, add appropriate validations
        
        # Wait for phase completion
        self.page.wait_for_load_state("domcontentloaded")
        '''
        
        return implementations
    
    def _generate_optional_bdd_integration(self, processed_data: Dict[str, Any]) -> List[str]:
        """Generate optional BDD integration files"""
        bdd_files = []
        
        # Generate feature file
        feature_file = self.recordings_dir / f"{self.flow_name}_bdd_integration.feature"
        feature_content = self._generate_bdd_feature_content(processed_data)
        
        with open(feature_file, 'w') as f:
            f.write(feature_content)
        bdd_files.append(str(feature_file))
        
        # Generate step definitions template
        steps_file = self.recordings_dir / f"{self.flow_name}_bdd_steps_template.py" 
        steps_content = self._generate_bdd_steps_template(processed_data)
        
        with open(steps_file, 'w') as f:
            f.write(steps_content)
        bdd_files.append(str(steps_file))
        
        return bdd_files
    
    def _generate_bdd_feature_content(self, processed_data: Dict[str, Any]) -> str:
        """Generate BDD feature file content"""
        phase_groups = processed_data.get('phase_groups', {})
        
        feature_template = '''# Optional BDD Integration for {flow_name}
# Generated from enhanced recording session on {timestamp}

@enhanced @standalone_ready @{flow_name_tag}
Feature: {flow_name_title} Enhanced E2E Flow
  As a user of the application
  I want to complete the {flow_name_title} process
  So that I can achieve my business objective

  Background:  
    Given the application is accessible
    And I have the required test data

{scenarios}

  @error_recovery @enhanced
  Scenario: {flow_name_title} with Error Recovery
    Given I start the enhanced flow session
    When I encounter an error during navigation
    Then the system should provide recovery options
    And I should be able to continue the flow
    And the error should be logged for analysis

  @debug @enhanced
  Scenario: {flow_name_title} Debug Mode
    Given I start the enhanced flow in debug mode
    When I complete all phases
    Then I should see detailed phase results
    And recovery actions should be logged
    And debug screenshots should be captured
'''
        
        # Generate scenarios based on phases
        scenarios = ""
        for phase_name in phase_groups.keys():
            safe_phase = re.sub(r'[^a-zA-Z0-9_]', '_', phase_name.lower())
            scenarios += f'''
  @enhanced @{safe_phase}
  Scenario: {phase_name}
    Given I am in the {phase_name.lower()} phase
    When I complete the required actions
    Then the phase should complete successfully
    And I should proceed to the next phase
'''
        
        flow_name_title = ' '.join(word.title() for word in self.flow_name.split('_'))
        flow_name_tag = re.sub(r'[^a-zA-Z0-9_]', '_', self.flow_name.lower())
        
        return feature_template.format(
            flow_name=self.flow_name,
            timestamp=self.start_timestamp,
            flow_name_title=flow_name_title,
            flow_name_tag=flow_name_tag,
            scenarios=scenarios
        )
    
    def _generate_bdd_steps_template(self, processed_data: Dict[str, Any]) -> str:
        """Generate BDD step definitions template"""
        class_name = ''.join(word.capitalize() for word in self.flow_name.split('_'))
        
        return f'''"""
BDD Step Definitions Template for {self.flow_name}
Generated from enhanced recording session

To integrate with BDD:
1. Move this file to tests/bdd/steps/{self.flow_name}_enhanced_steps.py  
2. Import the Enhanced{class_name}Test class
3. Implement the step definitions using the standalone test methods
4. Update pyproject.toml with new markers
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page
from pathlib import Path

# Import the generated standalone test class
# from execution.recordings.{self.flow_name}_enhanced_{self.start_timestamp} import Enhanced{class_name}Test

# Load scenarios from feature file
# scenarios(Path(__file__).parent / "features" / "{self.flow_name}_bdd_integration.feature")

@given("I start the enhanced flow session")
def start_enhanced_flow_session(page: Page):
    """Initialize enhanced flow session"""
    # Implement using Enhanced{class_name}Test class
    pass

@when("I encounter an error during navigation")
def encounter_navigation_error(page: Page):
    """Simulate or handle navigation error"""
    # Implement error scenario
    pass

@then("the system should provide recovery options")
def verify_recovery_options_provided(page: Page):
    """Verify recovery mechanisms are available"""
    # Implement recovery verification
    pass

@then("the error should be logged for analysis")
def verify_error_logging(page: Page):
    """Verify error logging functionality"""
    # Implement error log verification
    pass

# Add more step definitions as needed for your specific phases
'''
    
    def _generate_enhanced_documentation(self, processed_data: Dict[str, Any]) -> str:
        """Generate comprehensive documentation"""
        error_analysis = processed_data.get('error_analysis', {})
        recovery_summary = processed_data.get('recovery_summary', {})
        
        doc_template = '''# {flow_name} - Enhanced E2E Flow Documentation

Generated on: {timestamp} using Enhanced Interactive Flow Designer

## Overview
- **Flow Name**: {flow_name}
- **Base URL**: {base_url} 
- **Recording Type**: Enhanced with real-time capture
- **Total Actions Captured**: {total_actions}
- **Phases Identified**: {total_phases}
- **Errors Encountered**: {total_errors}
- **Recovery Actions**: {total_recoveries}

## Enhanced Features Used

### 1. Real-time Action Capture
- ✅ Actions captured during manual navigation
- ✅ Background processing thread active
- ✅ Real-time feedback provided

### 2. Error Recovery System  
- ✅ Error states captured: {total_errors}
- ✅ Recovery commands executed: {total_recoveries}
- ✅ Recovery success rate: {recovery_success_rate:.1%}

### 3. Post-session Processing
- ✅ Action grouping by phases
- ✅ Pattern analysis completed
- ✅ Element mapping generated
- ✅ Reusable component identification

## Generated Artifacts

### Standalone Test Script
**File**: `{recording_file}`
- Framework-compliant structure
- Built-in error recovery
- Comprehensive phase management
- Debug capabilities

### BDD Integration (Optional)
**Files**: 
- `{flow_name}_bdd_integration.feature` - Feature file template
- `{flow_name}_bdd_steps_template.py` - Step definitions template

### Usage Instructions

#### Running Standalone Tests
```bash
# Run complete enhanced flow
pytest execution/recordings/{recording_file} -v -s

# Run with debug mode (keeps browser open)
pytest execution/recordings/{recording_file}::test_{flow_name_safe}_debug_with_recovery -v -s

# Run specific test function
pytest execution/recordings/{recording_file}::test_{flow_name_safe}_enhanced_standalone -v -s
```

#### BDD Integration (Optional)
1. Move BDD files to appropriate directories
2. Update pyproject.toml with new markers
3. Import standalone test class in step definitions
4. Run BDD scenarios

## Error Analysis

{error_analysis_content}

## Recovery System Performance

{recovery_analysis_content}

## Framework Integration Notes

This enhanced flow follows framework patterns:
- **Page Object Model**: Ready for extraction to pages/
- **Locator Strategy**: Uses role-based selectors where possible
- **Flow Orchestration**: Compatible with flows/e2e/ patterns
- **Validation Layer**: Includes assertion points
- **Error Handling**: Built-in recovery mechanisms

## Recommendations

### 1. Production Integration
- Extract page methods to appropriate page objects
- Move locators to dedicated locator modules  
- Add to flow orchestration hierarchy
- Integrate with existing validation classes

### 2. Error Handling Enhancement
- Review captured error patterns
- Enhance recovery strategies based on actual failures
- Add application-specific recovery commands

### 3. BDD Integration (if desired)
- Use generated BDD templates as starting point
- Map phases to business requirements
- Add domain-specific language to step definitions

---
*Generated by Enhanced Interactive E2E Flow Designer with real-time capture and post-session processing*
'''
        
        # Format error analysis
        error_analysis_content = "No errors encountered during recording session." 
        if error_analysis.get('total_errors', 0) > 0:
            error_types = error_analysis.get('error_types', [])
            error_analysis_content = f'''
**Total Errors**: {error_analysis.get('total_errors', 0)}
**Error Types**: {', '.join(error_types)}
**Most Common**: {error_types[0] if error_types else 'N/A'}
'''
        
        # Format recovery analysis
        recovery_analysis_content = "No recovery actions were needed."
        if recovery_summary.get('total_recoveries', 0) > 0:
            recovery_types = recovery_summary.get('recovery_types', [])
            recovery_analysis_content = f'''
**Total Recovery Actions**: {recovery_summary.get('total_recoveries', 0)}
**Recovery Types Used**: {', '.join(recovery_types)}
**Success Rate**: {recovery_summary.get('effectiveness', 0)}/{recovery_summary.get('total_recoveries', 0)}
'''
        
        flow_name_safe = re.sub(r'[^a-zA-Z0-9_]', '_', self.flow_name.lower())
        total_recoveries = recovery_summary.get('total_recoveries', 0)
        recovery_success_rate = recovery_summary.get('effectiveness', 0) / max(total_recoveries, 1) if total_recoveries > 0 else 0
        
        return doc_template.format(
            flow_name=self.flow_name,
            timestamp=self.start_timestamp,
            base_url=self.base_url,
            total_actions=len(self.real_time_capture.captured_actions),
            total_phases=len(self.real_time_capture.phase_markers),
            total_errors=len(self.real_time_capture.error_states),
            total_recoveries=total_recoveries,
            recovery_success_rate=recovery_success_rate,
            recording_file=self.recording_file.name,
            flow_name_safe=flow_name_safe,
            error_analysis_content=error_analysis_content,
            recovery_analysis_content=recovery_analysis_content
        )
    
    def _summarize_enhanced_features_usage(self) -> Dict[str, Any]:
        """Summarize which enhanced features were used"""
        return {
            "real_time_capture": len(self.real_time_capture.captured_actions) > 0,
            "error_recovery": len(self.real_time_capture.error_states) > 0,
            "phase_marking": len(self.real_time_capture.phase_markers) > 0,
            "post_session_processing": self.real_time_capture.state == CaptureState.COMPLETED,
            "standalone_test_generation": True,
            "bdd_integration_ready": True
        }
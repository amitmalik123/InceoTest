"""
Enhanced Interactive Flow MCP Integration
Orchestrates MCP browser sessions with enhanced flow designer

This module provides the command-line interface and MCP session management
for the enhanced interactive flow designer with real-time capture capabilities.

Features:
- MCP browser session management
- Interactive command loop for flow design
- Enhanced capture coordination
- Error recovery command interface
- Post-session processing coordination
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import json
import signal
from datetime import datetime

# Import our enhanced flow designer
from .enhanced_interactive_flow_designer import EnhancedInteractiveE2EFlowDesigner, CaptureState


class EnhancedInteractiveFlowMCP:
    """Enhanced MCP session manager with real-time capture integration"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None  
        self.page: Optional[Page] = None
        self.flow_designer: Optional[EnhancedInteractiveE2EFlowDesigner] = None
        self.session_active = False
        self.playwright = None
        
        # Session configuration
        self.session_config = {
            "headless": False,  # Always visible for manual navigation
            "slow_mo": 500,     # Slow motion for better capture
            "viewport": {"width": 1280, "height": 720},
            "timeout": 30000    # 30s default timeout
        }
    
    def start_enhanced_mcp_session(self, flow_name: str, base_url: str, browser_type: str = "chromium") -> Dict[str, Any]:
        """Start enhanced MCP browser session"""
        try:
            print(f"🚀 Starting Enhanced Interactive Flow MCP Session")
            print(f"📝 Flow: {flow_name}")
            print(f"🌐 URL: {base_url}")
            print(f"🔧 Browser: {browser_type}")
            
            # Initialize Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser
            browser_launcher = getattr(self.playwright, browser_type)
            self.browser = browser_launcher.launch(**self.session_config)
            
            # Create context and page
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # Initialize enhanced flow designer
            self.flow_designer = EnhancedInteractiveE2EFlowDesigner(
                self.page, 
                self.context,
                flow_name,
                base_url
            )
            
            # Start enhanced recording session
            recording_result = self.flow_designer.start_enhanced_recording_session()
            
            self.session_active = True
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            print(f"✅ Enhanced MCP session ready!")
            print(f"📱 Browser is open - navigate manually")
            print(f"💻 Use interactive commands to control recording")
            
            return {
                "status": "enhanced_mcp_started",
                "session_active": True,
                "flow_name": flow_name,
                "base_url": base_url,
                "browser_type": browser_type,
                "recording_result": recording_result
            }
            
        except Exception as e:
            print(f"❌ Failed to start enhanced MCP session: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_interactive_command_loop(self) -> Dict[str, Any]:
        """Run interactive command loop with enhanced features"""
        if not self.session_active or not self.flow_designer:
            return {"status": "error", "message": "Session not active"}
        
        print(f"\n🎮 Enhanced Interactive Command Loop Active")
        self._display_enhanced_commands()
        
        session_results = {
            "commands_executed": [],
            "phases_completed": [],
            "errors_handled": [],
            "session_duration": 0
        }
        
        session_start = datetime.now()
        
        try:
            while self.session_active:
                try:
                    # Get user command
                    command_input = input("\n📝 Enhanced Flow Command > ").strip().lower()
                    
                    if not command_input:
                        continue
                    
                    # Process command
                    result = self._process_enhanced_command(command_input)
                    session_results["commands_executed"].append({
                        "command": command_input,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Check for session termination
                    if command_input in ['quit', 'exit', 'finish']:
                        break
                        
                except KeyboardInterrupt:
                    print(f"\n⚡ Keyboard interrupt received")
                    result = self._handle_interrupt()
                    if result.get('action') == 'exit':
                        break
                    
                except EOFError:
                    print(f"\n📝 Input stream ended")
                    break
                    
        except Exception as e:
            print(f"❌ Command loop error: {e}")
            session_results["error"] = str(e)
        
        finally:
            session_results["session_duration"] = (datetime.now() - session_start).total_seconds()
            print(f"⏱️ Session duration: {session_results['session_duration']:.1f}s")
        
        return session_results
    
    def _process_enhanced_command(self, command_input: str) -> Dict[str, Any]:
        """Process enhanced commands with error handling"""
        try:
            parts = command_input.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            # Enhanced command routing
            if command in ['help', 'h']:
                self._display_enhanced_commands()
                return {"status": "help_displayed"}
            
            elif command in ['status', 's']:
                return self._get_session_status()
            
            elif command in ['mark', 'm']:
                return self._handle_mark_phase_command(args)
            
            elif command in ['error', 'e']:
                return self._handle_error_command(args)
            
            elif command in ['recover', 'r']:
                return self._handle_recovery_command(args)
            
            elif command in ['capture', 'c']:
                return self._handle_capture_command(args)
            
            elif command in ['screenshot', 'ss']:
                return self._take_enhanced_screenshot(args)
            
            elif command in ['validate', 'v']:
                return self._handle_validation_command(args)
            
            elif command in ['debug', 'd']:
                return self._handle_debug_command(args)
            
            elif command in ['finish', 'f', 'complete']:
                return self._handle_finish_command(args)
            
            elif command in ['quit', 'q', 'exit']:
                return self._handle_quit_command()
            
            else:
                print(f"❓ Unknown command: {command}")
                print(f"💡 Type 'help' for available commands")
                return {"status": "unknown_command", "command": command}
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            return {"status": "command_error", "error": str(e)}
    
    def _handle_mark_phase_command(self, args: str) -> Dict[str, Any]:
        """Handle phase marking command"""
        if not args:
            print(f"❓ Usage: mark <phase_name> [description]")
            return {"status": "missing_args"}
        
        parts = args.split(maxsplit=1)
        phase_name = parts[0]
        description = parts[1] if len(parts) > 1 else f"Phase: {phase_name}"
        
        print(f"📋 Marking phase: {phase_name}")
        result = self.flow_designer.mark_phase(phase_name, description)
        
        if result.get('status') == 'phase_marked':
            print(f"✅ Phase '{phase_name}' marked successfully")
            if 'screenshot' in result:
                print(f"📸 Screenshot: {result['screenshot']}")
        else:
            print(f"❌ Failed to mark phase: {result.get('message', 'Unknown error')}")
        
        return result
    
    def _handle_error_command(self, args: str) -> Dict[str, Any]:
        """Handle error state command"""
        if not args:
            print(f"❓ Usage: error <description> [recovery_strategy]")
            return {"status": "missing_args"}
        
        parts = args.split(' | ')
        error_description = parts[0]
        recovery_strategy = parts[1] if len(parts) > 1 else None
        
        print(f"🚨 Handling error: {error_description}")
        result = self.flow_designer.handle_error(error_description, recovery_strategy)
        
        if result.get('status') == 'error_captured':
            print(f"✅ Error state captured")
            print(f"🔧 Recovery commands available:")
            for cmd in result.get('recovery_commands', []):
                print(f"   • {cmd}")
        else:
            print(f"❌ Failed to handle error: {result.get('message', 'Unknown error')}")
        
        return result
    
    def _handle_recovery_command(self, args: str) -> Dict[str, Any]:
        """Handle recovery command execution"""
        if not args:
            print(f"❓ Available recovery commands:")
            print(f"   • retry_last_action")
            print(f"   • navigate_back")
            print(f"   • refresh_page")
            print(f"   • wait_and_retry [wait_time]")
            print(f"   • reset_to_phase [phase_name]")
            print(f"   • custom_recovery [action]")
            return {"status": "recovery_help"}
        
        parts = args.split(maxsplit=1)
        command = parts[0]
        kwargs = {}
        
        # Parse command-specific arguments
        if command == "wait_and_retry" and len(parts) > 1:
            try:
                kwargs['wait_time'] = int(parts[1])
            except ValueError:
                print(f"❓ Invalid wait time: {parts[1]}")
                return {"status": "invalid_args"}
        elif command == "reset_to_phase" and len(parts) > 1:
            kwargs['phase_name'] = parts[1]
        elif command == "custom_recovery" and len(parts) > 1:
            kwargs['action'] = parts[1]
        
        print(f"🔧 Executing recovery: {command}")
        result = self.flow_designer.recover(command, **kwargs)
        
        if result.get('status') == 'recovery_executed':
            print(f"✅ Recovery completed: {command}")
            for action in result.get('recovery_actions', []):
                print(f"   ✓ {action}")
        else:
            print(f"❌ Recovery failed: {result.get('message', 'Unknown error')}")
        
        return result
    
    def _handle_capture_command(self, args: str) -> Dict[str, Any]:
        """Handle manual capture command"""
        if not args:
            print(f"❓ Usage: capture <action_type> <description> [element_selector]")
            print(f"   • Action types: click, fill, select, keyboard, assertion")
            return {"status": "missing_args"}
        
        parts = args.split(maxsplit=2)
        action_type = parts[0]
        description = parts[1] if len(parts) > 1 else ""
        element_selector = parts[2] if len(parts) > 2 else None
        
        print(f"📝 Manually capturing action: {action_type}")
        result = self.flow_designer.real_time_capture.capture_manual_action(
            action_type, description, element_selector
        )
        
        if result.get('status') == 'captured':
            print(f"✅ Action captured: {result['action_id']}")
        else:
            print(f"❌ Failed to capture action: {result.get('message', 'Unknown error')}")
        
        return result
    
    def _take_enhanced_screenshot(self, args: str) -> Dict[str, Any]:
        """Take screenshot with enhanced naming"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
            filename = args if args else f"enhanced_capture_{timestamp}"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            screenshot_path = Path("execution/screenshots") / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.page.screenshot(path=str(screenshot_path))
            
            print(f"📸 Screenshot saved: {screenshot_path}")
            return {"status": "screenshot_taken", "path": str(screenshot_path)}
            
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return {"status": "screenshot_error", "error": str(e)}
    
    def _handle_validation_command(self, args: str) -> Dict[str, Any]:
        """Handle validation command"""
        if not args:
            print(f"❓ Usage: validate <assertion_type> <expected_value>")
            print(f"   • url <expected_url>")
            print(f"   • title <expected_title>")
            print(f"   • element <selector> <expected_text>")
            return {"status": "missing_args"}
        
        parts = args.split(maxsplit=2)
        assertion_type = parts[0]
        
        try:
            if assertion_type == "url" and len(parts) > 1:
                expected_url = parts[1]
                current_url = self.page.url
                success = expected_url in current_url
                print(f"🔍 URL validation: {success}")
                print(f"   Expected: {expected_url}")
                print(f"   Current: {current_url}")
                
            elif assertion_type == "title" and len(parts) > 1:
                expected_title = parts[1]
                current_title = self.page.title()
                success = expected_title in current_title
                print(f"🔍 Title validation: {success}")
                print(f"   Expected: {expected_title}")
                print(f"   Current: {current_title}")
                
            elif assertion_type == "element" and len(parts) > 2:
                selector = parts[1]
                expected_text = parts[2]
                element = self.page.locator(selector)
                current_text = element.text_content() if element.count() > 0 else ""
                success = expected_text in current_text
                print(f"🔍 Element validation: {success}")
                print(f"   Selector: {selector}")
                print(f"   Expected: {expected_text}")
                print(f"   Current: {current_text}")
                
            else:
                print(f"❓ Invalid validation command: {args}")
                return {"status": "invalid_validation"}
            
            return {"status": "validation_complete", "success": success}
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return {"status": "validation_error", "error": str(e)}
    
    def _handle_debug_command(self, args: str) -> Dict[str, Any]:
        """Handle debug command"""
        if not args:
            args = "info"
        
        try:
            if args == "info":
                status = self._get_session_status()
                print(f"🔍 Debug Info:")
                print(f"   Session Active: {status['session_active']}")
                print(f"   Capture State: {status.get('capture_state', 'Unknown')}")
                print(f"   Actions Captured: {status.get('actions_captured', 0)}")
                print(f"   Phases Marked: {status.get('phases_marked', 0)}")
                print(f"   Errors Encountered: {status.get('errors_encountered', 0)}")
                
            elif args == "actions":
                actions = self.flow_designer.real_time_capture.captured_actions
                print(f"🔍 Captured Actions ({len(actions)}):")
                for i, action in enumerate(actions[-10:], 1):  # Show last 10
                    print(f"   {i}. {action.action_type.value} - {action.user_input or 'Auto-captured'}")
                
            elif args == "errors":
                errors = self.flow_designer.real_time_capture.error_states
                print(f"🔍 Error States ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    print(f"   {i}. {error.get('error_description', 'Unknown error')}")
                
            elif args == "phases":
                phases = self.flow_designer.real_time_capture.phase_markers
                print(f"🔍 Phase Markers ({len(phases)}):")
                for i, phase in enumerate(phases, 1):
                    print(f"   {i}. {phase.get('phase_name', 'Unknown')} - {phase.get('description', '')}")
            
            return {"status": "debug_complete", "debug_type": args}
            
        except Exception as e:
            print(f"❌ Debug error: {e}")
            return {"status": "debug_error", "error": str(e)}
    
    def _handle_finish_command(self, args: str) -> Dict[str, Any]:
        """Handle finish/complete command"""
        print(f"🏁 Finalizing enhanced recording session...")
        
        try:
            # Get final description
            final_description = args if args else "Enhanced recording session completed"
            
            # Finalize recording
            result = self.flow_designer.finalize_enhanced_recording(final_description)
            
            if result.get('status') == 'enhanced_recording_complete':
                print(f"✅ Enhanced recording completed successfully!")
                print(f"📄 Standalone Test: {result['standalone_test']}")
                print(f"📚 Documentation: {result['documentation']}")
                
                if result.get('bdd_integration'):
                    print(f"🎯 BDD Integration Files:")
                    for bdd_file in result['bdd_integration']:
                        print(f"   • {bdd_file}")
                
                # Display summary
                summary = result.get('processing_summary', {})
                print(f"📊 Session Summary:")
                print(f"   • Total Actions: {summary.get('total_actions', 0)}")
                print(f"   • Phases Marked: {summary.get('phases_marked', 0)}")
                print(f"   • Errors Handled: {summary.get('errors_encountered', 0)}")
                
            else:
                print(f"❌ Failed to finalize recording: {result.get('message', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to finish session: {e}")
            return {"status": "finish_error", "error": str(e)}
    
    def _handle_quit_command(self) -> Dict[str, Any]:
        """Handle quit command"""
        print(f"🛑 Quitting enhanced session...")
        
        try:
            # Check if recording is active
            if (self.flow_designer and 
                self.flow_designer.real_time_capture.state == CaptureState.RECORDING):
                
                print(f"⚠️ Recording is still active. Finalizing first...")
                finalize_result = self._handle_finish_command("Session terminated by user")
                
                if finalize_result.get('status') != 'enhanced_recording_complete':
                    print(f"⚠️ Warning: Recording may not have been properly finalized")
            
            # Stop session
            self.session_active = False
            
            return {"status": "session_terminated", "action": "exit"}
            
        except Exception as e:
            print(f"❌ Error during quit: {e}")
            self.session_active = False
            return {"status": "quit_error", "error": str(e), "action": "exit"}
    
    def _get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        status = {
            "session_active": self.session_active,
            "browser_active": self.browser is not None,
            "page_active": self.page is not None,
            "flow_designer_active": self.flow_designer is not None
        }
        
        if self.flow_designer:
            capture = self.flow_designer.real_time_capture
            status.update({
                "capture_state": capture.state.value,
                "actions_captured": len(capture.captured_actions),
                "phases_marked": len(capture.phase_markers),
                "errors_encountered": len(capture.error_states),
                "current_url": self.page.url if self.page else "N/A"
            })
        
        return status
    
    def _display_enhanced_commands(self):
        """Display available enhanced commands"""
        commands = [
            ("help, h", "Show this help message"),
            ("status, s", "Show current session status"),
            ("mark, m <name> [desc]", "Mark phase completion"),
            ("error, e <desc> [strategy]", "Handle error state"),
            ("recover, r <command> [args]", "Execute recovery command"),
            ("capture, c <type> <desc> [sel]", "Manual action capture"),
            ("screenshot, ss [name]", "Take screenshot"),
            ("validate, v <type> <expected>", "Validate current state"),
            ("debug, d [info|actions|errors|phases]", "Show debug information"),
            ("finish, f [description]", "Finalize and generate test"),
            ("quit, q", "Quit session (will finalize if needed)")
        ]
        
        print(f"\n🎮 Enhanced Interactive Commands:")
        print(f"{'='*50}")
        for cmd, desc in commands:
            print(f"  {cmd:<25} {desc}")
        print(f"{'='*50}")
        
        print(f"\n✨ Enhanced Features Active:")
        print(f"  • Real-time action capture")
        print(f"  • Error recovery system")
        print(f"  • Phase marking with screenshots")
        print(f"  • Post-session processing")
        print(f"  • Standalone test generation")
        print(f"  • Optional BDD integration")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals gracefully"""
        print(f"\n⚡ Signal {signum} received - shutting down gracefully...")
        self.session_active = False
        
        if self.flow_designer:
            try:
                self._handle_finish_command("Session interrupted by signal")
            except:
                print(f"⚠️ Could not finalize recording due to signal interrupt")
        
        self._cleanup_session()
        sys.exit(0)
    
    def _handle_interrupt(self) -> Dict[str, Any]:
        """Handle keyboard interrupt"""
        print(f"\n⚡ Keyboard interrupt received")
        print(f"Options:")
        print(f"  1. Continue session (c)")
        print(f"  2. Finalize and quit (f)")
        print(f"  3. Force quit (q)")
        
        try:
            choice = input("Choose option (c/f/q): ").strip().lower()
            
            if choice == 'c':
                print(f"📝 Continuing session...")
                return {"status": "continue"}
            elif choice == 'f':
                print(f"🏁 Finalizing session...")
                self._handle_finish_command("Session interrupted - finalizing")
                return {"status": "finalized", "action": "exit"}
            else:
                print(f"🛑 Force quitting...")
                return {"status": "force_quit", "action": "exit"}
                
        except (KeyboardInterrupt, EOFError):
            print(f"🛑 Force quitting due to repeated interrupts...")
            return {"status": "force_quit", "action": "exit"}
    
    def _cleanup_session(self):
        """Clean up session resources"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
                
            print(f"🧹 Session cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error (non-critical): {e}")
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if self.session_active:
            self._cleanup_session()


def main():
    """Main CLI entry point for enhanced interactive flow MCP"""
    parser = argparse.ArgumentParser(
        description="Enhanced Interactive E2E Flow Designer with Playwright MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utils.enhanced_interactive_flow_mcp --flow login_flow --url https://app.example.com/login
  python -m utils.enhanced_interactive_flow_mcp --flow journal_transfer --url https://ewm.test11.com --browser firefox
  python -m utils.enhanced_interactive_flow_mcp --flow user_registration --url https://app.qa.com/register --help-commands

Enhanced Features:
  • Real-time action capture during manual navigation
  • Error recovery system with multiple strategies  
  • Phase marking with automatic screenshots
  • Post-session processing and pattern analysis
  • Standalone test generation with built-in recovery
  • Optional BDD integration templates
        """
    )
    
    parser.add_argument(
        "--flow", "-f",
        required=True,
        help="Name of the flow to design (e.g., 'login_flow', 'journal_transfer')"
    )
    
    parser.add_argument(
        "--url", "-u", 
        required=True,
        help="Base URL to start the flow from"
    )
    
    parser.add_argument(
        "--browser", "-b",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser engine to use (default: chromium)"
    )
    
    parser.add_argument(
        "--help-commands",
        action="store_true",
        help="Show detailed command help and exit"
    )
    
    args = parser.parse_args()
    
    if args.help_commands:
        print("""
Enhanced Interactive Flow MCP - Command Reference

Session Management:
  help (h)                     - Show command help
  status (s)                   - Display session status
  quit (q)                     - Quit session (auto-finalizes)

Flow Recording:
  mark (m) <name> [desc]       - Mark phase completion with screenshot
                                 Example: mark "login_phase" "User login completed"
  
  capture (c) <type> <desc>    - Manually capture action
                                 Types: click, fill, select, keyboard, assertion
                                 Example: capture click "Submit login form"

Error Handling:
  error (e) <description>      - Handle unexpected state/error
                                 Example: error "Login form not visible"
  
  recover (r) <command>        - Execute recovery action
                                 Commands: retry_last_action, navigate_back,
                                          refresh_page, wait_and_retry,
                                          reset_to_phase, custom_recovery

Validation & Debug:
  validate (v) <type> <value>  - Validate current state
                                 Types: url, title, element
                                 Example: validate url "/dashboard"
  
  screenshot (ss) [filename]   - Take screenshot with custom name
  
  debug (d) [type]             - Show debug information
                                 Types: info, actions, errors, phases

Session Completion:
  finish (f) [description]     - Finalize recording and generate test files
  
Interactive Workflow:
1. Start session: python -m utils.enhanced_interactive_flow_mcp --flow my_flow --url https://site.com
2. Navigate manually in the opened browser (actions captured automatically)
3. Use 'mark' commands to define phases: mark "login_complete" 
4. Use 'error' and 'recover' if issues occur
5. Use 'finish' to generate the final test files
6. Generated files will be in execution/recordings/
        """)
        return
    
    # Initialize and start enhanced MCP session
    mcp_session = EnhancedInteractiveFlowMCP()
    
    try:
        print(f"🚀 Enhanced Interactive E2E Flow Designer")
        print(f"✨ Features: Real-time capture, Error recovery, Post-session processing")
        print(f"={'='*60}")
        
        # Start MCP session
        session_result = mcp_session.start_enhanced_mcp_session(
            flow_name=args.flow,
            base_url=args.url,
            browser_type=args.browser
        )
        
        if session_result.get('status') != 'enhanced_mcp_started':
            print(f"❌ Failed to start session: {session_result.get('message', 'Unknown error')}")
            return
        
        # Run interactive command loop
        loop_result = mcp_session.run_interactive_command_loop()
        
        print(f"\n📊 Session Results:")
        print(f"   Commands Executed: {len(loop_result.get('commands_executed', []))}")
        print(f"   Session Duration: {loop_result.get('session_duration', 0):.1f}s")
        
        if 'error' in loop_result:
            print(f"   Session Error: {loop_result['error']}")
        
    except KeyboardInterrupt:
        print(f"\n⚡ Session interrupted by user")
        
    except Exception as e:
        print(f"❌ Session error: {e}")
        
    finally:
        # Ensure cleanup
        mcp_session._cleanup_session()
        print(f"👋 Enhanced MCP session ended")


if __name__ == "__main__":
    main()
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, TextArea
from textual.worker import Worker, get_current_worker
from textual import events
import asyncio
import subprocess
import sys
from pathlib import Path


class DebugScreen(Screen):
    """Debug screen with mypy and pydantic check buttons and results display."""
    
    CSS = """
    #debug-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    #debug-content {
        width: 90%;
        height: 90%;
        align: center middle;
    }
    
    #debug-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 2;
    }
    
    #debug-subtitle {
        text-align: center;
        margin: 1;
    }
    
    #debug-buttons {
        align: center middle;
        height: auto;
        margin: 2;
    }
    
    #mypy-btn, #pydantic-btn, #clear-btn, #back-btn {
        margin: 1;
        min-width: 15;
    }
    
    #status-message {
        text-align: center;
        margin: 1;
    }
    
    #debug-results {
        height: 25;
        margin: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="debug-container"):
            with Vertical(id="debug-content"):
                yield Static("Debug Commands", id="debug-title")
                yield Static("Run code quality checks:", id="debug-subtitle")
                with Horizontal(id="debug-buttons"):
                    yield Button("MyPy Check", id="mypy-btn", variant="primary")
                    yield Button("Pydantic Check", id="pydantic-btn", variant="default")
                    yield Button("Clear Results", id="clear-btn", variant="default")
                    yield Button("Back", id="back-btn", variant="default")
                yield Static("", id="status-message")
                yield TextArea("", id="debug-results", read_only=True)
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen on mount."""
        self.update_status("Select a command to run", "info")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "mypy-btn":
            self.run_mypy_check()
        elif event.button.id == "pydantic-btn":
            self.run_pydantic_check()
        elif event.button.id == "clear-btn":
            self.clear_results()
        elif event.button.id == "back-btn":
            self.app.pop_screen()

    def run_mypy_check(self) -> None:
        """Run mypy type checking."""
        mypy_btn = self.query_one("#mypy-btn", Button)
        mypy_btn.disabled = True
        mypy_btn.text = "Running..."
        
        self.update_status("Running MyPy type check...", "info")
        
        # Start mypy check in a worker
        self.mypy_worker = self.run_worker(
            self.execute_mypy_check(),
            name="mypy_check"
        )

    def run_pydantic_check(self) -> None:
        """Run pydantic validation check."""
        pydantic_btn = self.query_one("#pydantic-btn", Button)
        pydantic_btn.disabled = True
        pydantic_btn.text = "Running..."
        
        self.update_status("Running Pydantic validation check...", "info")
        
        # Start pydantic check in a worker
        self.pydantic_worker = self.run_worker(
            self.execute_pydantic_check(),
            name="pydantic_check"
        )

    async def execute_mypy_check(self) -> None:
        """Execute mypy check in a worker thread."""
        worker = get_current_worker()
        
        try:
            # Run mypy command
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._run_mypy_command
            )
            
            if not worker.is_cancelled:
                self.call_from_thread(self.display_mypy_results, result)
                
        except Exception as e:
            if not worker.is_cancelled:
                self.call_from_thread(self.handle_debug_error, "mypy", str(e))

    async def execute_pydantic_check(self) -> None:
        """Execute pydantic check in a worker thread."""
        worker = get_current_worker()
        
        try:
            # Run pydantic validation
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._run_pydantic_check
            )
            
            if not worker.is_cancelled:
                self.call_from_thread(self.display_pydantic_results, result)
                
        except Exception as e:
            if not worker.is_cancelled:
                self.call_from_thread(self.handle_debug_error, "pydantic", str(e))

    def _run_mypy_command(self) -> tuple[str, str, int]:
        """Run mypy command and return stdout, stderr, and return code."""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent
            
            # Run mypy on the project
            result = subprocess.run(
                [sys.executable, "-m", "mypy", str(project_root)],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            return result.stdout, result.stderr, result.returncode
            
        except Exception as e:
            return "", str(e), 1

    def _run_pydantic_check(self) -> tuple[str, str, int]:
        """Run pydantic validation check."""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent
            
            # Create a simple pydantic validation script
            pydantic_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

try:
    from weather.types import WeatherResult, HourlyData, HourlyUnits
    from weather.location import get_longitude_and_latitude_for_address
    from weather.run import run_weather_request
    
    # Test basic imports and model creation
    print("✓ Pydantic models imported successfully")
    
    # Test model creation with sample data
    sample_data = {
        "hourly": {
            "temperature_2m": [72.5, 75.0, 78.2],
            "time": ["2024-01-01T00:00", "2024-01-01T01:00", "2024-01-01T02:00"]
        },
        "hourly_units": {
            "temperature_2m": "°F",
            "time": "iso8601"
        },
        "elevation": 100.0,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "timezone_abbreviation": "EST",
        "utc_offset_seconds": -18000,
        "generationtime_ms": 0.123
    }
    
    weather_result = WeatherResult(**sample_data)
    print("✓ WeatherResult model validation successful")
    print(f"  - Temperature data: {len(weather_result.hourly.temperature_2m)} entries")
    print(f"  - Location: {weather_result.latitude}, {weather_result.longitude}")
    print(f"  - Timezone: {weather_result.timezone}")
    
    print("\\n✓ All Pydantic validations passed!")
    return "", "", 0
    
except Exception as e:
    print(f"✗ Pydantic validation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    return "", str(e), 1
"""
            
            # Write and run the script
            script_path = project_root / "temp_pydantic_check.py"
            with open(script_path, "w") as f:
                f.write(pydantic_script)
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Clean up
            script_path.unlink(missing_ok=True)
            
            return result.stdout, result.stderr, result.returncode
            
        except Exception as e:
            return "", str(e), 1

    def display_mypy_results(self, result: tuple[str, str, int]) -> None:
        """Display mypy check results."""
        stdout, stderr, returncode = result
        
        # Re-enable mypy button
        mypy_btn = self.query_one("#mypy-btn", Button)
        mypy_btn.disabled = False
        mypy_btn.text = "MyPy Check"
        
        # Format results
        if returncode == 0:
            self.update_status("MyPy check completed successfully!", "success")
            results_text = "MyPy Type Check Results:\n" + "="*50 + "\n\n"
            if stdout:
                results_text += "✓ No type errors found!\n\n"
                results_text += stdout
            else:
                results_text += "✓ No type errors found!"
        else:
            self.update_status("MyPy check found issues", "warning")
            results_text = "MyPy Type Check Results:\n" + "="*50 + "\n\n"
            if stdout:
                results_text += stdout
            if stderr:
                results_text += "\nErrors:\n" + stderr
        
        # Update the text area
        text_area = self.query_one("#debug-results", TextArea)
        text_area.text = results_text

    def display_pydantic_results(self, result: tuple[str, str, int]) -> None:
        """Display pydantic check results."""
        stdout, stderr, returncode = result
        
        # Re-enable pydantic button
        pydantic_btn = self.query_one("#pydantic-btn", Button)
        pydantic_btn.disabled = False
        pydantic_btn.text = "Pydantic Check"
        
        # Format results
        if returncode == 0:
            self.update_status("Pydantic validation completed successfully!", "success")
            results_text = "Pydantic Validation Results:\n" + "="*50 + "\n\n"
            results_text += stdout
        else:
            self.update_status("Pydantic validation found issues", "error")
            results_text = "Pydantic Validation Results:\n" + "="*50 + "\n\n"
            if stdout:
                results_text += stdout
            if stderr:
                results_text += "\nErrors:\n" + stderr
        
        # Update the text area
        text_area = self.query_one("#debug-results", TextArea)
        text_area.text = results_text

    def handle_debug_error(self, command: str, error_message: str) -> None:
        """Handle debug command errors."""
        # Re-enable appropriate button
        if command == "mypy":
            mypy_btn = self.query_one("#mypy-btn", Button)
            mypy_btn.disabled = False
            mypy_btn.text = "MyPy Check"
        elif command == "pydantic":
            pydantic_btn = self.query_one("#pydantic-btn", Button)
            pydantic_btn.disabled = False
            pydantic_btn.text = "Pydantic Check"
        
        self.update_status(f"{command.title()} error: {error_message}", "error")
        
        # Update results
        text_area = self.query_one("#debug-results", TextArea)
        text_area.text = f"Error running {command}:\n{error_message}"

    def clear_results(self) -> None:
        """Clear the results text area."""
        text_area = self.query_one("#debug-results", TextArea)
        text_area.text = ""
        self.update_status("Results cleared", "info")

    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update the status message."""
        status_widget = self.query_one("#status-message", Static)
        status_widget.text = message
        
        # Update styling based on status type
        if status_type == "error":
            status_widget.styles.color = "red"
        elif status_type == "success":
            status_widget.styles.color = "green"
        elif status_type == "warning":
            status_widget.styles.color = "yellow"
        else:
            status_widget.styles.color = "blue"

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.app.pop_screen()

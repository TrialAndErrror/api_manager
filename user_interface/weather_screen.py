from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static, TextArea
from textual.worker import Worker, get_current_worker
from textual import events
import asyncio
from typing import Optional

from weather.run import run_weather_request, show_graph


class WeatherScreen(Screen):
    """Weather screen with location input and weather fetching functionality."""
    
    CSS = """
    #weather-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    #weather-content {
        width: 80%;
        height: 90%;
        align: center middle;
    }
    
    #weather-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 2;
    }
    
    #location-label {
        margin: 1;
    }
    
    #location-input {
        margin: 1;
    }
    
    #weather-buttons {
        align: center middle;
        height: auto;
        margin: 2;
    }
    
    #submit-btn, #back-btn {
        margin: 1;
        min-width: 15;
    }
    
    #status-message {
        text-align: center;
        margin: 1;
    }
    
    #weather-results {
        height: 20;
        margin: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="weather-container"):
            with Vertical(id="weather-content"):
                yield Static("Weather Command", id="weather-title")
                yield Label("Enter location:", id="location-label")
                yield Input(placeholder="e.g., New York, NY or 123 Main St, City", id="location-input")
                with Horizontal(id="weather-buttons"):
                    yield Button("Submit", id="submit-btn", variant="primary")
                    yield Button("Back", id="back-btn", variant="default")
                yield Static("", id="status-message")
                yield TextArea("", id="weather-results", read_only=True)
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen on mount."""
        self.query_one("#location-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "submit-btn":
            self.submit_weather_request()
        elif event.button.id == "back-btn":
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key press in input field."""
        if event.input.id == "location-input":
            self.submit_weather_request()

    def submit_weather_request(self) -> None:
        """Submit the weather request."""
        location_input = self.query_one("#location-input", Input)
        location = location_input.value.strip()
        
        if not location:
            self.update_status("Please enter a location", "error")
            return
        
        # Disable submit button and show loading
        submit_btn = self.query_one("#submit-btn", Button)
        submit_btn.disabled = True
        submit_btn.text = "Loading..."
        
        self.update_status("Fetching weather data...", "info")
        
        # Start the weather request in a worker
        self.weather_worker = self.run_worker(
            self.fetch_weather_data(location),
            name="weather_fetch"
        )

    async def fetch_weather_data(self, location: str) -> None:
        """Fetch weather data in a worker thread."""
        worker = get_current_worker()
        
        try:
            # Run the weather request in a thread pool
            weather_result = await asyncio.get_event_loop().run_in_executor(
                None, run_weather_request, location
            )
            
            if not worker.is_cancelled:
                # Update UI with results
                self.call_from_thread(self.display_weather_results, weather_result, location)
                
        except Exception as e:
            if not worker.is_cancelled:
                self.call_from_thread(self.handle_weather_error, str(e))

    def display_weather_results(self, weather_result, location: str) -> None:
        """Display weather results in the UI."""
        # Re-enable submit button
        submit_btn = self.query_one("#submit-btn", Button)
        submit_btn.disabled = False
        submit_btn.text = "Submit"
        
        # Format weather data
        hourly = weather_result.hourly
        temps = hourly.temperature_2m
        times = hourly.time
        
        # Get current temperature (first entry)
        current_temp = temps[0] if temps else "N/A"
        
        # Create results text
        results_text = f"""Weather for: {location}
Current Temperature: {current_temp}°F
Timezone: {weather_result.timezone}
Elevation: {weather_result.elevation}m
Latitude: {weather_result.latitude}
Longitude: {weather_result.longitude}

Temperature Forecast (next 24 hours):
"""
        
        # Add hourly forecast (limit to 24 hours)
        for i, (time, temp) in enumerate(zip(times[:24], temps[:24])):
            results_text += f"{time.strftime('%Y-%m-%d %H:%M')}: {temp}°F\n"
        
        # Update the text area
        text_area = self.query_one("#weather-results", TextArea)
        text_area.text = results_text
        
        self.update_status("Weather data fetched successfully! Showing graph...", "success")
        
        # Show the matplotlib graph
        try:
            show_graph(times[:24], temps[:24], location)
        except Exception as e:
            self.update_status(f"Graph display error: {str(e)}", "warning")

    def handle_weather_error(self, error_message: str) -> None:
        """Handle weather request errors."""
        # Re-enable submit button
        submit_btn = self.query_one("#submit-btn", Button)
        submit_btn.disabled = False
        submit_btn.text = "Submit"
        
        self.update_status(f"Error: {error_message}", "error")
        
        # Clear results
        text_area = self.query_one("#weather-results", TextArea)
        text_area.text = ""

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

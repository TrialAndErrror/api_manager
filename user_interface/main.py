from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static
from textual.screen import Screen
from textual import events

from .weather_screen import WeatherScreen
from .debug_screen import DebugScreen


class MainScreen(Screen):
    """Main screen with weather and debug command buttons."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="main-content"):
                yield Static("API Manager", id="title")
                yield Static("Select a command:", id="subtitle")
                with Horizontal(id="button-container"):
                    yield Button("Weather", id="weather-btn", variant="primary")
                    yield Button("Debug", id="debug-btn", variant="default")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "weather-btn":
            self.app.push_screen(WeatherScreen())
        elif event.button.id == "debug-btn":
            self.app.push_screen(DebugScreen())


class APIManagerApp(App):
    """Main application class."""
    
    CSS = """
    #main-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    #main-content {
        align: center middle;
        width: 50%;
        height: 50%;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 2;
    }
    
    #subtitle {
        text-align: center;
        margin: 1;
    }
    
    #button-container {
        align: center middle;
        height: auto;
    }
    
    #weather-btn, #debug-btn {
        margin: 2;
        min-width: 20;
    }
    """
    
    def on_mount(self) -> None:
        """Set up the app on mount."""
        self.title = "API Manager"
        self.sub_title = "Command Interface"
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield MainScreen()


def run_ui() -> None:
    """Run the Textual UI application."""
    app = APIManagerApp()
    app.run()


if __name__ == "__main__":
    run_ui()

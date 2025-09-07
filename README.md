# API Manager - Type-Safe API Integrations

A Python application that demonstrates modern Python development practices using **Pydantic** for data validation, **MyPy** for static type checking, and clean architecture patterns.
The primary API integration in this project fetches weather forecast data from the Open-Meteo API and visualizes it using matplotlib.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Understanding Pydantic](#understanding-pydantic)
- [Understanding MyPy](#understanding-mypy)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Code Walkthrough](#code-walkthrough)
- [Development Best Practices](#development-best-practices)

## Overview

This application demonstrates how to build a robust Python application using:

- **Pydantic**: For data validation and serialization
- **MyPy**: For static type checking and improved code quality
- **Clean Architecture**: Modular design with separation of concerns
- **External APIs**: Integration with weather and geocoding services

The app takes a location (address or city), geocodes it to get coordinates, fetches weather forecast data, and displays a temperature graph.

## Features

- 🌍 **Geocoding**: Convert addresses to coordinates using OpenStreetMap
- 🌤️ **Weather Data**: Fetch hourly temperature forecasts from Open-Meteo API
- 📊 **Data Visualization**: Generate temperature graphs using matplotlib
- ✅ **Data Validation**: Robust data validation using Pydantic models
- 🔍 **Type Safety**: Static type checking with MyPy
- 🏗️ **Clean Architecture**: Modular, maintainable code structure

## Technology Stack

- **Python 3.10+**: Modern Python with type hints
- **Pydantic 2.11+**: Data validation and settings management
- **MyPy 1.17+**: Static type checker
- **Requests**: HTTP client for API calls
- **Geopy**: Geocoding library
- **Matplotlib**: Data visualization
- **UV**: Fast Python package manager

## Understanding Pydantic

Pydantic is a data validation library that uses Python type annotations to validate data. It's particularly powerful for API development, configuration management, and data serialization.

### Key Benefits

1. **Automatic Validation**: Validates data based on type hints
2. **Clear Error Messages**: Detailed validation error reporting
3. **Serialization**: Convert between Python objects and JSON/dict
4. **IDE Support**: Better autocomplete and type checking
5. **Performance**: Fast validation using Rust-based core

### Pydantic in This Project

Let's examine how Pydantic is used in our weather application:

```python
# weather/types.py
from datetime import datetime
from pydantic import BaseModel, Field

class HourlyData(BaseModel):
    temperature_2m: list[float]
    time: list[datetime]

class HourlyUnits(BaseModel):
    temperature_2m: str
    time: str

class WeatherResult(BaseModel):
    hourly: HourlyData
    hourly_units: HourlyUnits
    elevation: float
    latitude: float
    longitude: float
    timezone: str
    timezone_abbreviation: str
    utc_offset_seconds: int
    generationtime_ms: float
```
### Key Benefits

1. **Automatic Validation**: Validates data based on type hints
2. **Clear Error Messages**: Detailed validation error reporting
3. **Serialization**: Convert between Python objects and JSON/dict
4. **IDE Support**: Better autocomplete and type checking
5. **Performance**: Fast validation using Rust-based core

### Why use Pydantic?

Using BaseModel enables Pydantic support on the classes. Pydantic will look at the type annotations listed in the class definition and uses those types to validate the data that is used to instantiate the class.
I chose to use Pydantic because the JSON data coming from the API responses only contains distinctions between numbers and strings, and I wanted more type safety on the incoming data so that an exception would be raised if the data comes over in the wrong shape.
If we receive invalid data, or the response from the API changes over time, we want to know right away so that we can halt the erroneous ingest and prevent invalid data from being processed the same way valid data is.
Once we get an alert that the data is invalid, we can make the adjustments to the ingest process, so any data that gets passed along is guaranteed to be as safe and expected as possible.

### Example Usage

```python
# This will automatically validate the API response
data = response.json()
weather_result = WeatherResult(**data)  # Validates and creates object

# If data is invalid, Pydantic raises ValidationError with details
try:
    invalid_data = {"hourly": "not a dict"}
    WeatherResult(**invalid_data)
except ValidationError as e:
    print(e)  # Clear error message about what's wrong
```

## Understanding MyPy

MyPy is a static type checker for Python that helps catch type-related errors before runtime. It analyzes your code and reports potential issues based on type annotations.

### Key Benefits

1. **Early Error Detection**: Catch type errors before running code
2. **Better IDE Support**: Enhanced autocomplete and refactoring
3. **Documentation**: Type hints serve as inline documentation
4. **Refactoring Safety**: Safer code changes with type checking
5. **Team Collaboration**: Clearer interfaces between modules


### Why use MyPy?
I chose to use MyPy because I want to ensure that there are no edge cases with any functions that could lead to unexpected behavior. This ingest process has to be set up in a way that it could be run unsupervised, and so we want to anticipate any unexpected behaviors ahead of time during the development process and make sure that the typehints and return types make sense when functionality is combined.
Furthermore, if other team members are working on this project, I want them to be sure that any functions that I write are compatible with the code that they write, and that they are not creating any unforeseen outcomes due to a lack of understanding or misuse of my code.
Finally, just like with Pydantic, we want more checks that we can run to make sure that everything is working during the development process.

### MyPy in This Project

Our project uses type hints throughout:

```python
# weather/location.py
def get_longitude_and_latitude_for_address(address: str) -> tuple[float, float]:
    geolocator = Nominatim(user_agent="api_manager_location")
    location = geolocator.geocode(query=address)
    
    if not location:
        raise Exception("Could not find coordinates for address")
    
    return location.latitude, location.longitude
```

### Example Type Annotations

- `address: str` - Parameter must be a string
- `-> tuple[float, float]` - Function returns a tuple of two floats
- `list[datetime]` - List containing datetime objects
- `Optional[str]` - String or None (if imported from typing)

### Running MyPy

```bash
# Check all files
mypy .

# Check specific file
mypy weather/types.py

# Strict mode (recommended for new projects)
mypy --strict .
```

## Project Structure

```
api_manager/
├── main.py                 # Application entry point
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Locked dependency versions
├── README.md             # This file
└── weather/              # Weather module
    ├── __init__.py       # Module initialization
    ├── types.py          # Pydantic data models
    ├── location.py       # Geocoding functionality
    └── run.py            # Main weather logic and visualization
```

### Module Breakdown

#### `main.py` - Application Entry Point
- Imports and orchestrates the weather application
- Contains the main execution logic

#### `weather/types.py` - Data Models
- Defines Pydantic models for weather data
- `WeatherResult`: Main model for API response
- `HourlyData`: Hourly weather information
- `HourlyUnits`: Units for measurements

#### `weather/location.py` - Geocoding
- Converts addresses to latitude/longitude coordinates
- Uses OpenStreetMap's Nominatim service via Geopy
- Handles geocoding failures gracefully

#### `weather/run.py` - Core Logic
- Fetches weather data from Open-Meteo API
- Creates data visualization using matplotlib
- Orchestrates the entire weather request flow

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
git clone <your-repo-url>
cd api_manager

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

### Verify Installation

```bash
# Run the application
python main.py

# Run type checking
mypy .

# Check for any linting issues
python -m flake8 .  # If you have flake8 installed
```

## Usage

### Basic Usage

With UV:
```bash
uv run main.py
```

Without UV:
```bash
python main.py
```

This will:
1. Prompt the user for an address 
2. Geocode the address to get coordinates
3. Fetch 7-day weather forecast from Open-Meteo API
4. Display a temperature graph

### Programmatic Usage

```python
from weather.run import run_weather_request, show_graph

# Get weather data
result = run_weather_request("Paris, France")

# Display the graph
show_graph(
    times=result.hourly.time,
    temps=result.hourly.temperature_2m,
    location="Paris, France"
)
```

## Code Walkthrough

### 1. Data Flow

```
User Input (Address) 
    ↓
Geocoding (location.py)
    ↓
API Request (run.py)
    ↓
Data Validation (Pydantic)
    ↓
Visualization (matplotlib)
```

### 2. Key Components

#### Geocoding Process
```python
# weather/location.py
def get_longitude_and_latitude_for_address(address: str) -> tuple[float, float]:
    geolocator = Nominatim(user_agent="api_manager_location")
    location = geolocator.geocode(query=address)
    
    if not location:
        raise Exception("Could not find coordinates for address")
    
    return location.latitude, location.longitude
```

**What happens here:**
- Takes a human-readable address
- Uses OpenStreetMap's Nominatim service
- Returns precise coordinates
- Handles failures gracefully

#### API Integration
```python
# weather/run.py
def run_weather_request(address: str):
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    lat, long = get_longitude_and_latitude_for_address(address=address)
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m",
        "models": "gfs_seamless",
        "temperature_unit": "fahrenheit"
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return WeatherResult(**data)  # Pydantic validation here!
```

**Key points:**
- Constructs API URL with parameters
- Handles HTTP errors with `raise_for_status()`
- **Pydantic magic**: `WeatherResult(**data)` automatically validates the JSON response
- Returns a strongly-typed object

#### Data Visualization
```python
def show_graph(times: list[datetime], temps: list[float], location: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    ax.plot(times, temps, marker="o", linestyle="-", linewidth=2)
    ax.set_title(f"Temperature for {location}", fontsize=14)
    ax.set_xlabel("Date / Time", fontsize=12)
    ax.set_ylabel("Temperature (°F)", fontsize=12)
    
    # Format dates nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=30)
    
    plt.tight_layout()
    plt.show()
```

### 3. Error Handling

The application handles several types of errors:

1. **Geocoding Failures**: When an address can't be found
2. **API Errors**: Network issues or invalid responses
3. **Data Validation**: Invalid JSON structure from API
4. **Type Errors**: Caught by MyPy during development

## Development Best Practices

### 1. Type Hints Everywhere

```python
# Good
def process_weather_data(data: dict[str, Any]) -> WeatherResult:
    return WeatherResult(**data)

# Avoid
def process_weather_data(data):
    return WeatherResult(**data)
```

### 2. Pydantic Models for External Data

Always validate external data (APIs, user input, config files):

```python
# This ensures data integrity
weather_data = WeatherResult(**api_response)
```

### 3. Meaningful Error Messages

```python
# Good
if not location:
    raise ValueError(f"Could not find coordinates for address: {address}")

# Avoid
if not location:
    raise Exception("Error")
```

### 4. Modular Design

- Separate concerns into different modules
- Keep functions focused and single-purpose
- Use clear, descriptive names

## Conclusion

This project demonstrates how to build a robust Python application using modern tools and practices:

- **Pydantic** ensures data integrity and provides excellent developer experience
- **MyPy** catches type errors early and improves code quality
- **Clean architecture** makes the code maintainable and testable
- **Type hints** serve as documentation and enable better tooling

These practices lead to more reliable, maintainable, and collaborative codebases. As you continue developing, consider adding tests, logging, and more sophisticated error handling to further improve the application.

---

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

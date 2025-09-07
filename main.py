
from weather.run import run_weather_request, show_graph

if __name__ == '__main__':
    address = input("Please enter your location (address or city, country): ")
    result = run_weather_request(address)
    show_graph(times=result.hourly.time, temps=result.hourly.temperature_2m, location=address)

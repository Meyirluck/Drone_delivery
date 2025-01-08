# Drone Delivery System

This is a Flask-based drone delivery simulation system. The system includes features for order placement, monitoring drone locations on a map, and simulating drone movements between the base, restaurants, and delivery locations.

## Features

1. **Order Placement**
   - Customers can select their name, phone number, and restaurant for placing an order.
   - Supported restaurants: Salam Bro, KFC, YOLO.

2. **Drone Monitoring**
   - The system visualizes drone locations on an interactive map using Leaflet.js.
   - Displays real-time weather conditions, battery level, and other information for the drone.

3. **Drone Movement Simulation**
   - Drones move between the base, restaurants, and delivery locations.
   - Includes logic for handling weather conditions, low battery, and distance limitations.

4. **Weather and Battery Management**
   - Retrieves real-time weather data using the OpenWeather API.
   - Simulates battery consumption and recharging.

5. **Interactive Map**
   - Allows users to click on a map to set delivery destinations.
   - Visualizes the drone's route and updates positions in real-time.

## Prerequisites

1. **Python 3.7 or later**
2. **Dependencies**: Install using `pip install -r requirements.txt`.
3. **API Key**: An OpenWeather API key is required to fetch weather data.

## Usage

### Placing an Order
1. Navigate to the main page and fill in your details.
2. Select a restaurant and submit the order.
3. You will be redirected to the map for delivery tracking.

### Tracking the Drone
1. The map displays the drone's current position, weather conditions, and battery status.
2. Click anywhere on the map to set a delivery location.
3. Confirm the delivery when prompted, and the drone will begin moving toward the destination.

## Configuration

- **Drone Base Location**: Default is set to `43.1965135, 76.6309754` for Kaskelen.
- **Maximum Distance**: Drones can fly up to 15 km.
- **Weather Conditions**: Delivery is restricted if humidity exceeds 75% or wind speed exceeds 10 m/s.

## Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript (Leaflet.js, jQuery)
- **APIs**: OpenWeather API
- **Geolocation**: geopy for distance calculation

## Notes

- Ensure the OpenWeather API key is valid for retrieving weather data.
- Monitor battery status to ensure drones can complete deliveries.


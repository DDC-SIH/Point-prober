from flask import Flask, request, jsonify
import requests
import numpy as np
from datetime import datetime
import dateutil.parser
from pyproj import Transformer

app = Flask(__name__)

# INSAT 3DR information
INSAT_3DR_LONGITUDE = 74.0  # Geostationary position in degrees East

def get_point_probe(lat, lon, timestamp):
    """
    Calculate point probe data for INSAT 3DR satellite based on given coordinates and time
    
    Args:
        lat (float): Latitude in degrees
        lon (float): Longitude in degrees
        timestamp (datetime): Timestamp for the data
    
    Returns:
        dict: Point probe data
    """
    # Convert geodetic to satellite view coordinates
    # This is a simplified calculation - in a real application, 
    # you would use actual satellite data or APIs
    
    # Check if coordinates are in visible range of the satellite
    if not (-81 <= lat <= 81 and -81 + INSAT_3DR_LONGITUDE <= lon <= 81 + INSAT_3DR_LONGITUDE):
        return {"error": "Coordinates outside INSAT 3DR viewing range"}
    
    # Calculate satellite zenith angle
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon - INSAT_3DR_LONGITUDE)
    
    # Earth radius in km
    R_EARTH = 6378.137
    # Geostationary orbit height in km
    H_GEO = 35786.0
    
    # Calculate viewing angle
    r_squared = (R_EARTH**2) + ((R_EARTH + H_GEO)**2) - (2 * R_EARTH * (R_EARTH + H_GEO) * 
                 np.cos(lat_rad) * np.cos(lon_rad))
    zenith_angle = np.arccos((R_EARTH * np.sin(lat_rad)) / np.sqrt(r_squared))
    
    # Mock sensor data based on time and location
    # In a real application, you would fetch actual satellite data
    hour = timestamp.hour
    
    # Simulated temperature based on time of day and latitude
    base_temp = 25.0 - 0.5 * abs(lat)  # Cooler at higher latitudes
    diurnal_factor = np.sin(np.pi * (hour - 6) / 12) * 10  # Day-night cycle
    temperature = base_temp + diurnal_factor
    
    # Simulated cloud cover based on longitude and time
    cloud_factor = (np.sin(np.radians(lon) * 2) + 1) / 2
    time_factor = (np.sin(np.radians(hour * 15)) + 1) / 2
    cloud_cover = (cloud_factor * 0.7 + time_factor * 0.3) * 100
    
    # Sample data that would be returned from INSAT 3DR
    point_data = {
        "coordinates": {
            "latitude": lat,
            "longitude": lon
        },
        "timestamp": timestamp.isoformat(),
        "satellite": "INSAT 3DR",
        "satellite_position": f"{INSAT_3DR_LONGITUDE}°E",
        "zenith_angle_degrees": np.degrees(zenith_angle),
        "data": {
            "temperature_celsius": round(temperature, 1),
            "cloud_cover_percent": round(cloud_cover, 1),
            "infrared_radiance": round(20.0 + temperature * 0.5, 2),
            "water_vapor": round(50.0 + cloud_cover * 0.3, 2)
        }
    }
    
    return point_data

@app.route('/point-probe', methods=['GET'])
def point_probe():
    # Get parameters from the request
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        time_str = request.args.get('time')
        
        # Validate parameters
        if lat < -90 or lat > 90:
            return jsonify({"error": "Latitude must be between -90 and 90 degrees"}), 400
        
        if lon < -180 or lon > 180:
            return jsonify({"error": "Longitude must be between -180 and 180 degrees"}), 400
        
        # Parse time string
        if time_str:
            try:
                timestamp = dateutil.parser.parse(time_str)
            except ValueError:
                return jsonify({"error": "Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        else:
            # Use current time if not specified
            timestamp = datetime.now()
            
        # Get the point probe data
        result = get_point_probe(lat, lon, timestamp)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>INSAT 3DR Point Probe API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>INSAT 3DR Point Probe API</h1>
            <p>Submit a GET request to <code>/point-probe</code> with the following parameters:</p>
            <ul>
                <li><code>lat</code> - Latitude in degrees (-90 to 90)</li>
                <li><code>lon</code> - Longitude in degrees (-180 to 180)</li>
                <li><code>time</code> - (Optional) ISO format timestamp (YYYY-MM-DDTHH:MM:SS)</li>
            </ul>
            <p>Example: <a href="/point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00">/point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True) 
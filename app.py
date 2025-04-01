from flask import Flask, request, jsonify
import requests
import numpy as np
from datetime import datetime
import dateutil.parser
from pyproj import Transformer
import re
import os
from pathlib import Path

app = Flask(__name__)

# INSAT 3DR information
INSAT_3DR_LONGITUDE = 74.0  # Geostationary position in degrees East

# Directory for COG files
COG_DIRECTORY = os.environ.get('COG_DIRECTORY', './data')

def extract_datetime_from_filename(filename):
    """
    Extract date and time from INSAT 3DR filename using regex
    Format example: 3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif
    
    Returns:
        datetime object if successful, None otherwise
    """
    pattern = r'3RIMG_(\d{2})([A-Z]{3})(\d{4})_(\d{4})_'
    match = re.search(pattern, filename)
    
    if not match:
        return None
    
    day = match.group(1)
    month_str = match.group(2)
    year = match.group(3)
    time_str = match.group(4)
    
    # Convert month name to number
    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }
    
    month = month_map.get(month_str, '01')  # Default to January if unknown
    
    # Parse hours and minutes
    hours = time_str[:2]
    minutes = time_str[2:]
    
    # Create ISO format datetime string
    dt_string = f"{year}-{month}-{day}T{hours}:{minutes}:00"
    
    try:
        return dateutil.parser.parse(dt_string)
    except ValueError:
        return None

def is_cog_file_valid(filename):
    """Check if a COG file exists and has a valid format"""
    filepath = Path(COG_DIRECTORY) / filename
    
    if not filepath.exists():
        return False, f"File {filename} not found in {COG_DIRECTORY}"
    
    if not filename.lower().endswith('.cog.tif'):
        return False, "File is not a valid COG format (.cog.tif)"
    
    # Check if filename follows INSAT 3DR naming convention
    if not re.match(r'3RIMG_\d{2}[A-Z]{3}\d{4}_\d{4}_.*\.cog\.tif', filename):
        return False, "Filename does not follow INSAT 3DR naming convention"
    
    return True, ""

def get_point_probe(lat, lon, timestamp, cog_filename=None):
    """
    Calculate point probe data for INSAT 3DR satellite based on given coordinates and time
    
    Args:
        lat (float): Latitude in degrees
        lon (float): Longitude in degrees
        timestamp (datetime): Timestamp for the data
        cog_filename (str, optional): COG file to use for validation
    
    Returns:
        dict: Point probe data
    """
    # Check if coordinates are in visible range of the satellite
    if not (-81 <= lat <= 81 and -81 + INSAT_3DR_LONGITUDE <= lon <= 81 + INSAT_3DR_LONGITUDE):
        return {"error": "Coordinates outside INSAT 3DR viewing range"}
    
    # For COG files, we would perform additional validation
    # In a real implementation, we would read the COG file's bounds and check if the coordinates
    # are within them. Here we're simulating with fixed bounds for ASIA region
    
    # Simulated bounds for ASIA region
    asia_bounds = {
        "min_lat": 5.0,
        "max_lat": 40.0,
        "min_lon": 60.0,
        "max_lon": 100.0
    }
    
    if cog_filename:
        if not (asia_bounds["min_lat"] <= lat <= asia_bounds["max_lat"] and 
                asia_bounds["min_lon"] <= lon <= asia_bounds["max_lon"]):
            return {
                "error": "Coordinates outside valid data range for this product",
                "valid_range": asia_bounds
            }
    
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
    # In a real application, you would fetch actual satellite data from the COG file
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
    
    # Add file information if COG file was used
    if cog_filename:
        point_data["source_file"] = cog_filename
    
    return point_data

@app.route('/point-probe', methods=['GET'])
def point_probe():
    # Get parameters from the request
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        time_str = request.args.get('time')
        cog_file = request.args.get('file')
        
        # Validate parameters
        if lat < -90 or lat > 90:
            return jsonify({"error": "Latitude must be between -90 and 90 degrees"}), 400
        
        if lon < -180 or lon > 180:
            return jsonify({"error": "Longitude must be between -180 and 180 degrees"}), 400
        
        # Handle COG file if provided
        if cog_file:
            # Check if file is valid
            is_valid, error_msg = is_cog_file_valid(cog_file)
            if not is_valid:
                return jsonify({"error": error_msg}), 400
            
            # Extract timestamp from filename
            timestamp = extract_datetime_from_filename(cog_file)
            if not timestamp:
                return jsonify({"error": "Failed to extract date and time from filename"}), 400
        else:
            # Parse time string if provided, otherwise use current time
            if time_str:
                try:
                    timestamp = dateutil.parser.parse(time_str)
                except ValueError:
                    return jsonify({"error": "Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
            else:
                # Use current time if not specified
                timestamp = datetime.now()
            
        # Get the point probe data
        result = get_point_probe(lat, lon, timestamp, cog_file)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/cog-files', methods=['GET'])
def list_cog_files():
    """List available COG files in the data directory"""
    try:
        files = []
        path = Path(COG_DIRECTORY)
        
        if path.exists() and path.is_dir():
            for file in path.glob('*.cog.tif'):
                dt = extract_datetime_from_filename(file.name)
                files.append({
                    "filename": file.name,
                    "size_bytes": file.stat().st_size,
                    "datetime": dt.isoformat() if dt else None
                })
            
            return jsonify({
                "count": len(files),
                "files": files
            })
        else:
            return jsonify({"error": f"COG directory {COG_DIRECTORY} does not exist"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>INSAT 3DR Point Probe API</h1>
            
            <h2>Point Probe API</h2>
            <p>Submit a GET request to <code>/point-probe</code> with the following parameters:</p>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Description</th>
                    <th>Required</th>
                </tr>
                <tr>
                    <td><code>lat</code></td>
                    <td>Latitude in degrees (-90 to 90)</td>
                    <td>Yes</td>
                </tr>
                <tr>
                    <td><code>lon</code></td>
                    <td>Longitude in degrees (-180 to 180)</td>
                    <td>Yes</td>
                </tr>
                <tr>
                    <td><code>time</code></td>
                    <td>ISO format timestamp (YYYY-MM-DDTHH:MM:SS)</td>
                    <td>No (if <code>file</code> not provided)</td>
                </tr>
                <tr>
                    <td><code>file</code></td>
                    <td>INSAT 3DR COG file to use (e.g., 3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif)</td>
                    <td>No</td>
                </tr>
            </table>
            
            <h3>Examples:</h3>
            <ul>
                <li>Using time parameter: <a href="/point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00">/point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00</a></li>
                <li>Using COG file: <a href="/point-probe?lat=28.6&lon=77.2&file=3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif">/point-probe?lat=28.6&lon=77.2&file=3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif</a></li>
            </ul>
            
            <h2>Available COG Files</h2>
            <p>To list all available COG files: <a href="/cog-files">/cog-files</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs(COG_DIRECTORY, exist_ok=True)
    app.run(debug=True) 
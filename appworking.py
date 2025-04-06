from flask import Flask, request, jsonify
import rasterio
from rasterio.warp import transform
import os
from datetime import datetime, timedelta
import glob

app = Flask(__name__)

# Set the directory where COG files are stored
DATA_DIR = "./data"  # Update as per your structure

# Helper to find files within date range
def get_files_for_range(date_start, date_end):
    date_range = [date_start + timedelta(days=i) for i in range((date_end - date_start).days + 1)]
    all_files = []
    for date in date_range:
        # Look for both .tif and .cog.tif files
        pattern = f"*{date.strftime('%d%b%Y').upper()}*.tif"
        matches = glob.glob(os.path.join(DATA_DIR, pattern))
        all_files.extend(matches)
        
        # Also check for .cog.tif files
        pattern = f"*{date.strftime('%d%b%Y').upper()}*.cog.tif"
        matches = glob.glob(os.path.join(DATA_DIR, pattern))
        all_files.extend(matches)
    return all_files

# Helper function to extract date and time from filename
def extract_date_time(filename):
    # Extract date and time from filenames like 3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif
    parts = os.path.basename(filename).split('_')
    if len(parts) >= 3:
        date_str = parts[1]  # e.g., 22MAR2025
        time_str = parts[2] if len(parts) > 2 else None  # e.g., 0915
        
        date_obj = datetime.strptime(date_str, "%d%b%Y")
        if time_str and time_str.isdigit() and len(time_str) == 4:
            # Add time information if available
            hours = int(time_str[:2])
            minutes = int(time_str[2:])
            date_obj = date_obj.replace(hour=hours, minute=minutes)
        
        return date_obj
    return None

# Helper to probe a point
def probe_point(file_path, lon, lat, bands):
    result = {}
    with rasterio.open(os.path.abspath(file_path)) as src:
        dst_crs = src.crs
        x, y = transform("EPSG:4326", dst_crs, [lon], [lat])
        values = list(src.sample([(x[0], y[0])]))[0]
        for b in bands:
            val = values[b - 1]
            result[f"Band_{b}"] = float(val) if val is not None else None  # ✅ fixes JSON error

    return result

@app.route("/probe", methods=["POST"])
def probe():
    data = request.get_json()
    lon = data.get("lon")
    lat = data.get("lat")
    bands = data.get("bands", list(range(1, 17)))  # default all bands
    date = data.get("date")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    test_file = data.get("test_file")  # Optional: specify a specific test file

    # Validate inputs
    if not lon or not lat:
        return jsonify({"error": "Missing coordinates"}), 400

    results = []

    # Special case: if test_file is provided, use that directly
    if test_file:
        files = [test_file] if os.path.exists(test_file) else []
    # Single date case
    elif date:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        files = get_files_for_range(date_obj, date_obj)
    # Date range case
    elif start_date and end_date:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        files = get_files_for_range(start_obj, end_obj)
    else:
        return jsonify({"error": "Missing date, date range, or test_file"}), 400

    for file in files:
        try:
            # Try to extract date from filename
            file_date = extract_date_time(file)
            date_str = file_date.strftime("%Y-%m-%d %H:%M") if file_date else "Unknown"
            
            # Get actual values from the geotiff
            values = probe_point(file, lon, lat, bands)
            results.append({
                "file": os.path.basename(file),
                "date": date_str,
                "values": values
            })
        except Exception as e:
            results.append({"file": os.path.basename(file), "error": str(e)})

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

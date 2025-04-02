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
        pattern = f"*{date.strftime('%d%b%Y').upper()}*.tif"
        matches = glob.glob(os.path.join(DATA_DIR, pattern))
        all_files.extend(matches)
    return all_files

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

    # Validate inputs
    if not lon or not lat:
        return jsonify({"error": "Missing coordinates"}), 400

    results = []

    # Single date case
    if date:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        files = get_files_for_range(date_obj, date_obj)
    elif start_date and end_date:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        files = get_files_for_range(start_obj, end_obj)
    else:
        return jsonify({"error": "Missing date or date range"}), 400

    for file in files:
        file_date_str = os.path.basename(file).split("_")[1]  # e.g. 22MAR2025
        file_date = datetime.strptime(file_date_str, "%d%b%Y")
        try:
            values = probe_point(file, lon, lat, bands)
            results.append({
                "file": os.path.basename(file),
                "date": file_date.strftime("%Y-%m-%d"),
                "values": values
            })
        except Exception as e:
            results.append({"file": os.path.basename(file), "error": str(e)})

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

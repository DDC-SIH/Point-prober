# Point-prober

A Flask server that returns point probe data from INSAT 3DR satellite based on time and coordinates.

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a data directory for COG files:
   ```
   mkdir -p data
   ```

## Usage

Start the server:

```
python app.py
```

The server will run at http://localhost:5000

### API Endpoints

#### GET /point-probe

Returns point probe data for the INSAT 3DR satellite at the specified coordinates and time.

Parameters:

- `lat` (required): Latitude in degrees (-90 to 90)
- `lon` (required): Longitude in degrees (-180 to 180)
- `time` (optional): ISO format timestamp (YYYY-MM-DDTHH:MM:SS). If not provided, current time will be used.
- `file` (optional): Filename of INSAT 3DR COG file to use. If provided, time will be extracted from the filename.

Example request using time parameter:

```
GET /point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00
```

Example request using COG file:

```
GET /point-probe?lat=28.6&lon=77.2&file=3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif
```

Example response:

```json
{
  "coordinates": {
    "latitude": 28.6,
    "longitude": 77.2
  },
  "timestamp": "2025-03-22T09:15:00",
  "satellite": "INSAT 3DR",
  "satellite_position": "74.0°E",
  "zenith_angle_degrees": 15.23,
  "data": {
    "temperature_celsius": 32.8,
    "cloud_cover_percent": 65.4,
    "infrared_radiance": 36.4,
    "water_vapor": 69.62
  },
  "source_file": "3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif"
}
```

#### GET /cog-files

Lists all available COG files in the data directory.

Example response:

```json
{
  "count": 1,
  "files": [
    {
      "filename": "3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif",
      "size_bytes": 102400,
      "datetime": "2025-03-22T09:15:00"
    }
  ]
}
```

## COG File Format

The server expects INSAT 3DR COG files to follow this naming convention:

```
3RIMG_DDMMMYYYY_HHMM_L1C_REGION_SENSOR_V01R00.cog.tif
```

Where:

- `DD`: Day (01-31)
- `MMM`: Month abbreviation (JAN, FEB, MAR, etc.)
- `YYYY`: Year (e.g., 2025)
- `HHMM`: Time in 24-hour format (e.g., 0915 for 9:15 AM)
- `REGION`: Coverage area (e.g., ASIA)
- `SENSOR`: Sensor used (e.g., MER)

Example: `3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif`

## Configuration

You can configure the location of the COG files directory by setting the `COG_DIRECTORY` environment variable:

```
export COG_DIRECTORY=/path/to/cog/files
python app.py
```

## Notes

This server provides simulated data based on a simplified model of the INSAT 3DR satellite. In a production environment, you would:

1. Connect to actual satellite data sources
2. Read raster data from the COG files for the given coordinates
3. Implement proper validation of the spatial extent of each COG file

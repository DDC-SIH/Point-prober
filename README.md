# Point-prober

A Flask-based geospatial data extraction API for retrieving pixel values from GeoTIFF/COG files at specific geographic coordinates.

## Overview

Point-prober allows users to extract pixel values at specific geographic coordinates (longitude and latitude) from GeoTIFF or Cloud Optimized GeoTIFF (COG) files. The API supports querying by date, date range, or directly specifying a file to probe.

## Prerequisites

- Python 3.6 or higher
- GDAL/rasterio environment

### Required Python packages:

```
flask
rasterio
```

## Installation

1. Clone this repository
2. Activate your GDAL/rasterio environment:
   ```
   conda activate gdal
   ```
3. Install the required packages (if not already installed):
   ```
   pip install flask rasterio
   ```

## Running the Server

```
python appworking.py
```

The server will start on port 5000 by default.

## API Documentation

### Endpoint: `/probe`

Retrieves pixel values from geospatial files at specified coordinates.

#### Method: POST

#### Request Body Parameters

| Parameter  | Type       | Description                                | Required | Default   |
| ---------- | ---------- | ------------------------------------------ | -------- | --------- |
| lon        | float      | Longitude (in decimal degrees)             | Yes      | None      |
| lat        | float      | Latitude (in decimal degrees)              | Yes      | None      |
| bands      | array[int] | Array of band indices to extract (1-based) | No       | All bands |
| date       | string     | Single date in format "YYYY-MM-DD"         | No\*     | None      |
| start_date | string     | Start date of range in format "YYYY-MM-DD" | No\*     | None      |
| end_date   | string     | End date of range in format "YYYY-MM-DD"   | No\*     | None      |
| test_file  | string     | Path to specific GeoTIFF/COG file to probe | No\*     | None      |

\* At least one of `date`, `(start_date AND end_date)`, or `test_file` must be provided.

#### Response Format

The API returns a JSON array of results, with one object per file processed:

```json
[
  {
    "file": "filename.tif",
    "date": "YYYY-MM-DD HH:MM",
    "values": {
      "Band_1": 0.42,
      "Band_2": 0.38,
      "Band_3": 0.65
    }
  }
]
```

In case of errors, the response includes error information:

```json
[
  {
    "file": "filename.tif",
    "error": "Error message"
  }
]
```

#### Error Codes

- **400 Bad Request**: Missing required parameters
- **500 Internal Server Error**: Server-side processing error

## Usage Examples

### Example 1: Probe a specific file at coordinates

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"lon": 86.3976, "lat": 24.9879, "bands": [1, 2, 3], "test_file": "test_lowrange_semitrans1.tif"}' \
  http://127.0.0.1:5000/probe
```

### Example 2: Probe by date

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"lon": 86.3976, "lat": 24.9879, "bands": [1, 2, 3], "date": "2025-03-22"}' \
  http://127.0.0.1:5000/probe
```

### Example 3: Probe within a date range

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"lon": 86.3976, "lat": 24.9879, "bands": [1, 2, 3], "start_date": "2025-03-01", "end_date": "2025-03-31"}' \
  http://127.0.0.1:5000/probe
```

## File Naming Convention

When using date-based queries, the API looks for files in the `./data` directory that match the pattern:

```
*DDMMMYYYY*.tif  or  *DDMMMYYYY*.cog.tif
```

For example, files for March 22, 2025 should include `22MAR2025` in their filename:

- `3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif`

The API also extracts time information if available in the format `HHMM` (e.g., `0915` for 09:15).

## How It Works

1. The API receives a request with coordinates and date/file information
2. It locates the appropriate geospatial file(s) based on the request
3. For each file, it:
   - Transforms the provided WGS84 coordinates to the file's coordinate reference system
   - Extracts the pixel values at the specified location for the requested bands
   - Returns the results in a structured JSON format

## Advanced Usage

### Working with Time Information

The API extracts time information from filenames with the format:

```
PREFIX_DDMMMYYYY_HHMM_SUFFIX.tif
```

For example, `3RIMG_22MAR2025_0915_L1C_ASIA_MER_V01R00.cog.tif` will be interpreted as data from March 22, 2025 at 09:15.

### Testing with Specific Files

For testing or direct file access, use the `test_file` parameter to bypass the date-based file search:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"lon": 86.3976, "lat": 24.9879, "test_file": "path/to/your/file.tif"}' \
  http://127.0.0.1:5000/probe
```

## License

[MIT License](LICENSE)

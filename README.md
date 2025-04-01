# Point-prober

A Flask server that returns point probe data from INSAT 3DR satellite based on time and coordinates.

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
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

Example request:

```
GET /point-probe?lat=28.6&lon=77.2&time=2023-05-15T14:30:00
```

Example response:

```json
{
  "coordinates": {
    "latitude": 28.6,
    "longitude": 77.2
  },
  "timestamp": "2023-05-15T14:30:00",
  "satellite": "INSAT 3DR",
  "satellite_position": "74.0°E",
  "zenith_angle_degrees": 15.23,
  "data": {
    "temperature_celsius": 32.8,
    "cloud_cover_percent": 65.4,
    "infrared_radiance": 36.4,
    "water_vapor": 69.62
  }
}
```

## Notes

This server provides simulated data based on a simplified model of the INSAT 3DR satellite. In a production environment, you would connect to actual satellite data sources.

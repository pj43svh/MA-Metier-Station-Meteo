from database import get_db_connection, add_data, read_data

add_data("weather_data", value={"device_id": 1, "temperature": 65.5, "humidity": 50.0, "pressure": 1057.0, "date_hours": "2026-01-16 15:00:00"})
add_data("weather_data", value={"device_id": 2, "temperature": 53.1, "humidity": 40.0, "pressure": 1057.5, "date_hours": "2026-01-16 15:00:00"})
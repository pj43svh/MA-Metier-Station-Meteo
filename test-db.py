from database import get_db_connection, add_data, read_data
import random

add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.32"})
add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.33"})

date = -1

tempperature1=10
tempperature2=10
humidity1=    50
humidity2=    50
pressure1=    1020
pressure2=    1020
for i in range(24):
    tempperature1+= random.randint(-5,5)
    tempperature2+= random.randint(-5,5)
    humidity1+=     random.randint(-10,10)
    humidity2+=     random.randint(-10,10)
    pressure1+=     random.randint(-2,2)
    pressure2+=     random.randint(-2,2)
    date += 1
    add_data("weather_data", value={"device_id": 1, "temperature": tempperature1, "humidity": humidity1, "pressure": pressure1, "date": f"2026-03-16", "hour":date})
    add_data("weather_data", value={"device_id": 2, "temperature": tempperature2, "humidity": humidity2, "pressure": pressure2, "date": f"2026-03-16", "hour":date})

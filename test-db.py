from database import add_data
import random

#add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.32"})
#add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.33"})

#hour = 0
#date = 1
#tempperature1=10
#tempperature2=10
#humidity1=    50
#humidity2=    50
#pressure1=    1020
#pressure2=    1020
#for i in range(24*30):
#    tempperature1+= random.randint(-5,5)
#    tempperature2+= random.randint(-5,5)
#    humidity1+=     random.randint(-10,10)
#    humidity2+=     random.randint(-10,10)
#    pressure1+=     random.randint(-2,2)
#    pressure2+=     random.randint(-2,2)
#    add_data("esp1", value={"temperature": tempperature1, "humidity": humidity1, "pressure": pressure1, "date": f"2026-01-{date}","hour": f"{hour}:00"})
#    add_data("esp2", value={"temperature": tempperature2, "humidity": humidity2, "pressure": pressure2, "date": f"2026-01-{date}","hour": f"{hour}:00"})
#    hour += 1
#    if hour == 24 :
#        hour = 0
#        date+=1

add_data("esp1", value={"temperature": 999.9, "humidity": 999.9, "pressure": 999.9, "date": f"2026-01-31","hour": f"01:00"})
add_data("esp2", value={"temperature": 999.9, "humidity": 999.9, "pressure": 999.9, "date": f"2026-01-31","hour": f"01:00"})
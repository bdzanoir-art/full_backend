"""
Run with:  python seed.py
(from inside backend_browse/ with the venv activated)
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from inventory.models import Category, Material

# ── Categories ────────────────────────────────────────────────────────────────
cats = [
    {"name": "Microcontrollers",    "key": "microcontrollers"},
    {"name": "Development Boards",  "key": "development-boards"},
    {"name": "Networking",          "key": "networking"},
    {"name": "Sensors",             "key": "sensors"},
    {"name": "Power Supplies",      "key": "power-supplies"},
]

cat_objs = {}
for c in cats:
    obj, created = Category.objects.get_or_create(key=c["key"], defaults={"name": c["name"]})
    cat_objs[c["key"]] = obj
    print(f"{'Created' if created else 'Exists '} category: {obj.name}")

# ── Materials ─────────────────────────────────────────────────────────────────
materials = [
    # Microcontrollers
    {"title": "Arduino Uno R3",        "category": "microcontrollers", "description": "Classic 8-bit AVR microcontroller board, ideal for beginners and prototyping.", "location": "Room A - Shelf 1", "status": "Available"},
    {"title": "Arduino Nano",          "category": "microcontrollers", "description": "Compact AVR-based board with USB connectivity, perfect for small projects.", "location": "Room A - Shelf 1", "status": "Available"},
    {"title": "ATmega328P (DIP)",      "category": "microcontrollers", "description": "Standalone 8-bit AVR MCU used in Arduino Uno, available as bare IC.", "location": "Room A - Shelf 2", "status": "Available"},
    {"title": "STM32F103C8 (Blue Pill)", "category": "microcontrollers", "description": "32-bit ARM Cortex-M3 microcontroller with abundant peripherals.", "location": "Room A - Shelf 3", "status": "In Use"},

    # Development Boards
    {"title": "Raspberry Pi 4 Model B", "category": "development-boards", "description": "Quad-core 64-bit SBC running Linux, 4 GB RAM. Great for IoT gateways.", "location": "Room B - Shelf 1", "status": "Available"},
    {"title": "ESP32 DevKit V1",        "category": "development-boards", "description": "Dual-core board with integrated Wi-Fi and Bluetooth 4.2.", "location": "Room B - Shelf 2", "status": "Available"},
    {"title": "BeagleBone Black",       "category": "development-boards", "description": "AM335x ARM Cortex-A8 SBC with 512 MB RAM and PRU sub-processors.", "location": "Room B - Shelf 3", "status": "Maintenance"},
    {"title": "NodeMCU (ESP8266)",      "category": "development-boards", "description": "Wi-Fi enabled development board based on the ESP8266 chip.", "location": "Room B - Shelf 2", "status": "Available"},

    # Networking
    {"title": "TP-Link TL-WR841N Router", "category": "networking", "description": "300 Mbps wireless N router, suitable for lab network experiments.", "location": "Room C - Shelf 1", "status": "Available"},
    {"title": "Cisco SG110-16 Switch",    "category": "networking", "description": "16-port unmanaged Gigabit Ethernet switch for structured wired networks.", "location": "Room C - Shelf 1", "status": "In Use"},
    {"title": "USB Wi-Fi Adapter (AC600)","category": "networking", "description": "Dual-band 802.11ac USB adapter for PC/laptop wireless connectivity.", "location": "Room C - Shelf 2", "status": "Available"},

    # Sensors
    {"title": "DHT22 Temperature & Humidity", "category": "sensors", "description": "Digital sensor providing temperature (−40 to 80 °C) and humidity readings.", "location": "Room D - Shelf 1", "status": "Available"},
    {"title": "HC-SR04 Ultrasonic Sensor",    "category": "sensors", "description": "Distance measurement sensor with 2–400 cm range.", "location": "Room D - Shelf 1", "status": "Available"},
    {"title": "MPU-6050 IMU",                 "category": "sensors", "description": "6-axis accelerometer + gyroscope module with I²C interface.", "location": "Room D - Shelf 2", "status": "Unavailable"},

    # Power Supplies
    {"title": "Bench Power Supply 30V/5A", "category": "power-supplies", "description": "Adjustable variable DC power supply for lab use.", "location": "Room E - Shelf 1", "status": "Available"},
    {"title": "LM7805 Voltage Regulator",  "category": "power-supplies", "description": "5 V fixed positive linear regulator in TO-220 package.", "location": "Room E - Shelf 2", "status": "Available"},
]

for m in materials:
    obj, created = Material.objects.get_or_create(
        title=m["title"],
        defaults={
            "description": m["description"],
            "category":    cat_objs[m["category"]],
            "location":    m["location"],
            "status":      m["status"],
        }
    )
    print(f"{'Created' if created else 'Exists '} material: {obj.title}")

print("\n✅ Seed complete.")

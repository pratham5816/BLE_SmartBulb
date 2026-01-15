
Summary — BLE-Based Smart Light Automation (Python)

This Python script implements a **proximity-based home automation system** using **BLE iBeacons** and **WiZ smart bulbs**.

**Core Technologies**

* **Python (asyncio)**
* **BLE scanning** via `bleak`
* **iBeacon packet parsing**
* **WiZ Smart Bulb control** via `pywizlight`
* **Asynchronous event handling**

---
How the Script Works

BLE iBeacon Detection

The script continuously scans for BLE advertisements using `BleakScanner`.

It extracts and decodes raw **iBeacon manufacturer data**:

UUID
Major / Minor
TX Power
RSSI (signal strength)

This allows accurate identification of a specific beacon 🧭

---

Proximity Estimation using RSSI

The distance is approximated using RSSI values:


FAR  = -80 dBm
CLOSE = -30 dBm
Trigger zone = [-80 dBm  →  -30 dBm]


When the device enters this range, the system determines that the user is **physically near the beacon**.

---

Event-Driven Light Automation

When the device enters the trigger range:

* The script connects to multiple WiZ bulbs by **IP address**
* Reads their current state
* **Toggles ON/OFF** automatically
* Prevents repeated triggering using a `triggered` flag
* Resets when the user moves away

All operations run asynchronously for fast, non-blocking performance ⚡

---

Real-World Use Case

> Walk into your room → Your phone’s BLE beacon is detected →
> Lights automatically turn ON / OFF without touching any switch.

---

What I Learned

* BLE & iBeacon internals
* Low-level packet parsing
* Async Python programming
* IoT device integration
* Real-time automation logic

---



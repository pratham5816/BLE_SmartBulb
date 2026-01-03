import asyncio
import time

from bleak import BleakScanner
import struct
import warnings
from pywizlight import wizlight, PilotBuilder

# Suppress the harmless cleanup warning
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Configuration.  // "192.168.1.13" hall // bedroom 192.168.1.5  192.168.1.8
BULB_IP = "192.168.1.4"
BULB_IP_B1 = "192.168.1.5"
BULB_IP_B2 = "192.168.1.8"

BArr = [BULB_IP , BULB_IP_B1, BULB_IP_B2]
TARGET_UUID = "FDA50693-A4E2-4FB1-AFCF-C6EB07647825"
TARGET_ADDRESS = "4D416CF5-1DC6-5F38-38E0-B63628E8CDB8"
RSSI_THRESHOLD_CLOSE = -30  # Very close (higher value = stronger signal)
RSSI_THRESHOLD_FAR = -80    # Further away (lower value = weaker signal)
# Trigger when RSSI is between -55 and -30 (in range)

# Track if we already triggered
triggered = False



async def toggle_bulb2():
    """Toggle all bulbs ON/OFF with better error handling"""
    print("\n" + "=" * 60)
    print("Toggling bulbs...")
    for i in range(0, 20):
        print(i)
        time.sleep(0.2)

    
    for b in BArr:
        try:
            print(f"\n→ Connecting to bulb {b}...")
            bulb = wizlight(b)
            
            # Wait for state with timeout
            state = await asyncio.wait_for(bulb.updateState(), timeout=5.0)
            
            if state.get_state():
                await asyncio.wait_for(bulb.turn_off(), timeout=5.0)
                print(f"  ✓ Bulb {b} turned OFF")
                time.sleep(5)
            else:
                await asyncio.wait_for(bulb.turn_on(), timeout=5.0)
                print(f"  ✓ Bulb {b} turned ON")
            
            await asyncio.sleep(0.2)
            
        except asyncio.TimeoutError:
            print(f"  ✗ Timeout: Bulb {b} not responding (check if it's online)")
        except Exception as e:
            print(f"  ✗ Error with bulb {b}: ERROR")
    
    print("\n" + "=" * 60)
    print("Done!\n")

async def toggle_bulb():
    """Toggle the bulb ON/OFF"""
    try:
        for b in BArr:
            bulb = wizlight(b)
            state = await bulb.updateState()
            if state.get_state():
                await bulb.turn_off()
                print(f"✓ Bulb {b} turned OFF")
            else:
                await bulb.turn_on()
                print(f"✓ Bulb {b} turned ON")
        await asyncio.sleep(0.1)
           
       
    except Exception as e:
        print(f"✗ Error toggling bulb: {e}")

def parse_ibeacon(manufacturer_data):
    """Parse iBeacon data from manufacturer specific data"""
    try:
        if len(manufacturer_data) < 23:
            return None
        
        # Check for Apple iBeacon prefix (0x02, 0x15)
        if manufacturer_data[0] != 0x02 or manufacturer_data[1] != 0x15:
            return None
        
        # Extract UUID (16 bytes)
        uuid_bytes = manufacturer_data[2:18]
        uuid = '-'.join([
            uuid_bytes[0:4].hex(),
            uuid_bytes[4:6].hex(),
            uuid_bytes[6:8].hex(),
            uuid_bytes[8:10].hex(),
            uuid_bytes[10:16].hex()
        ]).upper()
        
        # Extract Major (2 bytes, big endian)
        major = struct.unpack('>H', manufacturer_data[18:20])[0]
        
        # Extract Minor (2 bytes, big endian)
        minor = struct.unpack('>H', manufacturer_data[20:22])[0]
        
        # Extract TX Power (1 byte, signed)
        tx_power = struct.unpack('b', manufacturer_data[22:23])[0]
        
        return uuid, major, minor, tx_power
    except Exception as e:
        return None

async def monitor_beacon():
    """Monitor iBeacon and trigger bulb toggle when close"""
    global triggered
    
    print(f"Monitoring iBeacon...")
    print(f"Target UUID: {TARGET_UUID}")
    print(f"Target Address: {TARGET_ADDRESS}")
    print(f"RSSI Range: {RSSI_THRESHOLD_FAR} to {RSSI_THRESHOLD_CLOSE} dBm")
    print(f"Will toggle bulb at {BULB_IP} when in range\n")
    print("=" * 60)
    
    def detection_callback(device, advertisement_data):
        global triggered
        
        # Apple company ID is 0x004C (76 in decimal)
        if 76 in advertisement_data.manufacturer_data:
            manufacturer_data = advertisement_data.manufacturer_data[76]
            
            parsed = parse_ibeacon(manufacturer_data)
            if parsed:
                uuid, major, minor, tx_power = parsed
                rssi = advertisement_data.rssi
                
                # Check if this is our target beacon
                if uuid == TARGET_UUID or device.address == TARGET_ADDRESS:
                    print(f"\n[{device.address}] UUID: {uuid}")
                    print(f"  RSSI: {rssi} dBm | Range: {RSSI_THRESHOLD_FAR} to {RSSI_THRESHOLD_CLOSE} dBm")
                    print(f"  Major: {major} | Minor: {minor}")
                    
                    # Check if RSSI is in range (between FAR and CLOSE thresholds)
                    # Correct logic: RSSI must be >= -55 (far) AND <= -30 (close)
                    if RSSI_THRESHOLD_FAR <= rssi <= RSSI_THRESHOLD_CLOSE:
                        print(f"  ✓ RSSI {rssi} is IN RANGE ({RSSI_THRESHOLD_FAR} to {RSSI_THRESHOLD_CLOSE}) - YOU ARE CLOSE!")
                        if not triggered:
                            print(f"  🔄 Triggering bulb toggle...")
                            asyncio.create_task(toggle_bulb())
                            triggered = True
                    else:
                        print(f"  ⚠ RSSI {rssi} is OUT OF RANGE - Too far or too close")
                        if triggered:
                            # Reset trigger when you move away
                            print(f"  ↩ Reset trigger (moved out of range)")
                            triggered = False
    
    scanner = BleakScanner(detection_callback=detection_callback)
    
    print("\nScanning for iBeacon...\n")
    await scanner.start()
    
    # Scan for 60 seconds (adjust as needed)
    await asyncio.sleep(120)
    
    print("\n\nStopping scan...")
    await scanner.stop()
    print("Scan stopped.")

if __name__ == "__main__":
    print("iBeacon Proximity Trigger")
    print("=" * 60)
    try:
        asyncio.run(monitor_beacon())  # ✓ Run monitor function
    except KeyboardInterrupt:
        print("\nExiting...")

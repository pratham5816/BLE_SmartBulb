import asyncio
import warnings
from pywizlight import wizlight

# Suppress the harmless cleanup warning
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Replace with your bulb's IP address
BULB_IP = "192.168.1.13"  # Change this to your bulb's IP


async def toggle():
    """Toggle bulb ON/OFF"""
    try:
        bulb = wizlight(BULB_IP)
        state = await bulb.updateState()
        if state.get_state():
            await bulb.turn_off()
            print(f"✓ Bulb {BULB_IP} turned OFF")
        else:
            await bulb.turn_on()
            print(f"✓ Bulb {BULB_IP} turned ON")
        await asyncio.sleep(0.1)  # Small delay for cleanup
    except Exception as e:
        print(f"✗ Error toggling bulb: ")
        # print(f"Error type: {type(e).__name__}")
        # import traceback
        # traceback.print_exc()



if __name__ == "__main__":
    asyncio.run(toggle())
   
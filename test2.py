import asyncio
from pywizlight import wizlight, PilotBuilder, discovery

async def discover_all_bulbs():
    """Discover all WiZ bulbs in your network"""
    print("Searching for WiZ bulbs in your room...")
    print("=" * 60)
    
    try:
        # Discover bulbs on the network
        bulbs = await discovery.discover_lights(broadcast_space="192.168.1.255")
        
        if not bulbs:
            print("\nNo WiZ bulbs found!")
            print("\nTroubleshooting tips:")
            print("- Make sure your WiZ bulbs are powered on")
            print("- Ensure your device is on the same WiFi network as the bulbs")
            print("- Check if bulbs are connected to WiFi (not Bluetooth mode)")
            return []
        
        print(f"\n✓ Found {len(bulbs)} WiZ bulb(s)!\n")
        
        # Display details for each bulb
        for idx, bulb in enumerate(bulbs, 1):
            print(f"Bulb #{idx}:")
            print(f"  IP Address: {bulb.ip}")
            print(f"  MAC Address: {bulb.mac}")
            
            # Try to get bulb state
            try:
                state = await bulb.updateState()
                if state:
                    status = "ON" if state.get_state() else "OFF"
                    brightness = state.get_brightness()
                    print(f"  Status: {status}")
                    if brightness:
                        print(f"  Brightness: {brightness}")
            except Exception as e:
                print(f"  Status: Unable to get state")
            
            print()
        
        # Print summary with just IPs
        print("=" * 60)
        print("Summary - Bulb IP Addresses:")
        for idx, bulb in enumerate(bulbs, 1):
            print(f"  {idx}. {bulb.ip}")
        print("=" * 60)
        
        return bulbs
        
    except Exception as e:
        print(f"Error during discovery: {e}")
        print("\nMake sure you're connected to the same network as your bulbs!")
        return []

async def main():
    bulbs = await discover_all_bulbs()
    
    if bulbs:
        print(f"\n✓ Discovery complete! You can now use these IP addresses to control your bulbs.")
        print("\nExample usage:")
        print(f"  light = wizlight('{bulbs[0].ip}')")
        print("  await light.turn_on()")

if __name__ == "__main__":
    asyncio.run(main())



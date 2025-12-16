"""
Basic Channel Access Client using PyEPICS
Demonstrates fundamental CA operations with the MyProject IOC
"""

from epics import caget, caput, camonitor, cainfo
import time
from datetime import datetime


def display_pv_info(pv_name):
    """Display detailed information about a PV"""
    print(f"\n{'='*60}")
    print(f"PV Information for: {pv_name}")
    print(f"{'='*60}")
    cainfo(pv_name, print_out=True)


def read_single_value(pv_name):
    """Read a single value from a PV"""
    value = caget(pv_name)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {pv_name} = {value}")
    return value


def write_value(pv_name, value):
    """Write a value to a PV"""
    success = caput(pv_name, value)
    if success:
        print(f"Successfully wrote {value} to {pv_name}")
        # Verify the write
        new_value = caget(pv_name)
        print(f"Verified value: {new_value}")
    else:
        print(f"Failed to write to {pv_name}")
    return success


def monitor_callback(pvname=None, value=None, timestamp=None, **kwargs):
    """Callback function for camonitor"""
    dt = datetime.fromtimestamp(timestamp)
    print(f"[{dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {pvname} = {value}")


def monitor_pv(pv_name, duration=10):
    """Monitor a PV for changes over a specified duration"""
    print(f"\nMonitoring {pv_name} for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    camonitor(pv_name, callback=monitor_callback)
    
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")


def main():
    """Main demonstration function"""
    # Replace 'bradm' with your actual hostname prefix
    pv_prefix = "bradm"
    
    # Example PVs from MyProject IOC
    ai_pv = f"{pv_prefix}:aiExample"
    asub_pv = f"{pv_prefix}:aSubExample"
    
    print("="*60)
    print("Basic Channel Access Client - MyProject IOC")
    print("="*60)
    
    # Display PV information
    display_pv_info(ai_pv)
    
    # Read values
    print("\n--- Reading PV Values ---")
    read_single_value(ai_pv)
    read_single_value(asub_pv)
    
    # Write a value
    print("\n--- Writing to PV ---")
    write_value(asub_pv, 42)
    
    # Write and monitor
    print("\n--- Writing sequence and monitoring ---")
    monitor_pv(asub_pv, duration=5)
    
    # Write some test values
    print("\n--- Writing test sequence ---")
    for i in range(5):
        write_value(asub_pv, i * 10)
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. MyProject IOC is running")
        print("2. PV names match your hostname")

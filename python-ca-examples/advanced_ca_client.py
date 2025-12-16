"""
Advanced Channel Access Client using PyEPICS
Demonstrates advanced features: PV objects, callbacks, connection management
"""

from epics import PV
import time
import threading
from datetime import datetime
from collections import deque


class PVMonitor:
    """Class to monitor and log PV changes with statistics"""
    
    def __init__(self, pv_name, buffer_size=100):
        self.pv_name = pv_name
        self.pv = PV(pv_name, callback=self.on_change)
        self.buffer = deque(maxlen=buffer_size)
        self.change_count = 0
        self.lock = threading.Lock()
        
    def on_change(self, pvname=None, value=None, timestamp=None, **kwargs):
        """Callback when PV value changes"""
        with self.lock:
            self.change_count += 1
            dt = datetime.fromtimestamp(timestamp)
            entry = {
                'timestamp': dt,
                'value': value,
                'count': self.change_count
            }
            self.buffer.append(entry)
            print(f"[{dt.strftime('%H:%M:%S.%f')[:-3]}] {pvname}: {value} (change #{self.change_count})")
    
    def get_statistics(self):
        """Calculate statistics from buffered values"""
        with self.lock:
            if not self.buffer:
                return None
            
            values = [entry['value'] for entry in self.buffer if isinstance(entry['value'], (int, float))]
            
            if not values:
                return None
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1],
                'total_changes': self.change_count
            }
    
    def disconnect(self):
        """Disconnect from PV"""
        self.pv.disconnect()


class PVController:
    """Class to control multiple PVs with coordinated operations"""
    
    def __init__(self, pv_names):
        self.pvs = {name: PV(name) for name in pv_names}
        self._wait_for_connections()
    
    def _wait_for_connections(self, timeout=5.0):
        """Wait for all PVs to connect"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if all(pv.connected for pv in self.pvs.values()):
                print(f"All {len(self.pvs)} PVs connected successfully")
                return True
            time.sleep(0.1)
        
        # Report connection status
        for name, pv in self.pvs.items():
            status = "✓" if pv.connected else "✗"
            print(f"{status} {name}: {'Connected' if pv.connected else 'Disconnected'}")
        return False
    
    def get(self, pv_name):
        """Get value from a specific PV"""
        if pv_name in self.pvs:
            return self.pvs[pv_name].get()
        return None
    
    def put(self, pv_name, value, wait=False):
        """Put value to a specific PV"""
        if pv_name in self.pvs:
            self.pvs[pv_name].put(value, wait=wait)
            return True
        return False
    
    def get_all(self):
        """Get values from all PVs"""
        return {name: pv.get() for name, pv in self.pvs.items()}
    
    def disconnect_all(self):
        """Disconnect all PVs"""
        for pv in self.pvs.values():
            pv.disconnect()


def demonstrate_pv_object():
    """Demonstrate using PV objects for more control"""
    print("\n" + "="*60)
    print("Demonstrating PV Object Features")
    print("="*60)
    
    pv = PV("bradm:aSubExample")
    
    # Wait for connection
    if not pv.wait_for_connection(timeout=5.0):
        print(f"Failed to connect to PV")
        return
    
    print(f"\nPV: {pv.pvname}")
    print(f"Connected: {pv.connected}")
    print(f"Value: {pv.value}")
    print(f"Type: {pv.type}")
    print(f"Count: {pv.count}")
    print(f"Host: {pv.host}")
    
    # Demonstrate put with wait
    print("\nWriting with wait=True...")
    pv.put(99, wait=True)
    print(f"Value after put: {pv.get()}")
    
    pv.disconnect()


def demonstrate_monitoring():
    """Demonstrate advanced monitoring with statistics"""
    print("\n" + "="*60)
    print("Demonstrating Advanced Monitoring")
    print("="*60)
    
    monitor = PVMonitor("bradm:aSubExample")
    
    print("\nMonitoring started. Writing test values...\n")
    pv_writer = PV("bradm:aSubExample")
    
    # Write a sequence of values
    test_values = [10, 20, 15, 30, 25, 35, 28, 40, 32, 45]
    for value in test_values:
        pv_writer.put(value)
        time.sleep(0.5)
    
    # Display statistics
    time.sleep(1)
    stats = monitor.get_statistics()
    
    if stats:
        print("\n" + "-"*60)
        print("Statistics Summary")
        print("-"*60)
        print(f"Total changes detected: {stats['total_changes']}")
        print(f"Values in buffer: {stats['count']}")
        print(f"Minimum value: {stats['min']}")
        print(f"Maximum value: {stats['max']}")
        print(f"Average value: {stats['avg']:.2f}")
        print(f"Latest value: {stats['latest']}")
    
    monitor.disconnect()
    pv_writer.disconnect()


def demonstrate_controller():
    """Demonstrate coordinated control of multiple PVs"""
    print("\n" + "="*60)
    print("Demonstrating PV Controller")
    print("="*60)
    
    pv_names = ["bradm:aiExample", "bradm:aSubExample"]
    controller = PVController(pv_names)
    
    # Read all values
    print("\nCurrent values:")
    all_values = controller.get_all()
    for name, value in all_values.items():
        print(f"  {name}: {value}")
    
    # Coordinated write
    print("\nWriting coordinated values...")
    controller.put("bradm:aSubExample", 100, wait=True)
    time.sleep(0.5)
    
    print("\nFinal values:")
    all_values = controller.get_all()
    for name, value in all_values.items():
        print(f"  {name}: {value}")
    
    controller.disconnect_all()


def main():
    """Main demonstration function"""
    print("="*60)
    print("Advanced Channel Access Client - MyProject IOC")
    print("="*60)
    
    try:
        demonstrate_pv_object()
        time.sleep(1)
        
        demonstrate_monitoring()
        time.sleep(1)
        
        demonstrate_controller()
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. MyProject IOC is running")
        print("2. PV names match your hostname")


if __name__ == "__main__":
    main()

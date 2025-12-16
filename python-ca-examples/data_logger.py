"""
PV Data Logger
Demonstrates file I/O, data processing, and long-term monitoring
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from epics import PV
import time
import threading


class PVDataLogger:
    """Logger to record PV data to CSV and JSON formats"""
    
    def __init__(self, pv_name, output_dir="logs"):
        self.pv_name = pv_name
        self.pv = PV(pv_name, callback=self._on_value_change)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create timestamped filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_pv_name = pv_name.replace(":", "_")
        
        self.csv_file = self.output_dir / f"{safe_pv_name}_{timestamp}.csv"
        self.json_file = self.output_dir / f"{safe_pv_name}_{timestamp}.json"
        
        self.data_buffer = []
        self.lock = threading.Lock()
        self.is_logging = True
        
        # Initialize CSV file
        self._initialize_csv()
        
        print(f"Logger initialized for {pv_name}")
        print(f"CSV output: {self.csv_file}")
        print(f"JSON output: {self.json_file}")
    
    def _initialize_csv(self):
        """Create CSV file with headers"""
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'iso_time', 'pv_name', 'value', 'status', 'severity'])
    
    def _on_value_change(self, pvname=None, value=None, timestamp=None, **kwargs):
        """Callback when PV value changes"""
        if not self.is_logging:
            return
        
        with self.lock:
            dt = datetime.fromtimestamp(timestamp)
            entry = {
                'timestamp': timestamp,
                'iso_time': dt.isoformat(),
                'pv_name': pvname,
                'value': value,
                'status': kwargs.get('status', 0),
                'severity': kwargs.get('severity', 0)
            }
            self.data_buffer.append(entry)
            
            # Write to CSV immediately
            self._append_to_csv(entry)
            
            print(f"[{dt.strftime('%H:%M:%S')}] Logged: {pvname} = {value}")
    
    def _append_to_csv(self, entry):
        """Append entry to CSV file"""
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry['timestamp'],
                entry['iso_time'],
                entry['pv_name'],
                entry['value'],
                entry['status'],
                entry['severity']
            ])
    
    def save_json_summary(self):
        """Save all logged data to JSON file"""
        with self.lock:
            data = {
                'pv_name': self.pv_name,
                'start_time': self.data_buffer[0]['iso_time'] if self.data_buffer else None,
                'end_time': self.data_buffer[-1]['iso_time'] if self.data_buffer else None,
                'total_samples': len(self.data_buffer),
                'data': self.data_buffer
            }
            
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\nSaved {len(self.data_buffer)} samples to {self.json_file}")
    
    def get_summary_statistics(self):
        """Calculate summary statistics from logged data"""
        with self.lock:
            if not self.data_buffer:
                return None
            
            numeric_values = [
                entry['value'] for entry in self.data_buffer 
                if isinstance(entry['value'], (int, float))
            ]
            
            if not numeric_values:
                return None
            
            return {
                'count': len(numeric_values),
                'min': min(numeric_values),
                'max': max(numeric_values),
                'avg': sum(numeric_values) / len(numeric_values),
                'first': numeric_values[0],
                'last': numeric_values[-1],
                'range': max(numeric_values) - min(numeric_values)
            }
    
    def stop_logging(self):
        """Stop logging and save data"""
        self.is_logging = False
        self.save_json_summary()
        self.pv.disconnect()


class DataAnalyzer:
    """Analyze logged PV data from CSV or JSON files"""
    
    @staticmethod
    def load_csv(csv_file):
        """Load data from CSV file"""
        data = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['timestamp'] = float(row['timestamp'])
                try:
                    row['value'] = float(row['value'])
                except ValueError:
                    pass  # Keep as string if not numeric
                data.append(row)
        return data
    
    @staticmethod
    def load_json(json_file):
        """Load data from JSON file"""
        with open(json_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def analyze_csv(csv_file):
        """Analyze CSV file and print statistics"""
        data = DataAnalyzer.load_csv(csv_file)
        
        if not data:
            print("No data found in file")
            return
        
        numeric_values = [row['value'] for row in data if isinstance(row['value'], (int, float))]
        
        print(f"\n{'='*60}")
        print(f"Analysis of {csv_file}")
        print(f"{'='*60}")
        print(f"Total records: {len(data)}")
        print(f"PV name: {data[0]['pv_name']}")
        print(f"Start time: {data[0]['iso_time']}")
        print(f"End time: {data[-1]['iso_time']}")
        
        if numeric_values:
            print(f"\nValue Statistics:")
            print(f"  Count: {len(numeric_values)}")
            print(f"  Min: {min(numeric_values)}")
            print(f"  Max: {max(numeric_values)}")
            print(f"  Average: {sum(numeric_values) / len(numeric_values):.2f}")
            print(f"  Range: {max(numeric_values) - min(numeric_values)}")


def demonstrate_logging():
    """Demonstrate data logging capabilities"""
    print("="*60)
    print("PV Data Logger Demonstration")
    print("="*60)
    
    # Start logging
    logger = PVDataLogger("bradm:aSubExample")
    
    # Wait for connection
    if not logger.pv.wait_for_connection(timeout=5.0):
        print("Failed to connect to PV")
        return
    
    # Generate some test data
    print("\nGenerating test data for 10 seconds...")
    pv_writer = PV("bradm:aSubExample")
    
    start_time = time.time()
    counter = 0
    
    try:
        while time.time() - start_time < 10:
            # Write varying values
            value = 50 + 20 * ((counter % 10) - 5)
            pv_writer.put(value)
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLogging interrupted by user")
    
    # Get statistics
    stats = logger.get_summary_statistics()
    if stats:
        print("\n" + "="*60)
        print("Logging Statistics")
        print("="*60)
        print(f"Total samples: {stats['count']}")
        print(f"Min value: {stats['min']}")
        print(f"Max value: {stats['max']}")
        print(f"Average value: {stats['avg']:.2f}")
        print(f"Value range: {stats['range']}")
    
    # Stop and save
    logger.stop_logging()
    pv_writer.disconnect()
    
    # Analyze the saved file
    print("\n" + "="*60)
    print("Analyzing saved data...")
    print("="*60)
    time.sleep(1)
    DataAnalyzer.analyze_csv(logger.csv_file)


def main():
    """Main function"""
    try:
        demonstrate_logging()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. MyProject IOC is running")
        print("2. PV names match your hostname")


if __name__ == "__main__":
    main()

import time
import sys
import random
import concurrent.futures
from datetime import datetime
from epics import caput

NUM_TARGETS = 36
PULSE_FREQUENCY = 14.0
IOC_PREFIX = "bradm"
PVS = {
    "temp1": f"{IOC_PREFIX}:TARGET:TEMP1",
    "temp2": f"{IOC_PREFIX}:TARGET:TEMP2",
    "temp3": f"{IOC_PREFIX}:TARGET:TEMP3",
    "temp4": f"{IOC_PREFIX}:TARGET:TEMP4",
    "rot_speed": f"{IOC_PREFIX}:TARGET:ROT_SPEED",
    "position": f"{IOC_PREFIX}:TARGET:POSITION",
    "cool_flow": f"{IOC_PREFIX}:TARGET:COOL_FLOW",
    "cool_temp_in": f"{IOC_PREFIX}:TARGET:COOL_TEMP_IN",
    "cool_temp_out": f"{IOC_PREFIX}:TARGET:COOL_TEMP_OUT",
    "power": f"{IOC_PREFIX}:TARGET:POWER",
    "beam_current": f"{IOC_PREFIX}:TARGET:BEAM_CURRENT",
    "neutron_rate": f"{IOC_PREFIX}:TARGET:NEUTRON_RATE",
    "vibration": f"{IOC_PREFIX}:TARGET:VIBRATION",
    "pulse_count": f"{IOC_PREFIX}:TARGET:PULSE_COUNT",
    "timestamp": f"{IOC_PREFIX}:TARGET:TIMESTAMP",
}


class TargetSimulator:
    def __init__(self):
        self.temps = [680.0, 685.0, 675.0, 690.0]
        self.cooling_flow = 45.0  # L/min
        self.cooling_temp_in = 18.0  # C
        self.beam_current = 50.0  # uA
        self.beam_power = 500.0  # kW
        self.rotation_speed = PULSE_FREQUENCY
        self.pulse_count = 0
        self.start_time = time.time()

    def update(self, position):
        for i in range(4):  # Add heat when position is near sensor
            heat_input = 0.5 if position % 9 == i * 2 else 0.0
            self.temps[i] += random.gauss(0, 0.5) + heat_input - 0.3
            self.temps[i] = max(600, min(850, self.temps[i]))
        self.cooling_flow = 45.0 + random.gauss(0, 1.0)
        self.cooling_flow = max(40, min(50, self.cooling_flow))
        temp_rise = self.beam_power / (self.cooling_flow * 4.186)
        self.cooling_temp_out = self.cooling_temp_in + temp_rise + random.gauss(0, 0.5)
        self.beam_current = 50.0 + random.gauss(0, 2.0)
        self.beam_current = max(0, min(100, self.beam_current))
        self.beam_power = 500.0 + random.gauss(0, 20.0)
        self.beam_power = max(0, self.beam_power)
        self.rotation_speed = PULSE_FREQUENCY + random.gauss(0, 0.05)
        self.pulse_count += 1

    def publish_to_epics(self, position):
        try:
            caput(PVS["temp1"], self.temps[0], wait=False)
            caput(PVS["temp2"], self.temps[1], wait=False)
            caput(PVS["temp3"], self.temps[2], wait=False)
            caput(PVS["temp4"], self.temps[3], wait=False)
            caput(PVS["rot_speed"], self.rotation_speed, wait=False)
            caput(PVS["position"], position, wait=False)
            caput(PVS["cool_flow"], self.cooling_flow, wait=False)
            caput(PVS["cool_temp_in"], self.cooling_temp_in, wait=False)
            caput(PVS["cool_temp_out"], self.cooling_temp_out, wait=False)
            caput(PVS["power"], self.beam_power, wait=False)
            caput(PVS["beam_current"], self.beam_current, wait=False)
            caput(PVS["neutron_rate"], self.beam_power * 1e13, wait=False)
            caput(
                PVS["vibration"],
                max(0, 1.0 + (sum(self.temps) / 4 - 680) / 100),
                wait=False,
            )
            caput(PVS["pulse_count"], self.pulse_count, wait=False)
            caput(
                PVS["timestamp"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                wait=False,
            )
        except Exception as e:
            print(f"\nWarning: Could not publish to EPICS: {e}")


def main():
    print("Tungsten Target Monitor")
    print("Press Ctrl+C to exit\n")

    simulator = TargetSimulator()
    epics_executor = concurrent.futures.ThreadPoolExecutor()
    last_publish_time = 0
    publish_interval = 0.5

    try:
        while True:
            elapsed = time.time() - simulator.start_time
            position = round(elapsed / (1 / PULSE_FREQUENCY)) % NUM_TARGETS
            simulator.update(position)

            if elapsed - last_publish_time >= publish_interval:
                epics_executor.submit(simulator.publish_to_epics, position)
                last_publish_time = elapsed

            line = ""
            for i in range(NUM_TARGETS):
                if i == position:
                    line += "◯ "  # Active target
                else:
                    line += "• "  # Inactive target

            avg_temp = sum(simulator.temps) / 4
            if avg_temp > 750:
                temp_str = f"\033[91m{avg_temp:.0f}K\033[0m"  # Red
            elif avg_temp > 700:
                temp_str = f"\033[93m{avg_temp:.0f}K\033[0m"  # Yellow
            else:
                temp_str = f"\033[92m{avg_temp:.0f}K\033[0m"  # Green

            sys.stdout.write(
                f"\r{line} | "
                f"t={elapsed:.1f}s | "
                f"T={temp_str} | "
                f"P={simulator.beam_power:.0f}kW | "
                f"I={simulator.beam_current:.1f}uA | "
                f"Flow={simulator.cooling_flow:.1f}L/m  "
            )
            sys.stdout.flush()

            time.sleep(0.016)  # ~60 FPS

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
        print(f"Total pulses: {simulator.pulse_count}")
        sys.exit(0)


if __name__ == "__main__":
    main()

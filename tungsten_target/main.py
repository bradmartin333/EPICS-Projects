import time
import sys
import random

NUM_TARGETS = 36
PULSE_FREQUENCY = 14.0


def clear_line():
    sys.stdout.write("\r")
    sys.stdout.flush()


def main():
    print("Tungsten Target Monitor")
    print("Press Ctrl+C to exit\n")

    temperature = 680.0
    start_time = time.time()

    try:
        while True:
            elapsed = time.time() - start_time
            interval = round(elapsed / (1 / PULSE_FREQUENCY)) % NUM_TARGETS

            temperature += random.gauss(0, 0.1)
            temperature = max(600, min(800, temperature))

            line = ""
            for i in range(NUM_TARGETS):
                if i == interval:
                    line += "◯ "  # Active target
                else:
                    line += "• "  # Inactive target

            if temperature > 700:
                temp_str = f"\033[93m{temperature:.0f}K\033[0m"  # Yellow
            elif temperature > 770:
                temp_str = f"\033[91m{temperature:.0f}K\033[0m"  # Red
            else:
                temp_str = f"\033[92m{temperature:.0f}K\033[0m"  # Green

            sys.stdout.write(f"\r{line} {elapsed:.3f}s {temp_str} ")
            sys.stdout.flush()
            time.sleep(0.016)  # ~60 FPS

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()

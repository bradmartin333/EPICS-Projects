# Beam Dump

Mock control of proton beam dump with debug visualization

## Setup

1. Install uv with PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
1. `uv sync`

## Usage

`uv run main.py`

## Demo

Trying to reduce RMS radius of artificially off-center beam at dump location by adjusting steering magnets. An automatic optimization loop would be needed to adjust the magnet settings to minimize the beam size at the dump, but this is just a demo of the visualization with some artificial jitter added to the magnet settings. Effective magnet kick shown as yellow vector. 

![Demo](./beam_dump_sim.gif)

Example state that would be packaged up properly and sent to the IOC:

```json
{
  "timestamp": 5.7010374,
  "target_distribution": {
    "mean_x": 0.20512467148147648,
    "mean_y": 0.5891563458149524,
    "std_x": 0.11529986253744536,
    "std_y": 0.25375506240908496,
    "rms_radius": 0.6832766794379885,
    "max_deviation": 1.266784920051739,
    "total_particles": 234
  },
  "magnets": [
    {
      "name": "Injector Corrector",
      "z_position": 0.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 0.8,
      "is_corrector": true
    },
    {
      "name": "H-Corrector 1",
      "z_position": 12.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 1.0,
      "is_corrector": true
    },
    {
      "name": "V-Corrector 1",
      "z_position": 24.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 1.0,
      "is_corrector": true
    },
    {
      "name": "H-Corrector 2",
      "z_position": 36.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 1.2,
      "is_corrector": true
    },
    {
      "name": "Final Corrector",
      "z_position": 48.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 1.0,
      "is_corrector": true
    },
    {
      "name": "Beam Dump",
      "z_position": 60.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": 0.0,
      "strength": 0.0,
      "is_corrector": false
    }
  ]
}
```

is printed with `camonitor bradm:DUMP:RMS_RADIUS bradm:DUMP:MEAN_X bradm:STEER:INJ:KICK_X`:

```
bradm:DUMP:MEAN_X              2025-12-17 21:15:03.994990 0.209073
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:04.085161 0.660418 HIGH MINOR
bradm:STEER:INJ:KICK_X         2025-12-17 21:15:04.194113 0
bradm:DUMP:MEAN_X              2025-12-17 21:15:08.416966 0.205196
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:08.438693 0.690471 HIGH MINOR
bradm:DUMP:MEAN_X              2025-12-17 21:15:08.933329 0.204785
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:08.952903 0.684183 HIGH MINOR
bradm:DUMP:MEAN_X              2025-12-17 21:15:09.449118 0.207382
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:09.473527 0.684 HIGH MINOR
bradm:DUMP:MEAN_X              2025-12-17 21:15:09.961843 0.209653
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:09.987480 0.68965 HIGH MINOR
bradm:DUMP:MEAN_X              2025-12-17 21:15:10.485095 0.207913
bradm:DUMP:RMS_RADIUS          2025-12-17 21:15:10.508157 0.688408 HIGH MINOR
```

which means I should probably adjust HOPR/LOPR...

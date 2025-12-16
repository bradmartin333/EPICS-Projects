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

Example state that would be packaged up properly and sent to the IOC

```json
{
  "timestamp": 15.3306133,
  "target_distribution": {
    "mean_x": 0.030970292382324228,
    "mean_y": 0.12887002361928068,
    "std_x": 0.1154094286576893,
    "std_y": 0.24238491212765256,
    "rms_radius": 0.2993934265278794,
    "max_deviation": 0.6685273265722469,
    "total_particles": 76
  },
  "magnets": [
    {
      "name": "Injector Corrector",
      "z_position": 0.0,
      "kick_x_mrad": -2.5,
      "kick_y_mrad": -5.5,
      "strength": 0.8,
      "is_corrector": true
    },
    {
      "name": "H-Corrector 1",
      "z_position": 12.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": -2.5,
      "strength": 1.0,
      "is_corrector": true
    },
    {
      "name": "V-Corrector 1",
      "z_position": 24.0,
      "kick_x_mrad": 0.0,
      "kick_y_mrad": -2.0,
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
      "kick_x_mrad": -2.5,
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
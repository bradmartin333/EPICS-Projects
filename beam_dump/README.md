# Beam Dump

Mock control of proton beam dump with debug visualization

## Setup

1. Install uv with PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
1. `uv sync`

## Usage

`uv run main.py`

## Demo

Trying to reduce RMS radius of artificially off-center beam at dump location by adjusting steering magnets.

Effective magnet kick shown as yellow vector.

![Demo](./beam_dump_dim.gif)

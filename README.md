# EPICS-Projects

- Learning with the Experimental Physics and Industrial Control System
- Most of these instructions are found in the [documentation](https://docs.epics-controls.org/en/latest/index.html#)
- See the subdirectories in this repository for more

## Windows 11 Setup

Freshly imaged system: i5-10400 @ 2.90GHz

### Building EPICS base

1. [Download latest EPICS base release from GitHub](https://github.com/epics-base/epics-base/releases)
    - Unzip into working directory
1. [Download latest Strawberry Perl .msi](https://strawberryperl.com/)
    - Open executable and install
    - Add `C:\Strawberry\c\bin` to PATH (For `gmake`)
1. [Download the Visual Studio 2019 Professional Installer](https://download.visualstudio.microsoft.com/download/pr/46bb5918-5ff1-4e1c-9090-bbc63baa33b6/1670cb87e49c7e1f1c777f4a56cda6777182171f20d01c70da6e166a4fb61af6/vs_Professional.exe)
    - Community is no longer available 
    - Open executable and install “Desktop development with C++” (Can uncheck most options)
    - Copy "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional" to "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community"
    - Good to reboot now
1. Open “Command Prompt” (Not PowerShell) in the EPICS base root directory
1. `set EPICS_HOST_ARCH=windows-x64`
1. `"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64`
1. `gmake -j6` (My computer has 6 cores)
1. Add “bin\windows-x64” full directory to PATH and as env var EPICS_BASE

### Create and Run IOC

1. Create working directory and open PowerShell at root
1. Create the app directory: `perl $env:EPICS_BASE\makeBaseApp.pl -t example MyProject`
1. Create the app files `perl $env:EPICS_BASE\makeBaseApp.pl -i -t example MyProject`
1. Close PowerShell and use Command Prompt from now on
    - Make the same way in the above section (#4 - #7)
1. Start IOC: `path\to\MyProject\bin\windows-x64\MyProject.exe .\iocBoot\iocMyProject\st.cmd`
1. List channels: `epics> dbl`
1. Open a new PowerShell while IOC is running
1. Test connection caget: `bradm:aiExample`
1. Test writing data: `caput bradm:aSubExample 42`
1. Test monitor with write: `camonitor bradm:aSubExample`

## Goals

EPICS is typically used in conjunction with NICOS, which is a control system for neutron scattering experiments. Data is then posted to kafka and later read into scipp before anaysis and storage in a database.

For this project, I would like to create a simple GUI for monitoring and controlling the EPICS IOC. Then, I want to create some simulated CA clients on different devices (RaspberryPi, Laptop, Phone). The UI will show device states (Online/Error/Offline).

Then, I want to create some mock data. This can be done on the same Windows PC for ease of development. Not sure how far I will get with this, but I would like to simulate:

- Vacuum pressures
- RF signals to simulate a klystron gallery
- Cryogenic temp sensors with PID setpoint control
- Refrigeriant loops
- [Beam position monitor](./beam_dump/)
- [Tungsten target monitor](./tungsten_target/)

This will likely all be accomplished with python, but I may get fancy and either access the IOC database directly or wrap the IOC header files in a WASM app or FFI for a different frontend.

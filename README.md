# gortparatus
Sound Blaster Live in a box

## Prerequisites
- Computer with some flavor of NT 5.1 (e.g. Windows XP) and a Creative Soundfont Device (SB Live)
- [Python 3.4.4](https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi)
- [MidiPlayer 6.1](http://web.archive.org/web/20220608030347/https://falcosoft.hu/midiplayer_61.zip) (to access patch names from loaded Soundfonts)
- [pywin32 build 221](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20221/pywin32-221.win-amd64-py3.4.exe/download) (to automaticaly retrieve patch names from MidiPlayer)
- [rtmidi 1.1.0](https://files.pythonhosted.org/packages/7c/0b/6fb1c8d1a00ae8347800b8a1fdfa06595fa952420b9ee6013fb878e950e5/python_rtmidi-1.1.0-cp34-cp34m-win32.whl) (for MIDI handling)
- [USBLCDServer for picoLCD](http://resources.mini-box.com/online/picoLCD%2020x2%20(OEM)/Software/Windows/usblcd-applications.zip)

## Setup
### Installation
- Clone master and unzip root files to some directory. e.g.: `C:\Synth`
- Download USBLCDServer and unzip to some directory. e.g.: `C:\Synth\picoLCD`
- Download MidiPlayer 6.1 and unzip to some directory. e.g.: `C:\MidiPlayer` (Note: This is only used during configuration.)
- Install Python 3.4.4. Be sure to tick the option to add Python to system PATH during installation.
- Install pywin32 build 221
- Rename `rtmidi-1.1.0-cp34-cp34m-win32.whl` to `python_rtmidi-1.1.0-cp34-none-any.whl`
- Install rtmidi using pip: `pip install python_rtmidi-1.1.0-cp34-none-any.whl`
### Configuration
- Run `get-ports.py`. All available MIDI ports on the system are displayed. The trailing digit is the ID of the port.
- Open `gort.cfg` using Notepad, and set the value for `In` to the ID for your desired MIDI port. e.g.: `In = 0`
- Run MidiPlayer 6.1. Then, run `get_patch_names.py`

### Final steps
- Navigate to your startup directory. e.g.: `C:\Documents and Settings\[Your Username]\Start Menu\Programs\Startup`
- Create a shortcut for `USBLCDServer.exe` in your startup directory.
- Create a shortcut for `GORT_SYNTH.py` in your startup directory.

## Files overview
### Scripts
- GORT_SYNTH.py - main application that does everything important. Run at boot time or whenever you wish. Requires that USBLCDServer also be running.
- get_patch_names.py - dump all patch names into .json files. Requires that MidiPlayer also be running.
- get_ports.py - show all the midi ports available on the system (this is needed to set up gort.cfg)

### Libraries
- MidiPlayer.py - library for messing with window elements on Falcosoft's MIDI Player application, used as a workaround hack for retrieving SBLive patch names, includes some unused features for grabbing and setting program/bank/channel.
- minibox.py - picoLCD library. `from minibox import picoLCD`

### Other files
- gmp_profile.json - used for MidiPlayer.py in case you have your own version and need to get the handle child numbers yourself.
- gort.cfg - config file that specifies midi in/out devices.
- program_names_melodic.json - list of melodic program names dumped from MidiPlayer
- program_names_pecussion.json - list of percussion names dumped from MidiPlayer
- __extras/__ - media created for the author's specific use case
- __extras/artwork/__ - custom splash
- __extras/patch-listings/__ - pages containing all programs used on the author's synth
- __support/__ gortparatus.ins - Cakewalk instrument list for the author's synth

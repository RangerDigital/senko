# Senko - OTA Update Agent
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

The simplest **OTA** solution for your **Micropython** project.
For more information visit [**Senko**](https://senko.bednarski.dev) official website.

Developed and tested on **ESP8266**, but should work fine on other boards.

>This project was made for small projects, Using it for commercial products is risky, especially on ESP8266.


## Installation

Senko is single **Micropython** module that you import.

Use **Ampy** or **WebREPL** to load **/bin/senko.py** module to the root of your filesystem.

```bash
sudo ampy -p /dev/ttyUSB0 put bin/senko.py
```

## Usage

> For more details visit [**Senko**](https://senko.bednarski.dev) official website.

Senko agent is flexible, that means you are responsible for network connections and reboots.

To start, create Senko object:

Example: **Senko("https://raw.githubusercontent.com/RangerDigital/senko-ota/master/bin/", ["boot.py", "main.py"])**

* **URL** of your OTA source root.
* **Files** that you want to track and update.
* **HTTP Headers** (optional) that will be sent with every request.



Use **Senko.fetch()** to check for changes between remote and local files.

Use **Senko.update()** to replace local files with remote ones if changes are detected. Senko supports per file updates.

>Supports GitHub public repos via raw.githubusercontent.com and custom OTA servers. You can ever use branches to further control deployments.

```python
import senko

# connect_wlan()

OTA = senko.Senko("https://raw.githubusercontent.com/RangerDigital/senko-ota/master/bin/", ["boot.py", "main.py"])

if OTA.update():
    print("OTA Updated to latest version!")
    # reboot()
```

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

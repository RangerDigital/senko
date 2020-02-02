<p align="center">
  <br /><img
    width="600"
    src="logo.png"
    alt="Senko – OTA Updater"
  />
</p>

***

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Senko is the simplest **Over The Air** updater solution for your **Micropython** projects based on **ESP8266** and **ESP32** microcontrollers. Senko synchronizes selected files on your microcontroller with the **GitHub** repository.

>🚧 By all means, Senko is not the best implementation, but for my simple IoT projects, It was adequate!

I used Senko to automatically deploy the latest `master` branch to my ESP8266 fleet using  `raw.githubusercontent.com`.

<br>

## 🛠 How Senko Works
Every time `.fetch()` or `.update()` methods are called Senko compares **SHA1** hashes of local files with remote ones to determine if they are the same.

If they are not, Senko saves remote files from GitHub to your microcontroller. This means you need to reboot to run the latest code.

>🚧 You are responsible for implementing a network connection and reboot strategy!

<br>

## 🔥 Installation
Senko consists of a single `senko.py` module that you import.

You can use **Ampy** or **WebREPL** to load `/senko/senko.py` module to your microcontroller:

```bash
sudo ampy -p /dev/ttyUSB0 put senko.py
```

<br>

## 🎉 Usage
You should start by importing the module and creating a `Senko` object.

You have to specify **URL** to the **GitHub** directory containing your code and **files** that you want to keep synchronized.

```python
# boot.py
import senko

GITHUB_URL = "https://github.com/RangerDigital/senko/blob/master/examples/"
OTA = senko.Senko(GITHUB_URL, ["boot.py", "main.py"])
```

To get that **URL** simply click the `RAW` button on one of the files that you want to track and then strip the name of that file from it.

>💡 You can even specify what branch Senko will update from!

Then after connecting to Wi-Fi network call `OTA.update()`:
```python
# boot.py
import senko
import machine
import network

GITHUB_URL = "https://github.com/RangerDigital/senko/blob/master/example/"
OTA = senko.Senko(GITHUB_URL, ["boot.py", "main.py"])

# Connect to Wi-Fi network.
connect_wlan()

if OTA.update():
    print("Updated to the latest version! Rebooting...")
    machine.reset()
```
This setup will try to keep `boot.py` and `main.py` updated every time microcontroller boots.

If you only want to check if the newer version of files exists call `OTA.fetch()`:
```python
if OTA.fetch():
    print("A newer version is available!")
else:
    print("Up to date!")
```

Check out a simple example of usage from `examples` directory!

<br>

## 📃 License
This project is licensed under [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) .

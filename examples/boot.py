import gc
import machine
import network
import upip


def connect_wlan(ssid, password):
    """Connects build-in WLAN interface to the network.
    Args:
        ssid: Service name of Wi-Fi network.
        password: Password for that Wi-Fi network.
    Returns:
        True for success, Exception otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    return True


def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """

    gc.collect()
    gc.enable()

    # Wi-Fi credentials
    SSID = ""
    PASSWORD = ""

    connect_wlan(SSID, PASSWORD)

    # Install Senko from PyPi
    upip.install("micropython-senko")

    import senko
    OTA = senko.Senko(user="RangerDigital", repo="senko", working_dir="examples", files=["main.py"])

    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()


if __name__ == "__main__":
    main()

# import requests as urequests
# import hashlib as uhashlib

import urequests
import uhashlib



class Senko:
    def __init__(self, url, files=[], username=None, password=None, debug=False):
        self.url = url
        self.debug = debug

        self.username = username
        self.password = password

        self.files = files

    def _debug(self, *args):
        if self.debug:
            for arg in args:
                print(arg + " ")

    def _check_hash(self, x, y):
        self._debug("DEBUG: Checking hashes!")
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())

        x = x_hash.digest()
        y = y_hash.digest()

        self._debug("DEBUG: Latest version HASH:", x)
        self._debug("DEBUG: Local version HASH:", y)

        if str(x) == str(y):
            self._debug("DEBUG: Files the same!")
            return True
        else:
            self._debug("DEBUG: Files NOT the same!")
            return False

    def _check_all(self):
        self._debug("DEBUG: _check_all running!")
        changed_files = []

        for file in self.files:
            self._debug("DEBUG: Checking files:", file)
            latest_version = urequests.get(self.url + file).text

            # self._debug("DEBUG: Latest file:")
            # self._debug(latest_version)

            try:
                local_file = open(file, "r")
                local_version = local_file.read()
                local_file.close()

            except:
                local_version = ""

            # self._debug("DEBUG: Local file:")
            # self._debug(local_version)

            if not self._check_hash(latest_version, local_version):
                changed_files.append(file)

        self._debug("DEBUG: Changed files:")
        self._debug(changed_files)

        return changed_files

    def fetch(self):
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        changed_files = self._check_all()
        for file in changed_files:
            self._debug("DEBUG: Updating file:", file)
            local_file = open(file, "w")
            local_file.write(urequests.get(self.url + file).text)
            local_file.close()

        if self._check_self(changed_files):
            self._debug("DEBUG: Auto update detected!")
            self._debug("Reboot!")

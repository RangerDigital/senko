# import requests as urequests
# import hashlib as uhashlib

import urequests
import uhashlib



class Senko:
    def __init__(self, url, files=[], username=None, password=None):
        self.url = url

        self.username = username
        self.password = password

        self.files = files

        print("DEBUG: Class URL:", self.url)

    def _check_hash(self, x, y):
        print("DEBUG: Checking hashes!")
        x = uhashlib.sha1(x.encode())
        y = uhashlib.sha1(y.encode())

        x = x.digest()
        y = y.digest()

        print("DEBUG: Latest version HASH:", x)
        print("DEBUG: Local version HASH:", y)

        if x == y:
            return True
        else:
            return False

    def _check_all(self):
        print("DEBUG: _check_all running!")
        changed_files = []

        for file in self.files:
            print("DEBUG: Checking files:", file)
            latest_version = urequests.get(self.url + file).text

            print("DEBUG: Latest file:")
            print(latest_version)

            try:
                local_file = open(file, "r")
                local_version = local_file.read()
                local_file.close()

            except FileNotFound:
                local_version = ""

            print("DEBUG: Local file:")
            print(local_version)

            if not self._check_hash(latest_version, local_version):
                changed_files.append(file)

        print("DEBUG: Changed files:")
        print(changed_files)

        return changed_files

    def fetch(self):
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        for file in self._check_all():
            print("DEBUG: Updating file:", file)
            local_file = open(file, "w")
            local_file.write(urequests.get(self.url + file).text)
            local_file.close()
        return True

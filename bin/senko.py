import requests as urequests
import hashlib as uhashlib


def why():
    print("Because why not?")

class Test:
    def __init__(self, x, y):

        self.x = x
        self.y = y

class Senko:
    def __init__(self, url, files=[], username=None, password=None):
        self.url = url

        self.username = username
        self.password = password

        self.files = files

    def _check_hash(self, x, y):
        x = uhashlib.sha1(x.encode())
        y = uhashlib.sha1(y.encode())

        if x.digest() == y.digest():
            return True
        else:
            return False

    def _check_all(self):
        changed_files = []

        for file in self.files:
            latest_version = urequests.get(self.url + file).text

            try:
                local_file = open(file, "r")
                local_version = local_file.read()
                local_file.close()

            except FileNotFound:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changed_files.append(file)

        return changed_files

    def fetch(self):
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        for file in self._check_all():
              local_file = open(file, "w")
              local_file.write(urequests.get(self.url + file).text)
              local_file.close()
        return True

x = Senko("ok", ["boot.py"])
print(x.files)

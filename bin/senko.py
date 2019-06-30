import urequests
import uhashlib


class Senko:
    def __init__(self, url, files=[], headers=[], debug=False):
        self.url = url
        self.headers = headers

        self.debug = debug

        self.files = files

    def _debug(self, msg):
        if self.debug:
            print(msg)

    def _check_hash(self, x, y):
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())

        x = x_hash.digest()
        y = y_hash.digest()

        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        payload = urequests.get(url, headers=self.headers)
        code = payload.status_code

        if code == 200:
            return payload.text
        else:
            self._debug("Request returned error code, " + str(code))
            return None

    def _check_all(self):
        changes = []

        for file in self.files:
            latest_version = self._get_file(self.url + file)
            if latest_version is None:
                return []

            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)

        return changes

    def fetch(self):
        if not self._check_all():
            self._debug("No changes detected!")
            return False
        else:
            self._debug("Changes detected!")
            return True

    def update(self):
        self._debug("Updating...")
        changes = self._check_all()

        for file in changes:
            self._debug("File: " + file)
            with open(file, "w") as local_file:
                local_file.write(self._get_file(self.url + file))

        if changes:
            self._debug("Done!")
            return True
        else:
            self._debug("No changes were made!")
            return False

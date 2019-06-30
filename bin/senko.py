import urequests
import uhashlib
import gc


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
        print(gc.mem_free())
        gc.collect()
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())
        print(gc.mem_free())
        x = x_hash.digest()
        y = y_hash.digest()
        print(gc.mem_free())
        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        print(gc.mem_free())
        gc.collect()
        payload = urequests.get(url, headers=self.headers)
        code = payload.status_code

        if code == 200:
            print(gc.mem_free())
            return payload.text
        else:
            self._debug("Request returned error code, " + str(code))
            return None

    def _check_all(self):
        changes = []

        for file in self.files:
            latest_version = self._get_file(self.url + file)
            print(gc.mem_free())
            if latest_version is None:
                return []

            print(gc.mem_free())
            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            print(gc.mem_free())
            if not self._check_hash(latest_version, local_version):
                changes.append(file)

        return changes

    def fetch(self):
        print(gc.mem_free())
        if not self._check_all():
            print(gc.mem_free())
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

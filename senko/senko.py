import mrequests as requests
import uhashlib
import gc
import os

def file_or_dir_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit("/", 1)
    if len(r) == 1:
        return ("", path)
    head = r[0] #.rstrip("/")
    if not head:
        head = "/"
    return (head, r[1])

def dirname(path):
    return split(path)[0]

class Senko:
    raw = "https://raw.githubusercontent.com"
    github = "https://github.com"

    def __init__(self, user, repo, url=None, branch="master", working_dir="app", files=["boot.py", "main.py"], headers={}, cleanup=[], buffersize=4096, debug=False):
        """Senko OTA agent class.

        Args:
            user (str): GitHub user.
            repo (str): GitHub repo to fetch.
            branch (str): GitHub repo branch. (master)
            working_dir (str): Directory inside GitHub repo where the micropython app is.
            url (str): URL to root directory.
            files (list): Files included in OTA update.
            headers (list, optional): Headers for urequests,
                e.g. 'Authorization': 'token {}'.format(token)
            cleanup (list, optional): Paths to clean up (delete)
            buffersize (number, optional): Buffer size in bytes.
            debug (boolean, optional): Print debug information
        """
        self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        self.headers = headers
        self.files = files
        self.cleanup = cleanup
        self.debug = debug
        self.buffersize = buffersize


    def _stream_to_hash(self, stream):
        hasher = uhashlib.sha1()
        while True:
            gc.collect()
            data = stream.read(self.buffersize)
            if not data:
                break
            hasher.update(data)
        digest = hasher.digest()
        return digest

    def _compute_file_hash(self, file):
        digest = ""
        try:
            reader = open(file, 'rb')
            digest = self._stream_to_hash(reader)
            reader.close()
        except Exception as e:
            if self.debug:
                print('missing file', file, e)
        if self.debug:
            print('_compute_file_hash', file, digest)
        return digest

    def _compute_url_hash(self, url):
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            if self.debug:
                print('URL not loaded', url, r.status_code)
            return None

        digest = self._stream_to_hash(r)
        if self.debug:
            print('_compute_url_hash', url, digest)
        return digest

    def _stream_url_to_file(self, url, file):
        try:
            r = requests.get(url, headers=self.headers)
            if r.status_code != 200:
                if self.debug:
                    print('URL not loaded', url, r.status_code)
                return None

            path = dirname(file)
            if not file_or_dir_exists(path):
                os.mkdir(path)

            with open(file, 'wb') as writer:
                # print('writer', writer)
                while True:
                    gc.collect()
                    data = r.read(self.buffersize)
                    if not data:
                        break
                    writer.write(data)
            return None
        except Exception as e:
            if self.debug:
                print('write error', url, file, e)
            return None

        if self.debug:
            print('_stream_url_to_file', file, url)


    def _check_all(self):
        changes = []

        for file in self.files:
            gc.collect()
            local_hash = self._compute_file_hash(file)
            latest_hash = self._compute_url_hash(self.url + "/" + file)

            if str(local_hash) != str(latest_hash):
                changes.append(file)

        if self.debug:
            print("found changes", changes)
        return changes

    def fetch(self):
        """Check if newer version is available.

        Returns:
            True - if is, False - if not.
        """
        if not self._check_all():
            return False

        return True

    def update(self):
        """Replace all changed files with newer one.

        Returns:
            True - if changes were made, False - if not.
        """
        changes = self._check_all()

        for file in changes:
            gc.collect()
            if self.debug:
                print("writing to", file)
            self._stream_url_to_file(self.url + "/" + file, file)

        for file in self.cleanup:
            if self.debug:
                print("removing file", file)
            try:
                os.remove(file)
            except Exception as e:
                if self.debug:
                    print("failed to remove file", file, e)

        if changes:
            return True

        return False

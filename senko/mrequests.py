"""A HTTP client module for MicroPython with an API similar to requests."""

import sys

try:
    import socket
except ImportError:
    import usocket as socket


MICROPY = sys.implementation.name == "micropython"
MAX_READ_SIZE = 4 * 1024


def encode_basic_auth(user, password):
    from ubinascii import b2a_base64

    auth_encoded = b2a_base64(b"%s:%s" % (user, password)).rstrip(b"\n")
    return {b"Authorization": b"Basic %s" % auth_encoded}


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)


def parse_url(url):
    port = None
    host = None

    # str.partition() would be handy here,
    # but it's not supported on the esp8266 port
    delim = url.find("//")
    if delim >= 0:
        scheme, loc = url[:delim].rstrip(':'), url[delim+2:]
    else:
        loc = url
        scheme = ""

    psep = loc.find("/")
    if psep == -1:
        if scheme:
            host = loc
            path = "/"
        else:
            path = loc
    elif psep == 0:
        path = loc
    else:
        path = loc[psep:]
        host = loc[:psep]

    if host:
        hsep = host.rfind(":")

        if hsep > 0:
            port = int(host[hsep + 1 :])
            host = host[:hsep]

    return scheme or None, host, port, path


class RequestContext:
    def __init__(self, url, method=None):
        self.redirect = False
        self.method = method or "GET"
        self.scheme, self.host, self._port, self.path = parse_url(url)
        if not self.scheme or not self.host:
            raise ValueError("An absolute URL is required.")

    @property
    def port(self):
        return self._port if self._port is not None else 443 if self.scheme == "https" else 80

    @property
    def url(self):
        return "%s://%s%s" % (
            self.scheme,
            self.host if self._port is None else ("%s:%s" % (self.host, self.port)),
            self.path,
        )

    def set_location(self, status, location):
        if status in (301, 302, 307, 308):
            self.redirect = True
        elif status == 303 and self.method != "GET":
            self.redirect = True

        if self.redirect:
            scheme, host, port, path = parse_url(location)

            if scheme and self.scheme == "https" and scheme != "https":
                self.redirect = False
                return

            if status not in (307, 308) and self.method != "HEAD":
                self.method = "GET"

            if scheme:
                self.scheme = scheme
            if host:
                self.host = host
                self._port = port

            if path.startswith("/"):
                self.path = path
            else:
                self.path = self.path.rsplit("/", 1)[0] + "/" + path


class Response:
    def __init__(self, sock, sockfile, save_headers=False):
        self.sock = sock
        self.sf = sockfile
        self.encoding = "utf-8"
        self._cached = None
        self._chunk_size = 0
        self._content_size = 0
        self.chunked = False
        self.status_code = None
        self.reason = ""
        self.headers = [] if save_headers else None

    def read(self, size=MAX_READ_SIZE):
        sf = self.sf

        if self.chunked:
            if self._chunk_size == 0:
                l = sf.readline().strip()

                if not l:
                    return b''

                # ignore chunk extensions
                l = l.split(b";", 1)[0]
                self._chunk_size = max(0, int(l, 16))

                if self._chunk_size == 0:
                    # End of message
                    sep = sf.read(2)
                    if sep != b"\r\n":
                        raise ValueError("Expected final chunk separator, read %r instead." % sep)

                    return b""

            data = sf.read(min(size or MAX_READ_SIZE, self._chunk_size))
            self._chunk_size -= max(0, len(data))

            if self._chunk_size == 0:
                sep = sf.read(2)
                if sep != b"\r\n":
                    raise ValueError("Expected chunk separator, read %r instead." % sep)

            return data
        else:
            if size:
                return sf.read(size)
            else:
                return sf.read(self._content_size)

    def save(self, fn, chunk_size=1024):
        read = 0

        with open(fn, "wb") as fp:
            while True:
                if self.chunked:
                    chunk = self.read()
                else:
                    remain = self._content_size - read

                    if remain <= 0:
                        break

                    chunk = self.read(min(chunk_size, remain))

                read += len(chunk)

                if not chunk:
                    break

                fp.write(chunk)

        self.close()

    def _parse_header(self, data):
        if data[:18].lower() == b"transfer-encoding:" and b"chunked" in data[18:]:
            self.chunked = True
            # print("Chunked response detected.")
        elif data[:15].lower() == b"content-length:":
            self._content_size = int(data.split(b":", 1)[1])
            # print("Content length: %i" % self._content_size)

    # overwrite this method, if you want to process/store headers differently
    def add_header(self, data):
        self._parse_header(data)

        if self.headers is not None:
            self.headers.append(data)

    def close(self):
        if not MICROPY:
            self.sf.close()
            self.sf = None
        if self.sock:
            self.sock.close()
            self.sock = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.read(size=None)
            finally:
                self.sock.close()
                self.sock = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson

        return ujson.loads(self.content)


def request(
    method,
    url,
    data=None,
    json=None,
    headers={},
    auth=None,
    encoding=None,
    response_class=Response,
    save_headers=False,
    max_redirects=1,
    timeout=None,
):
    if auth:
        headers.update(auth if callable(auth) else encode_basic_auth(auth[0], auth[1]))

    if json is not None:
        assert data is None
        import ujson

        data = ujson.dumps(json)

    ctx = RequestContext(url, method)

    while True:
        if ctx.scheme not in ("http", "https"):
            raise ValueError("Protocol scheme %s not supported." % ctx.scheme)

        ctx.redirect = False

        # print("Resolving host address...")
        ai = socket.getaddrinfo(ctx.host, ctx.port, 0, socket.SOCK_STREAM)
        ai = ai[0]

        # print("Creating socket...")
        sock = socket.socket(ai[0], ai[1], ai[2])
        sock.settimeout(timeout)
        try:
            # print("Connecting to %s:%i..." % (ctx.host, ctx.port))
            sock.connect(ai[-1])
            if ctx.scheme == "https":
                try:
                    import ssl
                except ImportError:
                    import ussl as ssl

                # print("Wrapping socket with SSL")
                create_ctx = getattr(ssl, 'create_default_context', None)
                if create_ctx:
                    sock = create_ctx().wrap_socket(sock, server_hostname=ctx.host)
                else:
                    sock = ssl.wrap_socket(sock, server_hostname=ctx.host)

            sf = sock if MICROPY else sock.makefile("rwb")
            sf.write(b"%s %s HTTP/1.1\r\n" % (ctx.method.encode("ascii"), ctx.path.encode("ascii")))

            if not b"Host" in headers:
                sf.write(b"Host: %s\r\n" % ctx.host.encode())

            for k, val in headers.items():
                sf.write(k if isinstance(k, bytes) else k.encode('ascii'))
                sf.write(b": ")
                sf.write(val if isinstance(val, bytes) else val.encode('ascii'))
                sf.write(b"\r\n")

            if data and ctx.method not in ("GET", "HEAD"):
                if json is not None:
                    sf.write(b"Content-Type: application/json")
                    if encoding:
                        sf.write(b"; charset=%s" % encoding.encode())
                    sf.write(b"\r\n")

                sf.write(b"Content-Length: %d\r\n" % len(data))

            sf.write(b"Connection: close\r\n\r\n")

            if data and ctx.method not in ("GET", "HEAD"):
                sf.write(data if isinstance(data, bytes) else data.encode(encoding or "utf-8"))

            if not MICROPY:
                sf.flush()

            resp = response_class(sock, sf, save_headers=save_headers)
            l = b""
            i = 0
            while True:
                l += sf.read(1)
                i += 1

                if l.endswith(b"\r\n") or i > MAX_READ_SIZE:
                    break

            # print("Response: %s" % l.decode("ascii"))
            l = l.split(None, 2)
            resp.status_code = int(l[1])

            if len(l) > 2:
                resp.reason = l[2].rstrip()

            while True:
                l = sf.readline()
                if not l or l == b"\r\n":
                    break

                if l.startswith(b"Location:"):
                    ctx.set_location(resp.status_code, l[9:].strip().decode("ascii"))

                # print("Header: %r" % l)
                resp.add_header(l)
        except OSError:
            sock.close()
            raise

        if ctx.redirect:
            # print("Redirect to: %s" % ctx.url)
            sock.close()
            max_redirects -= 1

            if max_redirects < 0:
                raise ValueError("Maximum redirection count exceeded.")

        else:
            break

    return resp

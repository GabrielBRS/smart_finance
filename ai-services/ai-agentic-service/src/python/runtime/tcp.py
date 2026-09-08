"""Runtime TCP listener. Loaded by CPython when Mojo calls python.runtime.tcp.

Mojo owns the accept loop, HTTP parsing, routing and use cases.
This module only binds/accepts/reads/writes bytes.

Why Python: Mojo 1.0 has no std.net. Later this can become libc FFI
in infrastructure/net without changing transport/http.
"""

from __future__ import annotations

import socket


class Listener:
    def __init__(self, host: str, port: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, int(port)))
        self._sock.listen(64)

    def accept(self) -> Connection:
        conn, _addr = self._sock.accept()
        return Connection(conn)

    def close(self) -> None:
        self._sock.close()


class Connection:
    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def recv_http(self) -> str:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self._sock.recv(4096)
            if not chunk:
                break
            data += chunk
        header, sep, rest = data.partition(b"\r\n\r\n")
        if not sep:
            return data.decode("utf-8", errors="replace")
        length = 0
        for line in header.split(b"\r\n")[1:]:
            if line.lower().startswith(b"content-length:"):
                length = int(line.split(b":", 1)[1].strip() or 0)
        body = rest
        while len(body) < length:
            chunk = self._sock.recv(min(4096, length - len(body)))
            if not chunk:
                break
            body += chunk
        return (header + sep + body).decode("utf-8", errors="replace")

    def sendall(self, data: str) -> None:
        self._sock.sendall(data.encode("utf-8"))

    def close(self) -> None:
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._sock.close()

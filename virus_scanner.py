import os
import socket

clamav_location = os.environ.get("CLAMAV_LOCATION", "localhost")
clamav_port = os.environ.get("CLAMAV_PORT", "3310")

chunk_size = 2048


# Returns False if viruses are detected on the path or results could not be determined
def scan_path(path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((clamav_location, 3310))

    file = open(path, "rb")
    s.send("zINSTREAM\0".encode("UTF-8"))

    try:
        chunk = file.read(chunk_size)

        while chunk != b'':
            size = len(chunk).to_bytes(4, "big")
            s.send(b''.join([size, chunk]))
            file.seek(chunk_size, 1)
            chunk = file.read(chunk_size)
    except Exception:
        data = s.recv(1024)
        print("connection aborted", repr(data))
        file.close()
        s.close()
        return False

    s.send((0).to_bytes(4, "big"))

    data = s.recv(1024).decode("UTF-8")
    file.close()
    s.close()

    result = data[len("stream: "):].strip("\x00")
    if result == "OK":
        return None
    if result.endswith(" FOUND"):
        return result.strip(" FOUND")

    return result

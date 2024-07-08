import time
import socket
import signal
import threading


class Reporter:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", 50000))
        self.last_beacon_at = {}
        self.host_to_message = {}
        self.host_added = False
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def get_hostname(self, addr):
        try:
            name, _, __ = socket.gethostbyaddr(addr)
            return name
        except socket.herror:
            return

    def is_beacon(self, message):
        return message.startswith("MuSync 1.0.0")

    def reciever(self):
        while not self.stop_event.is_set():
            data, addr = self.sock.recvfrom(1024)
            message = data.decode("utf-8")
            is_host = self.is_beacon(message)
            if not is_host:
                continue
            self.lock.acquire()
            if not addr in self.last_beacon_at:
                self.host_added = True
            self.last_beacon_at[addr] = time.time()
            self.host_to_message[addr] = message
            self.lock.release()

    def reporter(self):
        while not self.stop_event.is_set():
            self.lock.acquire()
            now = time.time()
            dead_hosts = [
                host
                for host in self.last_beacon_at
                if now - self.last_beacon_at[host] >= 6
            ]
            if self.host_added or dead_hosts:
                for host in dead_hosts:
                    del self.host_to_message[host]
                    del self.last_beacon_at[host]
                name_to_link = {}
                for (host, _), message in self.host_to_message.items():
                    try:
                        name = self.get_hostname(host) or host
                        port = int(message.split("\n")[1])
                        name_to_link[name] = f"http://{host}:{port}/ui/"
                    except (IndexError, ValueError):
                        pass
                print("\033[2J\033[H", end="")
                for name, link in name_to_link.items():
                    print(f"{link} ({name})")
                self.host_added = False
            self.lock.release()
            time.sleep(1)

    def init(self):
        signal.signal(signal.SIGINT, lambda sig, frame: self.stop_event.set())
        threading.Thread(target=self.reciever).start()
        threading.Thread(target=self.reporter).start()


Reporter().init()

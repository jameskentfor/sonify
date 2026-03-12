import json
from pythonosc.udp_client import SimpleUDPClient


class OscController:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            config = json.load(f)

        self.prefix = config["prefix"]
        self.client = SimpleUDPClient(config["host"], config["port"])

    def send(self, signal: dict):
        address = f"{self.prefix}/{signal['id']}"
        self.client.send_message(address, signal["value"])

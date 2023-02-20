# Class for properties

from pathlib import Path
from ast import literal_eval
import utils.app_tools as app_tools
from enum import Enum


def get_system_name() -> str:
    try:
        # uname doesn't exist in Windows...
        from os import uname
        return uname()[0].lower()
    except ImportError:
        return "nt"


def read_config() -> bool:
    global PROPERTIES_FILE, properties

    if not PROPERTIES_FILE.exists():
        write_config()

    contents = app_tools.read_file(PROPERTIES_FILE)

    if not contents:
        return False

    try:
        new_properties = dict_to_app_properties(literal_eval(contents))
    except KeyError:
        return False

    properties = new_properties

    return True


def write_config() -> bool:
    global CONFIG_DIRECTORY, PROPERTIES_FILE, properties

    if not CONFIG_DIRECTORY.exists():
        CONFIG_DIRECTORY.mkdir()

    data = properties.to_dict()

    return app_tools.write_file(PROPERTIES_FILE, str(data))


class ARPCommand(Enum):
    IP_A = 0
    ARP = 1
    ARPSPOOF = 2
    ARP_SCAN = 3


class AppProperties:
    def __init__(self):
        self.SYSTEM_NAME = get_system_name()

        if self.SYSTEM_NAME == "nt":
            self.ip_a_command = "ipconfig"
            self.arp_command = "arp /a"
            self.arpspoof_command = "arpspoof.exe"
        else:
            if self.SYSTEM_NAME == "darwin":
                self.ip_a_command = "ifconfig"
            else:
                self.ip_a_command = "ip a"

            self.arp_command = "arp -i %a -a"
            self.arpspoof_command = "arpspoof"

        self.arpspoof_path = ""

        self.arp_scan_command = "arp-scan"
        self.arp_scan_path = ""

    def to_dict(self) -> dict:
        return {
            "IP_A_COMMAND": self.ip_a_command,
            "ARP_COMMAND": self.arp_command,
            "ARPSPOOF_COMMAND": self.arpspoof_command,
            "ARPSPOOF_PATH": self.arpspoof_path,
            "ARP_SCAN_COMMAND": self.arp_scan_command,
            "ARP_SCAN_PATH": self.arp_scan_path
        }


def dict_to_app_properties(data: dict) -> AppProperties:
    new_properties = AppProperties()

    new_properties.ip_a_command = data["IP_A_COMMAND"]
    new_properties.arp_command = data["ARP_COMMAND"]
    new_properties.arpspoof_command = data["ARPSPOOF_COMMAND"]
    new_properties.arpspoof_path = data["ARPSPOOF_PATH"]
    new_properties.arp_scan_command = data["ARP_SCAN_COMMAND"]
    new_properties.arp_scan_path = data["ARP_SCAN_PATH"]

    return new_properties


CONFIG_DIRECTORY = Path().cwd().joinpath("config")
PROPERTIES_FILE = CONFIG_DIRECTORY.joinpath("data")
properties = AppProperties()

# App properties and configuration

from pathlib import Path
from ast import literal_eval
import utils.app_tools as app_tools
from enum import Enum


class ARPCommand(Enum):
    IP_A = 0
    ARP = 1
    ARPSPOOF = 2
    ARP_SCAN = 3


class AppProperties:
    def __init__(self):
        self.SYSTEM_NAME: str = get_system_name()
        self.IS_UNIX_LIKE_SYSTEM: bool = self.SYSTEM_NAME != "nt"

        if not self.IS_UNIX_LIKE_SYSTEM:
            self.ip_a_command = ""
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

        self.interface = ""
        self.router_ip = ""
        self.mdns_ip = ""
        self.allow_package_forwarding = False
        self.scan_every_arpspoof = False

        self.run_setup_in_startup = False
        self.setup_completed = False

    def reset_arpspoof(self):
        if not self.IS_UNIX_LIKE_SYSTEM:
            self.arpspoof_command = "arpspoof.exe"
        else:
            self.arpspoof_command = "arpspoof"

        self.arpspoof_path = ""


PROPERTIES = ["IP_A_COMMAND", "ARP_COMMAND", "ARPSPOOF_COMMAND", "ARPSPOOF_PATH", "ARP_SCAN_COMMAND", "ARP_SCAN_PATH",
              "INTERFACE", "ROUTER_IP", "MDNS_IP", "SCAN_EVERY_ARPSPOOF", "ALLOW_PACKAGE_FORWARDING",
              "RUN_SETUP_IN_STARTUP"]


def get_system_name() -> str:
    try:
        # uname doesn't exist in Windows...
        from os import uname
        return uname()[0].lower()
    except ImportError:
        return "nt"


def read_config() -> bool:
    global PROPERTIES_FILE, config

    from utils.net_tools import is_packet_forwarding_enabled

    if not PROPERTIES_FILE.exists():
        write_config()

    contents = app_tools.read_file(PROPERTIES_FILE)

    if not contents:
        return False

    new_properties, incomplete_data = dict_to_app_properties(literal_eval(contents))
    config = new_properties

    new_properties.allow_package_forwarding = is_packet_forwarding_enabled()

    if incomplete_data:
        write_config()

    return True


def write_config() -> bool:
    global CONFIG_DIRECTORY, PROPERTIES_FILE, config

    if not CONFIG_DIRECTORY.exists():
        CONFIG_DIRECTORY.mkdir()

    data = app_properties_to_dict(config)

    return app_tools.write_file(PROPERTIES_FILE, str(data))


def app_properties_to_dict(data: AppProperties) -> dict:
    global PROPERTIES

    dictionary = dict()

    for key in PROPERTIES:
        dictionary[key.upper()] = getattr(data, key.lower())

    return dictionary


def dict_to_app_properties(data: dict) -> tuple:
    global PROPERTIES

    new_properties = AppProperties()
    incomplete_data = False

    for key in PROPERTIES:
        try:
            setattr(new_properties, key.lower(), data[key.upper()])
        except KeyError:
            incomplete_data = True
            pass

    return new_properties, incomplete_data


def manage_settings():
    global config

    from utils.arpspoof_tools import setup_utility, print_debug_data
    from utils.net_tools import toggle_packet_forwarding
    from utils.arpspoof_thread import toggle_packet_forwarding_in_threads

    while True:
        app_tools.clear_screen(config.IS_UNIX_LIKE_SYSTEM)

        print("  Settings")
        print("1. Run setup")
        print("2. Unlink ARPSpoof executable")

        if config.arp_scan_path:
            print("3. Unlink arp-scan executable")
        else:
            print("3. Provide an arp-scan executable")

        if config.allow_package_forwarding:
            print("4. Disable packet forwarding")
        else:
            print("4. Enable packet forwarding")

        if config.run_setup_in_startup:
            print("5. Disable \"run setup\" in startup")
        else:
            print("5. Enable \"run setup\" in startup")

        if config.scan_every_arpspoof:
            print("6. Scan network manually")
        else:
            print("6. Scan network each time a device is ARPSpoof-ed")

        print("E. Go back")
        print("Select an option")

        selection = app_tools.select_option(["1", "2", "3", "4", "5", "6", "7", "E"])
        app_tools.clear_screen(config.IS_UNIX_LIKE_SYSTEM)

        if selection == "1":
            setup_utility(True)
        elif selection == "2":
            if not config.arpspoof_path:
                print("A copy of ARPSpoof wasn't provided, aborting...")
                input("  Press enter to continue ")
                continue

            print("This program will be terminated")
            print("  Do you want to proceed?")
            print("1. Yes")
            print("2. No")
            if app_tools.select_option(["1", "2"], [True, False]):
                config.reset_arpspoof()
                write_config()
                exit()
        elif selection == "3":
            print("Not implemented yet.")
            input("  Press enter to continue ")
        elif selection == "4":
            if not config.IS_UNIX_LIKE_SYSTEM:
                print("Sorry, Windows isn't supported")
                print("  Please refer to "
                      "https://serverfault.com/questions/929081/how-can-i-enable-packet-forwarding-on-windows")
                input("  Press enter to continue ")
                continue

            config.allow_package_forwarding = not config.allow_package_forwarding
            toggle_packet_forwarding(config.allow_package_forwarding)
            toggle_packet_forwarding_in_threads(config.allow_package_forwarding)
            input("  Press enter to continue ")
        elif selection == "5":
            config.run_setup_in_startup = not config.run_setup_in_startup
        elif selection == "6":
            config.scan_every_arpspoof = not config.scan_every_arpspoof
        elif selection == "7":
            print_debug_data()
        else:
            break

        if selection != "7":
            write_config()


CONFIG_DIRECTORY = Path().cwd().joinpath("config")
PROPERTIES_FILE = CONFIG_DIRECTORY.joinpath("data")
config = AppProperties()

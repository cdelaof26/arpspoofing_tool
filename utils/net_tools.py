# Networking tools
import utils.app_properties as app
import utils.app_tools as app_tools
import re


def list_interfaces() -> list:
    if not app.config.IS_UNIX_LIKE_SYSTEM:
        return list()

    output = app_tools.run_command(app.config.ip_a_command, False)

    # Looks for any string like "en0: " and/or "bridge0: "
    interfaces = re.findall(r'[a-zA-Z]{2,6}\d: ', output)

    # Looks for any string like "enp0s1: "
    interfaces += re.findall(r"[a-zA-Z]{2,6}\d[a-zA-Z]\d: ", output)

    i = 0
    while i < len(interfaces):
        interfaces[i] = interfaces[i].replace(": ", "")
        i += 1

    return interfaces


def select_interface() -> str:
    print(f"[ {app.config.ip_a_command.upper()} ] Detecting network interfaces...")
    interfaces = list_interfaces()
    printable_interfaces, options = app_tools.enumerate_list(interfaces)
    print(printable_interfaces)
    print("Select the interface to use")

    return app_tools.select_option(options, interfaces)


def list_devices_with_arp(interface="") -> tuple:
    app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

    print("[ ARP ] Scanning network...")

    arp_command = app.config.arp_command
    if not interface and app.config.IS_UNIX_LIKE_SYSTEM:
        raise ValueError("Interface parameter is needed for Unix like systems")
    elif app.config.IS_UNIX_LIKE_SYSTEM:
        arp_command = arp_command % interface

    output = app_tools.run_command(arp_command, False)

    ip_addresses = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", output)
    mac_addresses = re.findall(r"\w{1,2}:\w{1,2}:\w{1,2}:\w{1,2}:\w{1,2}:\w{1,2}", output)
    mac_addresses += re.findall(r"\w{1,2}-\w{1,2}-\w{1,2}-\w{1,2}-\w{1,2}-\w{1,2}", output)
    mdns_mac = ""

    complete_info = len(ip_addresses) == len(mac_addresses)

    if complete_info:
        if "224.0.0.251" in ip_addresses:
            mdns_mac = mac_addresses[ip_addresses.index("224.0.0.251")]

    return ip_addresses, mac_addresses, mdns_mac, complete_info


def is_packet_forwarding_enabled() -> bool:
    if not app.config.IS_UNIX_LIKE_SYSTEM:
        return False

    if app.config.SYSTEM_NAME == "darwin":
        output = app_tools.run_command("sysctl -w net.inet.ip.forwarding", False)
    else:
        output = app_tools.run_command("sysctl net.ipv4.ip_forward", False)

    return "1" in output


def toggle_packet_forwarding(enable: bool):
    if not app.config.IS_UNIX_LIKE_SYSTEM:
        return

    mode = 0
    if enable:
        mode = 1

    if app.config.SYSTEM_NAME == "darwin":
        app_tools.run_command(f"sysctl -w net.inet.ip.forwarding={mode}", False)
    else:
        app_tools.run_command(f"sysctl net.ipv4.ip_forward={mode}", False)

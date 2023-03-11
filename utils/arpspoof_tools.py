# Tools for arpspoofing

import utils.app_properties as app
import utils.app_tools as app_tools
import utils.net_tools as net_tools
import utils.arpspoof_thread as thread_manager


ip_addresses = list()
mac_addresses = list()
complete_data = False


def is_command_available(command: str, cwd: str) -> int:
    try:
        output = app_tools.run_command(command, True, cwd)
        if "not found" in output or "not recognized" in output:
            return 1

        if "Permission denied" in output:
            return 2

        return 0
    except (FileNotFoundError, NotADirectoryError):
        return 1


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
    command_availability = is_command_available(command, cwd)

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

        command_availability = is_command_available(command, cwd)


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

    ip_addresses, mac_addresses, mdns_ip, complete_data = net_tools.list_devices_with_arp(app.config.interface)
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


def arpspoof_device():
    global ip_addresses, mac_addresses, complete_data

    if app.config.scan_every_arpspoof:
        setup_utility(False)

    if complete_data:
        devices = app_tools.merge_lists(ip_addresses, mac_addresses)
        devices += ["Cancel"]
        printable_ips, options = app_tools.enumerate_list(devices)
    else:
        printable_ips, options = app_tools.enumerate_list(ip_addresses + ["Cancel"])

    print("  Devices discovered")
    print(printable_ips)
    print("Select your target IP")
    target_ip = app_tools.select_option(options, ip_addresses + ["E"])

    if target_ip == "E":
        return

    if target_ip == app.config.router_ip:
        print("You can't ARPSpoof the router!")
        input("  Press enter to continue ")
        return

    if thread_manager.is_thread_targeting(target_ip):
        print(f"A thread is already arpspoofing target {target_ip}")
        input("  Press enter to continue ")
        return

    thread = thread_manager.ArpspoofThread(
        app.config.interface, app.config.router_ip,
        target_ip, app.config.allow_package_forwarding
    )

    thread_manager.created_threads.append(thread)
    input("  Press enter to continue ")

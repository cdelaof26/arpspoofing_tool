# Tools for arpspoofing

import subprocess
import utils.app_properties as app_properties
import utils.app_tools as app_tools


def is_command_available(command: str, cwd: str) -> int:
    try:
        if not cwd:
            process = subprocess.run(command, capture_output=True)
        else:
            process = subprocess.run(command, cwd=cwd, capture_output=True)

        output = process.stderr.decode("utf-8")
        if "not found" in output or "not recognized" in output:
            return 1

        if "Permission denied" in output:
            return 2

        return 0
    except (FileNotFoundError, NotADirectoryError) as e:
        return 1


def select_executable(executable: app_properties.ARPCommand):
    file = app_tools.select_file()
    command = file.name
    if app_properties.properties.SYSTEM_NAME != "nt":
        command = "./" + command

    if executable == app_properties.ARPCommand.ARPSPOOF:
        app_properties.properties.arpspoof_command = command
        app_properties.properties.arpspoof_path = str(file.parent)
    elif executable == app_properties.ARPCommand.ARP_SCAN:
        app_properties.properties.arp_scan_command = command
        app_properties.properties.arp_scan_path = str(file.parent)
    else:
        raise ValueError(f"{executable} is not interchangeable")

    app_properties.write_config()


def get_arp_command(executable: app_properties.ARPCommand) -> tuple:
    cwd = ""
    if executable == app_properties.ARPCommand.IP_A:
        command = app_properties.properties.ip_a_command
    elif executable == app_properties.ARPCommand.ARP:
        command = "arp"
    elif executable == app_properties.ARPCommand.ARPSPOOF:
        command = app_properties.properties.arpspoof_command
        cwd = app_properties.properties.arpspoof_path
    else:
        command = app_properties.properties.arp_scan_command
        cwd = app_properties.properties.arp_scan_path

    return command, cwd


def look_up_for_arp_command(executable: app_properties.ARPCommand, required: bool):
    command, cwd = get_arp_command(executable)
    command_availability = is_command_available(command, cwd)

    while command_availability != 0:
        if command_availability == 1 and required:
            print(f"{command.replace('./', '')} command not found!")
            print("Do you want to provide a copy?")
            print("1. Yes")
            print("2. No, exit")
            if app_tools.select_option(["1", "2"], [True, False]):
                select_executable(executable)
                command, cwd = get_arp_command(executable)
            else:
                exit(0)

        if command_availability == 2:
            print(f"{command.replace('./', '')} requires elevated privileges!")
            if app_properties.properties.SYSTEM_NAME != "nt":
                print("    Try: sudo or doas")
            exit(1)

        command_availability = is_command_available(command, cwd)

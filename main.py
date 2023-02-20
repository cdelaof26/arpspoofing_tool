import utils.arpspoof_tools as arpspoof_tools
import utils.app_properties as app_properties
import utils.app_tools as app_tools

print("\n    Welcome to arpspoofing tool")

if not app_properties.read_config():
    print("Cannot read config, creating new file...", end="")
    app_properties.write_config()
    if not app_properties.read_config():
        print(" Error!")
        exit(1)
    print(" Done!")

arpspoof_tools.look_up_for_arp_command(app_properties.ARPCommand.IP_A, True)
arpspoof_tools.look_up_for_arp_command(app_properties.ARPCommand.ARP, True)
arpspoof_tools.look_up_for_arp_command(app_properties.ARPCommand.ARPSPOOF, True)
arpspoof_tools.look_up_for_arp_command(app_properties.ARPCommand.ARP_SCAN, False)

while True:
    print("  Main menu")
    print("1. ARPSpoof single device")
    print("2. ARPSpoof multiple devices")
    print("3. Try to ARPSpoof local multicast IP")
    print("S. Settings")
    print("E. Exit")
    print("Select an option")

    selection = app_tools.select_option(["1", "2", "3", "4", "S", "E"])

    # print("1. Provide/unlink ARPSpoof executable copy")
    # print("2. Enable/disable package forwarding")
    # print("3. Use arp-scan/arp")

    if selection == "E":
        break

print("Bye")

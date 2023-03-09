import utils.arpspoof_tools as arpspoof_tools
import utils.app_properties as app
import utils.app_tools as app_tools


if not app.read_config():
    print("Cannot read config, creating new file...", end="")
    app.write_config()
    if not app.read_config():
        print(" Error!")
        exit(1)
    print(" Done!")

arpspoof_tools.look_up_for_arp_command(app.ARPCommand.IP_A, True, False)
arpspoof_tools.look_up_for_arp_command(app.ARPCommand.ARP, True, False)
arpspoof_tools.look_up_for_arp_command(app.ARPCommand.ARPSPOOF, True, True)
arpspoof_tools.look_up_for_arp_command(app.ARPCommand.ARP_SCAN, False, True)

if app.config.run_setup_in_startup:
    arpspoof_tools.setup_utility()

while True:
    app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)
    print("    Welcome to arpspoofing tool")
    print("  Main menu")

    options = ["1", "E"]
    if not app.config.setup_completed:
        print("1. Run setup")
    else:
        print("1. ARPSpoof single device")
        print("2. ARPSpoof multiple devices")
        print("3. ARPSpoof mDNS IP")
        print("4. Re-scan network")
        print("S. Settings")
        options += ["2", "3", "4", "S"]

    print("E. Exit")
    print("Select an option")

    try:
        selection = app_tools.select_option(options)
    except KeyboardInterrupt:
        print("\n    Process cancelled!")
        input("Press enter to continue ")
        continue

    if selection == "1":
        if app.config.setup_completed:
            pass
        else:
            arpspoof_tools.setup_utility()
            arpspoof_tools.print_debug_data()

    if selection == "S":
        app.manage_settings()

    if selection == "E":
        break

print("Bye")

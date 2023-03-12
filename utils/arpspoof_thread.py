# Class for threads

import utils.app_tools as app_tools
import utils.app_properties as app
# from multiprocessing import Process
from enum import Enum


class ARPSpoofProcesses(Enum):
    TARGET_ROUTER = 0
    ROUTER_TARGET = 1
    BOTH = 2


class ARPSpoofThread:
    def __init__(self, interface: str, router_ip: str, target_ip: str, forward_back: bool):
        self.interface = interface
        self.router_ip = router_ip
        self.target_ip = target_ip
        self.forward_back = forward_back
        self.process_target_router = None
        self.process_router_target = None
        self.amount_of_threads = 0
        self.start_one()

    def start_all(self, process_to_start=ARPSpoofProcesses.BOTH):
        operate_tr = do_operate_target_router(process_to_start)
        operate_rt = do_operate_router_target(process_to_start)

        if self.process_target_router is None and operate_tr:
            self.process_target_router = list()

        if self.process_router_target is None and operate_rt:
            self.process_router_target = list()

        if isinstance(self.process_target_router, list) and operate_tr:
            for i in range(self.amount_of_threads):
                self.process_target_router.append(arpspoof(self.interface, self.target_ip, self.router_ip))
                print(f"[INFO] Started thread-{len(self.process_target_router)} for {self.target_ip}")

        if isinstance(self.process_router_target, list) and self.forward_back and operate_rt:
            for i in range(self.amount_of_threads):
                self.process_router_target.append(arpspoof(self.interface, self.router_ip, self.target_ip))
                print(f"[INFO] Started thread-{len(self.process_router_target)} for {self.target_ip} (RT)")

    def start_one(self, process_to_start=ARPSpoofProcesses.BOTH):
        operate_tr = do_operate_target_router(process_to_start)
        operate_rt = do_operate_router_target(process_to_start)

        if self.process_target_router is None and operate_tr:
            self.process_target_router = list()

        if self.process_router_target is None and operate_rt:
            self.process_router_target = list()

        if isinstance(self.process_target_router, list) and operate_tr:
            self.amount_of_threads += 1
            self.process_target_router.append(arpspoof(self.interface, self.target_ip, self.router_ip))
            print(f"[INFO] Started thread-{len(self.process_target_router)} for {self.target_ip}")

        if isinstance(self.process_router_target, list) and self.forward_back and operate_rt:
            self.process_router_target.append(arpspoof(self.interface, self.router_ip, self.target_ip))
            print(f"[INFO] Started thread-{len(self.process_router_target)} for {self.target_ip} (RT)")

    def stop_all(self, process_to_stop=ARPSpoofProcesses.BOTH):
        if self.process_target_router is not None and do_operate_target_router(process_to_stop):
            while self.process_target_router:
                self.process_target_router[0].terminate()
                print(f"[INFO] Stopped thread-{len(self.process_target_router)} for {self.target_ip}")
                self.process_target_router.pop(0)

            self.process_target_router = None

        if self.process_router_target is not None and do_operate_router_target(process_to_stop):
            while self.process_router_target:
                self.process_router_target[0].terminate()
                print(f"[INFO] Stopped thread-{len(self.process_router_target)} for {self.target_ip} (RT)")
                self.process_router_target.pop(0)

            self.process_router_target = None

    def stop_one(self, process_to_stop=ARPSpoofProcesses.BOTH):
        if self.process_target_router is not None and do_operate_target_router(process_to_stop):
            self.amount_of_threads -= 1
            if self.process_target_router:
                self.process_target_router[0].terminate()
                print(f"[INFO] Stopped thread-{len(self.process_target_router)} for {self.target_ip}")
                self.process_target_router.pop(0)

            if not self.process_target_router:
                self.process_target_router = None

        if self.process_router_target is not None and do_operate_router_target(process_to_stop):
            if self.process_router_target:
                self.process_router_target[0].terminate()
                print(f"[INFO] Stopped thread-{len(self.process_router_target)} for {self.target_ip} (RT)")
                self.process_router_target.pop(0)

            if not self.process_router_target:
                self.process_router_target = None

    def toggle_packet_forwarding(self, forward_back):
        self.forward_back = forward_back

        if forward_back:
            self.start_all(ARPSpoofProcesses.ROUTER_TARGET)
        else:
            self.stop_all(ARPSpoofProcesses.ROUTER_TARGET)

    def to_string(self) -> str:
        return f"Target\t[{self.target_ip}]\n" \
               f"\t  Packet forwarding\t{self.forward_back}\n" \
               f"\t  Is running       \t{self.process_target_router is not None}\n" \
               f"\t  Is running (RT)  \t{self.process_router_target is not None}"


created_threads = list()


def arpspoof(interface: str, ip1: str, ip2: str):
    cwd = ""
    cmd = app.config.arpspoof_command
    if app.config.arpspoof_path:
        cwd = app.config.arpspoof_path

    if interface:
        cmd += f" -i {interface}"

    cmd += f" -t {ip1} {ip2}"

    return app_tools.get_command_process(cmd, cwd)


def toggle_packet_forwarding_in_threads(new_value: bool):
    global created_threads

    for thread in created_threads:
        thread.toggle_packet_forwarding(new_value)


def is_ip_targeted(ip: str) -> bool:
    global created_threads

    for thread in created_threads:
        if thread.target_ip == ip:
            return True

    return False


def filter_ips(ip_addresses: list, mac_addresses: list, complete_data: bool) -> tuple:
    global created_threads

    selectable_ips = ip_addresses.copy()
    selectable_macs = mac_addresses.copy()

    try:
        thread_id = selectable_ips.index(app.config.router_ip)

        selectable_ips.pop(thread_id)
        if complete_data:
            selectable_macs.pop(thread_id)
    except IndexError:
        pass

    for thread in created_threads:
        try:
            thread_id = selectable_ips.index(thread.target_ip)
        except ValueError:
            continue

        selectable_ips.pop(thread_id)

        if complete_data:
            selectable_macs.pop(thread_id)

    return selectable_ips, selectable_macs


def toggle_threads_status(start: bool):
    global created_threads

    for thread in created_threads:
        if start:
            thread.start_all()
        else:
            thread.stop_all()


def do_operate_target_router(process_to_operate: ARPSpoofProcesses):
    return process_to_operate == ARPSpoofProcesses.BOTH or process_to_operate == ARPSpoofProcesses.TARGET_ROUTER


def do_operate_router_target(process_to_operate: ARPSpoofProcesses):
    return process_to_operate == ARPSpoofProcesses.BOTH or process_to_operate == ARPSpoofProcesses.ROUTER_TARGET


def modify_thread(thread: ARPSpoofThread):
    global created_threads

    while True:
        app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

        threads_amount = thread.amount_of_threads
        if app.config.allow_package_forwarding:
            threads_amount = threads_amount * 2

        options = ["1", "2", "E"]
        if thread.process_target_router is not None:
            print(f"  Target\t[{thread.target_ip}] [Threads: {threads_amount}]")
            print("1. Suspend all")
            print("2. Delete all")
            print("3. Start one")
            print("4. Stop one")
            print("5. Start N")
            print("6. Stop N")
            options += ["3", "4", "5", "6"]
        else:
            print(f"  Target\t[{thread.target_ip}] [Threads: 0]")
            print(f"1. Start all [{threads_amount} threads]")
            print("2. Delete all")

        print("E. Go back")
        print("Select an option")
        selection = app_tools.select_option(options)

        if selection == "1":
            if thread.process_target_router is not None:
                thread.stop_all()
            else:
                thread.start_all()
        elif selection == "2":
            thread.stop_all()
            created_threads.remove(thread)
            break
        elif selection == "3":
            thread.start_one()
        elif selection == "4":
            thread.stop_one()
        elif selection == "5":
            print("Enter the amount of threads to create [máx 50]")
            amount = app_tools.get_int_in(0, 50)
            if amount + threads_amount > 50:
                input("Python might crash!. Press enter to continue ")

            try:
                for _ in range(amount):
                    thread.start_one()
            except OSError:
                for _ in range(5):
                    thread.stop_one()

                print("Impossible open more processes")
                input("  Press enter to continue ")
        elif selection == "6":
            print(f"Enter the amount of threads to stop [máx {threads_amount}]")
            amount = app_tools.get_int_in(0, threads_amount)
            for _ in range(amount):
                thread.stop_one()
        else:
            break


def manage_threads():
    global created_threads

    while True:
        app_tools.clear_screen(app.config.IS_UNIX_LIKE_SYSTEM)

        if not created_threads:
            print("There are not threads")
            input("  Press enter to continue ")
            break

        threads = list()
        for thread in created_threads:
            threads.append(thread.to_string())

        enumerated_threads, options = app_tools.enumerate_list(threads)

        print("  Created threads")
        print(enumerated_threads)
        print("S. Start all")
        print("Q. Suspend all")
        print("D. Delete all")
        print("E. Exit")
        print("Select a thread to manage")
        selection = app_tools.select_option(options + ["S", "Q", "D", "E"], created_threads + ["S", "Q", "D", "E"])

        if isinstance(selection, str):
            if selection == "S":
                toggle_threads_status(True)
            elif selection == "Q":
                toggle_threads_status(False)
            elif selection == "D":
                toggle_threads_status(False)
                created_threads = list()
                break
            else:
                break
        elif isinstance(selection, ARPSpoofThread):  # Just to make PyCharm stop complaining
            modify_thread(selection)

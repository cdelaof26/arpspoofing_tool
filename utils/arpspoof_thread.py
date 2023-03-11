# Class for threads

import utils.app_tools as app_tools
import utils.app_properties as app
import threading
from enum import Enum


created_threads = list()


def arpspoof(interface: str, ip1: str, ip2: str):
    cwd = ""
    cmd = app.config.arpspoof_command
    if app.config.arpspoof_path:
        cwd = app.config.arpspoof_command

    if interface:
        cmd += f" -i {interface}"

    cmd += f" -t {ip1} {ip2}"

    app_tools.run_command(cmd, False, cwd)


class ArpspoofProcesses(Enum):
    TARGET_ROUTER = 0
    ROUTER_TARGET = 1
    BOTH = 2


def toggle_packet_forwarding_in_threads(new_value: bool):
    global created_threads

    for thread in created_threads:
        thread.toggle_packet_forwarding(new_value)


def is_thread_targeting(ip: str) -> bool:
    global created_threads

    for thread in created_threads:
        if thread.target_ip == ip:
            return True

    return False


# def filter_unselectable_ips():


def stop_threads():
    global created_threads

    for thread in created_threads:
        thread.stop(ArpspoofProcesses.BOTH)
        print(f"[INFO] Stopped thread for {thread.target_ip}")


def do_operate_target_router(process_to_operate: ArpspoofProcesses):
    return process_to_operate == ArpspoofProcesses.BOTH or process_to_operate == ArpspoofProcesses.TARGET_ROUTER


def do_operate_router_target(process_to_operate: ArpspoofProcesses):
    return process_to_operate == ArpspoofProcesses.BOTH or process_to_operate == ArpspoofProcesses.ROUTER_TARGET


class ArpspoofThread:
    def __init__(self, interface: str, router_ip: str, target_ip: str, forward_back: bool):
        self.interface = interface
        self.router_ip = router_ip
        self.target_ip = target_ip
        self.forward_back = forward_back
        self.process_target_router = None
        self.process_router_target = None
        self.start(ArpspoofProcesses.BOTH)

    def start(self, process_to_start: ArpspoofProcesses):
        if self.process_target_router is None and do_operate_target_router(process_to_start):
            print(f"[INFO] Started thread for {self.target_ip}")
            self.process_target_router = threading.Timer(
                0, arpspoof,
                args=(self.interface, self.target_ip, self.router_ip,)
            )

        if self.process_router_target is None and do_operate_router_target(process_to_start) and self.forward_back:
            self.process_router_target = threading.Timer(
                0, arpspoof,
                args=(self.interface, self.router_ip, self.target_ip,)
            )

    def stop(self, process_to_stop: ArpspoofProcesses):
        if self.process_target_router is not None and do_operate_target_router(process_to_stop):
            self.process_target_router.cancel()
            self.process_target_router = None

        if self.process_router_target is not None and do_operate_router_target(process_to_stop):
            self.process_router_target.cancel()
            self.process_router_target = None

    def toggle_packet_forwarding(self, forward_back):
        if forward_back:
            self.start(ArpspoofProcesses.ROUTER_TARGET)
        else:
            self.stop(ArpspoofProcesses.ROUTER_TARGET)

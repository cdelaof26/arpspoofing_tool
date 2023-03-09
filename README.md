# arpspoofing_tool

### What is this?

A basic python 3 project to ARP-Poisoning local users

### Disclaimer

This project is intended for _educational proposes_

**I'm not responsible for any potencial malicious use of this software**

Before running it, please read [LICENSE](LICENSE)

### Dependencies 

1. Python 3.6 or newer
2. For Linux:
   - `iproute2` for `ip` command
   - `net-tools` for `arp` command
   - `dsniff` for `arpspoof` command
   - `arp-scan`
3. For macOS and Windows:
   - You'll need to provide a copy of `arpspoof` and `arp-scan`
     (both SOes include similar tools to `ip` and `arp` by default, 
     so no need to provide a copy of each)

- **Note**: `arp-scan` is optional

### Running project

Clone this repo

<pre>
$ git clone https://github.com/cdelaof26/arpspoofing_tool.git
</pre>

Move into project directory

<pre>
$ cd arpspoofing_tool
</pre>

Run

<pre>
# If you're on macOS or Linux
$ python3 main.py

# If you're on Windows
$ python main.py
</pre>

**Note:**
When it's running for first time, you'll be asked to 
provide a copy of `arpspoof` if it isn't
installed in your system



### Changelog

### v0.0.2

- Improved menu
- Improved app settings
  - Added `interface`, `router_mac`, `mdns_mac`,
    `allow_package_forwarding` and more settings
- `arpspoofing_tool` can scan network for devices
- Added settings section (WIP)


### v0.0.1

- Initial project
  - Verification of dependencies works =p

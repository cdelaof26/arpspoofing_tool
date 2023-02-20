# arpspoofing_tool

### What is this?

A basic python 3 project to ARP-Poisoning local users

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
provide a copy of `arpspoof` and `arp-scan` if they aren't
installed in your system



### Changelog

### v0.0.1

- Initial project
  - Verification of dependencies works =p

# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/robot.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/>Wrapper Aircrack
A simple Mycroft wrapper for a small subset of Aircrack-ng.

## About 
A simple Mycroft wrapper for a small subset of Aircrack-ng. Basically, it can list networks and interfaces, bring interfaces up in monitor mode, deauth clients, and crack WPA2 passwords.

## Examples 
* "List interfaces."
* "Select interface number one."
* "List wireless networks."
* "Select network number three."
* "Start Monitor."
* "Disconnect Clients."
* "Crack Password."
* "Stop Monitor."

## Credits 
Jon Stratton (@JonStratton)

## Disclaimer
This tool is intended to test your own wireless networks, in a fun way, for bad wpa2 passwords.

Accessing wireless networks without permission is, and should be, a crime. As is cracking passwords. The user of this software is responsible for it’s use. Please don’t be a bad person.

## Notes
### sudo access
This skill must be able to sudo some programs without password prompting. To set up, use the `visudo` command and grant your user sudo access with something like the following:
```
Cmnd_Alias AIRCRACK = /usr/sbin/airmon-ng, /usr/sbin/airodump-ng, /usr/sbin/aireplay-ng, /sbin/iwlist
my_mycroft_user ALL = NOPASSWD: AIRCRACK
```
**Note:** Replace my_mycroft_user with the user you are running Mycroft as.

## Supported Devices 
platform_picroft platform_plasmoid 

## Category
Information

## Tags
#aircrack
#aircrack-ng
#wifi

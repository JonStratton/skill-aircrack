## Skill Wrapper Aircrack
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

## Notes
### sudo access
This skill must be able to sudo some programs without password prompting. To set up, please visudo and grant the user access like the following:
```
Cmnd_Alias AIRCRACK = /usr/sbin/airmon-ng, /usr/sbin/airodump-ng, /usr/sbin/aireplay-ng, /sbin/iwlist
my_mycroft_user ALL = NOPASSWD: AIRCRACK
```

### Password list files
In order to crack passwords, a password file must be on your system. Currently, this pulls in a password file from [Daniel Miessler's SecLists](https://github.com/danielmiessler/SecLists). If you want to use some other password file, update the "wordlist" to point at your password list file.

## Credits 
Jon Stratton

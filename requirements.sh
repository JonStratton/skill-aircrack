# The requirements.sh is an advanced mechanism an should rarely be needed.
# Be aware that it won't run with root permissions and 'sudo' won't work
# in most cases.

# Base commands
dist="$(lsb_release -is)"
if [[ "$dist" =~ "SUSE" ]]; then 
   sudo zypper install locate
   sudo zypper install aircrack-ng
elif [[ "$dist" =~ "Fedora" ]]; then 
   sudo yum install locate
   sudo yum install aircrack-ng
else 
   sudo apt-get install locate
   sudo apt-get install aircrack-ng
fi

# Probably need a password file
if [ -z "$(locate rockyou.txt)" ]; then
   echo "rockyou.txt not found. Please find a copy and download it."
fi

# Can we sudo our commands?
sudo_commands=( aireplay-ng airodump-ng airmon-ng iwlist )
for command in "${sudo_commands[@]}"
do
   if ! [[ "$(sudo $command --help)" =~ "sage" ]]; then
      echo "Passwordless \"sudo $command\" failed. Please update your sudo access."
   fi
done

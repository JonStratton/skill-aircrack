# The requirements.sh is an advanced mechanism an should rarely be needed.
# Be aware that it won't run with root permissions and 'sudo' won't work
# in most cases.

# Can we sudo our commands?
sudo_commands=( aireplay-ng airodump-ng airmon-ng iwlist )
for command in "${sudo_commands[@]}"
do
   if ! [[ "$(sudo -l | grep $command | grep NOPASS)" ]]; then
      echo "Passwordless \"sudo $command\" failed. Please update your sudo access."
   fi
done

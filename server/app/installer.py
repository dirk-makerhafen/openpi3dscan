import json
import os
import glob
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class Installer():

    def run(self):
        # COPY TO TARGET
        if SCRIPT_DIR != "/opt/openpi3dscan/server/app":
            self.shell("sudo mkdir -p /shots")
            self.shell("sudo mkdir -p /opt/openpi3dscan/server")
            self.shell("sudo mkdir -p /opt/openpi3dscan/client")
            self.shell("sudo mkdir -p /opt/openpi3dscan/realityCapture")
            self.shell("sudo mkdir -p /opt/openpi3dscan/firmware")
            self.shell("sudo mkdir -p /opt/openpi3dscan/meta")  # meta data backup dir
            self.shell('sudo rsync --delete -rav %s/../*                    /opt/openpi3dscan/server/ ' % SCRIPT_DIR)
            self.shell('sudo rsync --delete -rav %s/../../client/*          /opt/openpi3dscan/client/ ' % SCRIPT_DIR)
            self.shell('sudo rsync --delete -rav %s/../../realityCapture/*  /opt/openpi3dscan/realityCapture/ ' % SCRIPT_DIR)
    
            for imgzippath in glob.glob("%s/../../firmware/*.img.zip" % SCRIPT_DIR):
                imgfile = imgzippath.split("/")[-1].replace(".zip", "")
                if not os.path.exists("/opt/openpi3dscan/firmware/%s" % imgfile):
                    self.shell("cp '%s' /opt/openpi3dscan/firmware/ " % imgzippath)
                    self.shell("cd /opt/openpi3dscan/firmware/ ; unzip '%s.zip' ; rm '%s.zip'" % (imgfile, imgfile))
    
        # LISTEN ON ALL IPS, PORT 80
        self.shell("cat /opt/openpi3dscan/server/run.py | sed s/'127.0.0.1'/'0.0.0.0'/g | sed s/'8888'/'80'/g > 1 ; sudo mv 1 /opt/openpi3dscan/server/run.py ")
    
        # REQUIREMENTS
        self.shell("cd /opt/openpi3dscan/server/ ; sudo pip3 install -r requirements.txt")
        self.shell('sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update')
        self.shell('sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install avahi-daemon ntp dnsmasq iptables ntpdate ntp')
    
        # Add user for ssh login
        self.shell('sudo useradd openpi3dscan')
        self.shell('echo openpi3dscan:openpi3dscan | sudo chpasswd')
        self.shell('echo "openpi3dscan ALL=(ALL) NOPASSWD: ALL" > 1 ; sudo mv 1 "/etc/sudoers.d/010_openpi3dscan-nopasswd" ; sudo chown root:root /etc/sudoers.d/010_openpi3dscan-nopasswd ')
    
        hostname = "openpi3dscan"
        try:
            data = open("/opt/openpi3dscan/.openpi3dscan.json", "r").read()
            hostname = json.loads(data)["hostnameSettings"]["hostname"]
            if len(hostname) < 3:
                hostname = "openpi3dscan"
        except:
            hostname = "openpi3dscan"
    
        # HOSTNAME
        open("/tmp/1", "w").write("%s\n" % hostname)
        self.shell("sudo mv /tmp/1 /etc/hostname")
        self.shell("cat /etc/hosts | grep -v '192.168.99.' | grep -v localhost | grep -v raspberrypi | grep -v openpi3dscan > 1")
        self.shell("echo '192.168.99.254   openpi3dscan' >> 1")
        self.shell("echo '192.168.99.254   %s # openpi3dscan' >> 1" % hostname)
        self.shell("echo '127.0.0.1      localhost' >> 1")
        self.shell("sudo mv 1 /etc/hosts")
    
        # NETWORK
        s  = 'interface eth0 \n'
        s += 'static ip_address=192.168.99.254/24 \n'
        s += 'static domain_name_servers=8.8.8.8 \n'
        s += 'interface wlan0 \n'
        s += 'static domain_name_servers=8.8.8.8 \n'
        open("/tmp/1", "a").write(s)
        self.shell("sudo mv /tmp/1 /etc/dhcpcd.conf")
    
        # DHCPD
        s  = 'interface=eth0  \n'
        s += 'listen-address=192.168.99.254 \n'
        s += 'bind-interfaces \n'
        s += 'server=8.8.8.8  \n'
        s += 'domain-needed   \n'
        s += 'bogus-priv      \n'
        s += 'dhcp-range=192.168.99.2,192.168.2.64,96h \n'
        open("/tmp/1", "w").write(s)
        self.shell("sudo mv /tmp/1 /etc/dnsmasq.conf")
    
        # NTP
        self.shell('sudo systemctl stop systemd-timesyncd ; ')
        self.shell('sudo systemctl disable systemd-timesyncd ; ')
        self.shell("sudo service ntp stop")
        self.shell("sudo ntpdate de.pool.ntp.org")
        self.shell("cat /etc/ntp.conf | grep -v 192.168.99.0 |grep -v de.pool.ntp.org > 1")
        self.shell("echo 'restrict 192.168.99.0 mask 255.255.255.0 nomodify notrap' >> 1")
        self.shell("echo 'server de.pool.ntp.org prefer' >> 1")
        self.shell("echo 'server 127.127.1.0' >> 1")
        self.shell("echo 'fudge  127.127.1.0 stratum 10' >> 1")
        self.shell("sudo mv 1 /etc/ntp.conf")
        self.shell("sudo systemctl enable ntp")
        self.shell("sudo service ntp restart")
    
        # ROUTING
        self.shell("cat /etc/sysctl.conf | sed s/'#net.ipv4.ip_forward=1'/'net.ipv4.ip_forward=1'/g > 1")
        self.shell("sudo mv 1 /etc/sysctl.conf")
    
        # Nameserver
        self.shell("echo 'nameserver 8.8.8.8' > 1")
        self.shell("sudo mv 1 /etc/resolv.conf")
    
        # AUTOSTART
        self.shell("cat /etc/rc.local | grep -v 'sudo iptables -' | grep -v openpi3dscan |grep -v 'exit 0' > 1")
        self.shell("echo 'sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE' >> 1")
        self.shell("echo 'sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT' >> 1")
        self.shell("echo 'sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT' >> 1")
        self.shell("echo 'sudo python3 /opt/openpi3dscan/server/run.py &' >> 1")
        self.shell("echo 'exit 0' >> 1")
        self.shell("sudo chown root:root 1 ; sudo chmod +x 1 ; sudo mv 1 /etc/rc.local ")
    
        # shell("sudo reboot")

    def shell(self, cmd):
        print(cmd)
        os.system(cmd)

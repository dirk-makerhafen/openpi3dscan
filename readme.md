
- Create default raspian image
- Mount boot Partition
- Create empty "ssh" file in boot partition
- Create file wpa_supplicant.conf
  with following contents:
<pre>
country=de
update_config=1
ctrl_interface=/var/run/wpa_supplicant
network={
 scan_ssid=1
 ssid="WLAN_SSID"
 psk="WLAN_PASSWORD"
}
</pre>
 Replace country code "de" with your country:
 gb (United Kingdom),fr (France), de (Germany), us (United States), se (Sweden)
 
 Replace WLAN_SSID and WLAN_PASSWORD with your wlan data.
 
- Boot raspberry, find in wlan, conntect via ssh

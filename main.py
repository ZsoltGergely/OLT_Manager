from olt_telnet_functions import *
import time

tn_connection = connect("89.46.237.100", "smartoltusr", "Wx87NJ3TGm4Rv2", 2333)
#
# delete("gpon-onu_1/13/1:1", tn_connection)
#
# print(get_unconf(tn_connection))
#
# authorize(get_unconf(tn_connection)[0][1],get_unconf(tn_connection)[0][0], "Test", "Test street ye", 1, 1236, tn_connection)
# time.sleep(4)
# print(get_signal_telnet("gpon-onu_1/13/1:1",tn_connection))

print(get_traffic_telnet("gpon-onu_1/13/1:1",tn_connection))



#
# delete("gpon-onu_1/13/1:1", tn_connection)
#
 # time.sleep(4)
#
# print(get_unconf(tn_connection))


# tn_connection.close()


# TRUNCATE `cards`;TRUNCATE  `olts`;TRUNCATE `onu_vports`;TRUNCATE`pon_ports`



# client config

# config = "att_vlans:445,400,5\nmain_vlan:1236\nconn:pppoe:asdfg,gfyeuf\neth1:lan\neth2:vlan:untag;1/tag;445,400\neth3:lan\neth4:lan\nwlan1:ssid:asdasd:asdfghjk"
# tn_connection=[]
# parse_onu_config(config, "gpon-on_1/13/1:1", tn_connection)



# att_vlans:445,400,5
# main_vlan:1236
# conn:ip:192.168.1.2,255.255.255.0,192.168.1.1,1.1.1.1,8.8.8.8
# eth1:lan
# eth2:vlan:untag;1/tag;445,400
# eth3:lan
# eth4:lan
# wlan1:ssid:asdasd:asdfghjk

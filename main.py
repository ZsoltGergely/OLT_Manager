from olt_telnet_functions import *
import time

# tn_connection = connect("89.46.237.100", "smartoltusr", "Wx87NJ3TGm4Rv2", 2333)
#
# delete("gpon-onu_1/13/1:1", tn_connection)
#
# print(get_unconf(tn_connection))
#
# authorize(get_unconf(tn_connection)[0][1],get_unconf(tn_connection)[0][0], "Test", "Test street ye", 1, 1236, tn_connection)
# time.sleep(4)
# print(get_signal_telnet("gpon-onu_1/13/1:1",tn_connection))
# # print(get_traffic_telnet("gpon-onu_1/13/1:1",tn_connection))
#
# delete("gpon-onu_1/13/1:1", tn_connection)
# time.sleep(4)
#
# print(get_unconf(tn_connection))
#
# tn_connection.close()

# TRUNCATE `cards`;TRUNCATE  `olts`;TRUNCATE `onu_vports`;TRUNCATE`pon_ports`

# client config
config = "att_vlans:445,400,5\nmain vlan:1236\nconn:ip;value:192.168.1.2,255.255.255.0,192.168.1.1,1.1.1.1,8.8.8.8\neth1:lan;value:\neth2:vlan;value:untag:1/tag:445,400\neth3:lan;value:\neth4:lan;value:"
parse_onu_config(config)
# att_vlans:445,400,5
# main vlan:1236
# conn:ip;value:192.168.1.2,255.255.255.0,192.168.1.1,1.1.1.1,8.8.8.8
# eth1:lan;value:
# eth2:vlan;value:untag:1/tag:445,400
# eth3:lan;value:
# eth4:lan;value:

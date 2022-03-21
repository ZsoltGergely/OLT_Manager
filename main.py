from olt_telnet_functions import *


tn_connection = connect("89.46.237.100", "smartoltusr", "Wx87NJ3TGm4Rv2", 2333)

print(get_unconf(tn_connection))

authorize(get_unconf(tn_connection)[0][1],get_unconf(tn_connection)[0][0], "Test", "Test street ye", 1, 1236, tn_connection)


tn_connection.close()

# TRUNCATE `cards`;TRUNCATE  `olts`;TRUNCATE `onu_vports`;TRUNCATE`pon_ports`

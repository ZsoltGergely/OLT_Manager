from olt_telnet_functions import *

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="olt_management"
)
mycursor = mydb.cursor()


tn_connection = connect("89.46.237.100", "smartoltusr", "Wx87NJ3TGm4Rv2", 2333)

print(get_unconf(tn_connection))

tn_connection.close()

# TRUNCATE `cards`;TRUNCATE  `olts`;TRUNCATE `onu_vports`;TRUNCATE`pon_ports`

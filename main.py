from olt_telnet_functions import *
import time
# import threa

#
# delete("gpon-onu_1/13/1:1", tn_connection)
#
# print(get_unconf(tn_connection))
#
# authorize(get_unconf(tn_connection)[0][1],get_unconf(tn_connection)[0][0], "Test", "Test street ye", 1, 1236, tn_connection)
# time.sleep(4)
# print(get_signal_telnet(,tn_connection))
# print(get_traffic_telnet("gpon-onu_1/13/1:1",tn_connection))

def options():
    print """
    -----OPTIONS-----
    1. List Unconfigured ONUs
    2. List Clients
    3. Authorize ONU
    4. Edit ONU Config
    5. Get data of ONU
    6. List OLTs
    7. Initialize OLT
    -----------------
    """
    print("Choice: ")
    choice = int(input())
    if input == 1:
        list_unconfig()
    elif input == 2:
        list_clients()
    elif input == 3:
        cli_authorize()
    elif input == 4:
        edit_onu_config()
    elif input == 5:
    elif input == 6:
    elif input == 7:
    elif input == 8:
    elif input == 9:


def list_unconfig():
    mycursor.execute("SELECT id, ip, telnet_user, telnet_pass, telnet_port, name FROM olts")
    olts = mycursor.fetchall()
    for olt in olts:
        tn_connection = connect(olt[1], olt[2], olt[3], olt[4])
        onus = get_unconf(tn_connection)
        print("---------{}.{}---------".format(olt[0], olt[5]))
        for onu in onus:
            print(onu[0] + "    ------     " + onu[1] + )

def list_clients():
    mycursor.execute("SELECT port, name, device_type, olt_id FROM clients")
    clients = mycursor.fetchall()
    for client in clients:
        # TODO add join table with olts and get signal
        print(client[0] + " - " + client[1] + " - " + client[1] + " - " +)

def cli_authorize():
    print("OLT id: ")
    olt_id = input()
    print("ONU Port: ")
    unauth_port = input()
    print("ONU Serial Number: ")
    sn = input()
    print("Client Name: ")
    name = input()
    print("Client Address: ")
    address = input()
    print("Device Type ID: ")
    device_type = input()
    print("Main Vlan id: ")
    vlan = input()
    mycursor.execute("SELECT id, ip, telnet_user, telnet_pass, telnet_port, name FROM olts WHERE id = {}".format(olt_id))
    olt = mycursor.fetchone()
    tn_connection = connect(olt[1], olt[2], olt[3], olt[4])
    try:
        authorize(sn, unauth_port, name, address, device_type, vlan, olt_id, tn_connection)
        print("SUCCESS")
    except:
        print("ONU authorization FAILED")

def edit_onu_config():
    print("Client id: ")
    client_id = input()
    newconfig = ""
    mycursor.execute("SELECT config, port FROM clients WHERE id = {}".format(client_id))
    config = mycursor.fetchone()
    print(config[0])
    print("----------")
    while input() as line:
        newconfig += line + "\n"
    mycursor.execute("UPDATE clients SET config = {} WHERE id = {}".format(newconfig, ewclient_id))
    mydb.commit()
    parse_onu_config(newconfig, config[1])
    # TODO get olt telnet connection


def data_collection():
    mycursor.execute("SELECT id, ip, telnet_user, telnet_pass, telnet_port FROM olts")
    olts = mycursor.fetchall()
    for olt in olts:
        tn_connection = connect(olt[1], olt[2], olt[3], olt[4])
        mycursor.execute("SELECT id, port FROM clients WHERE olt_id = {}".format(olt[0]))
        onus = mycursor.fetchall()
        for onu in onus:
            signal = get_signal_telnet(onu[1], tn_connection)
            traffic = get_traffic_telnet(onu[1], tn_connection)
            sql = "INSERT INTO `data`(onu_id, sig_rx, sig_tx, bdw_in, pps_in, bdw_out, pps_out ) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            #TODO create db, add timestamp
            val = (onu[0], signal[0], signal[1], traffic[0][0], traffic[1], traffic[2][0], traffic[3])
            mycursor.execute(sql, val)
            mydb.commit()
        tn_connection.close()










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

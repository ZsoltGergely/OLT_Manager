import telnetlib
import re
from datetime import datetime
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="hIV9k@bQq!bc(CvA",
  database="olt_management"
)
mycursor = mydb.cursor()

HOST = "89.46.237.100"
user = "smartoltusr"
password = "Wx87NJ3TGm4Rv2"

onu_signal_oid = "1.3.6.1.4.1.3902.1012.3.50.12.1.1.10"

def log(string):

    from datetime import datetime

    print(string)
    now = datetime.now()
    date = now.strftime("%m%d%y")
    datetime = now.strftime("%m/%d/%y -- %H:%M")
    f = open("logs/log"+date+".txt", "a")
    f.write("---------------------"+datetime+"---------------------\n")
    f.write(str(string))
    f.write("\n")
    f.close()

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'k', 2: 'm', 3: 'g', 4: 't'}
    while size > power:
        size /= power
        n += 1
    return [size, power_labels[n]+'bps']

def send_multiple(lines):
    for line in lines:
        tn.write(str.encode(line+"\n"))
        log(tn.read_until(b"#").decode('ascii'))

def clean_traffic(raw):
    bps_ind = raw.find("bps")
    pps_ind = raw.find("pps")
    bps_val = raw[0:bps_ind]
    pps_val = raw[bps_ind+3:pps_ind]
    return [bps_val, pps_val]

def get_traffic_telnet(port):
    global tn
    tn = telnetlib.Telnet(HOST, 2333)

    tn.read_until(b"Username:")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\n")
        tn.read_until(b"#")
    command = "show interface " + port + "\n"
    tn.write(str.encode(command))
    response = tn.read_until(b"#").decode('ascii')
    response = response.replace(" ","")
    try:
        split = response.split("rate:")
        raw_input_curr = split[1]
        raw_output_curr = split[2]
        raw_input_all = split[4]
        raw_output_all = split[5]
        input_curr_bdw = format_bytes(int(clean_traffic(raw_input_curr)[0]))
        input_curr_pps = clean_traffic(raw_input_curr)[1]
        output_curr_bdw = format_bytes(int(clean_traffic(raw_output_curr)[0]))
        output_curr_pps = clean_traffic(raw_output_curr)[1]
        input_all_bdw = format_bytes(int(clean_traffic(raw_input_curr)[0]))
        input_all_pps = clean_traffic(raw_input_curr)[1]
        output_all_bdw = format_bytes(int(clean_traffic(raw_output_curr)[0]))
        output_all_pps = clean_traffic(raw_output_curr)[1]
        return [input_curr_bdw,input_curr_pps,output_curr_bdw,output_curr_pps,input_all_bdw,input_all_pps,output_all_bdw,output_all_pps]
    except IndexError:
        return[["0","0"],"0",["0","0"],"0",["0","0"],"0",["0","0"],"0",]


def get_signal_telnet(port):

    global tn
    tn = telnetlib.Telnet(HOST, 2333)

    tn.read_until(b"Username:")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\n")
        tn.read_until(b"#")
    command = "show pon power att " + port + "\n"
    tn.write(str.encode(command))
    response = tn.read_until(b"#").decode('ascii')
    try:
        split = response.split("Rx")
        value2 = split[1][2:9]
        value1 = split[2][1:8]
        tn.close()
        return [value1,value2]
    except IndexError:
        return["0.000","0.000"]

def get_olt_cards(tn_connection):
    command = "show card \n"
    tn_connection.write(str.encode(command))
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)
    response = response.splitlines()
    cards = []
    for line in response[2:-1]:
        values = line.split()
        if len(values) == 9:
            cards.append([values[2],values[3], values[5],values[7],values[8]])
        elif len(values) == 6:
            cards.append([values[2],values[3],values[4], "N/A", values[5]])
        elif len(values) == 8:
            cards.append([values[2],values[3],values[5],"N/A", values[7]])
    return cards


def add_static_ip(port, ip, subnet, gateway, dns1, dns2, vlan):

    global tn
    tn = telnetlib.Telnet(HOST, 2333)

    tn.read_until(b"Username:")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\n")
        tn.read_until(b"#")
    tn.write(str.encode("conf t\n"))
    tn.read_until(b"#")
    commands = [
    "pon-onu-mng {}".format(port),
    "flow mode 1 tag-filter vid-filter untag-filter discard",
    "flow 1 priority 0 vid {}".format(vlan),
    "gemport 1 flow 1",
    "switchport-bind switch_0/1 iphost 1",
    "switchport-bind switch_0/1 veip 1",
    "ip-host 1 ip {} mask {} gateway {}".format(ip, subnet, gateway),
    "ip-host 1 primary-dns {} second-dns {}".format(dns1, dns2),
    "vlan-filter-mode iphost 1 tag-filter vid-filter untag-filter discard",
    "vlan-filter iphost 1 priority 0 vid {}".format(vlan)
    ]
    for no in range(1,onu_port_nr):
        commands.append("dhcp-ip ethuni eth_0/{} from-onu".format(no))
    send_multiple(commands)
    response = tn.read_until(b"#").decode('ascii')
    log(response)

def set_bridge(port, vlan, onu_port_nr):

    global tn
    tn = telnetlib.Telnet(HOST, 2333)

    tn.read_until(b"Username:")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\n")
        tn.read_until(b"#")
    tn.write(str.encode("conf t\n"))
    tn.read_until(b"#")


    commands = [
    "pon-onu-mng {}".format(port),
    "flow mode 1 tag-filter vid-filter untag-filter discard",
    "flow 1 priority 0 vid 1236".format(vlan),
    "gemport 1 flow 1",
    "switchport-bind switch_0/1 veip 1",
    "security-mng 998 state enable mode permit ingress-type lan",
    "security-mng 999 state enable ingress-type lan protocol ftp telnet ssh snmp tr069"
    ]


    for no in range(1,onu_port_nr):
        commands.append("loop-detect ethuni eth_0/{} enable".format(no))
        commands.append("vlan port eth_0/{} mode tag vlan {}".format(no, vlan))
        commands.append("dhcp-ip ethuni eth_0/{} from-internet".format(no))
    send_multiple(commands)
    response = tn.read_until(b"#").decode('ascii')
    log(response)

def add_olt(name, ip, telnet_user, telnet_pass, telnet_port):
    sql = "INSERT INTO `olts`(`name`, `ip`, `telnet_user`, `telnet_pass`, `telnet_port`) VALUES (%s, %s, %s, %s, %s)"
    val = (name, ip, telnet_user, telnet_pass, telnet_port)
    mycursor.execute(sql, val)
    mydb.commit()
    global tn_connection
    tn_connection = telnetlib.Telnet(ip, telnet_port)

    log(tn_connection.read_until(b"Username:"))
    tn_connection.write(user.encode('ascii') + b"\n")
    log(tn_connection.read_until(b"Password:"))
    tn_connection.write(password.encode('ascii') + b"\n")
    log(tn_connection.read_until(b"#"))
    add_cards(tn_connection, mycursor.lastrowid)

def add_cards(tn_connection, olt_id):
# types:
#     0 - uplink
#     1 - pon
#     2 - mng
#     3 - pwr
#     4 - unknown
    cards = get_olt_cards(tn_connection)

    for card in cards:
        uplink_ports = None
        pon_ports = None

        if card[1] in ["GTGO", "GTGH"]:
            type = 1
            pon_ports = card[2]
            ports = int(card[2])
        elif card[1] in ["PRWH"]:
            type = 3
        elif card[1] in ["SCXN"]:
            type = 2
        elif card[1] in ["HUVQ", "GUFQ"]:
            uplink_ports = card[2]
            ports = int(card[2])
            type = 0
        else:
            type = 4

        sql = "INSERT INTO `cards`(`olt_id`, `olt_slot`, `type`, `type_name`, `uplink_ports`, `pon_ports`) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (olt_id, card[0], type, card[1], uplink_ports, pon_ports)
        mycursor.execute(sql, val)
        mydb.commit()
        print(card[4])
        if type <= 1 and card[4] != "OFFLINE":
            add_ports(type, mycursor.lastrowid, ports)

def add_ports(type, card_id, port_nr):
    if type == 1:
        for i in range(1,port_nr+1):

            sql = "INSERT INTO `pon_ports`(`port_nr`, `card_id`) VALUES (%s, %s)"
            val = (i, card_id)
            mycursor.execute(sql, val)
            mydb.commit()
            port_id = mycursor.lastrowid
            for j in range(1, 129):
                sql = "INSERT INTO `onu_vports`( `pon_port_id`, `vport_number`) VALUES (%s, %s)"
                val = (port_id, j)
                mycursor.execute(sql, val)
                mydb.commit()


# add_cards()
add_olt("kov", "89.46.237.100", "smartoltusr", "Wx87NJ3TGm4Rv2", 2333)

# add_static_ip("gpon-onu_0/13/1:1", "89.46.234.12", "255.255.255.0", "89.46.234.1", "1.1.1.1", "8.8.8.8", "1234", 4)


# TRUNCATE `cards`;TRUNCATE  `olts`;TRUNCATE `onu_vports`;TRUNCATE`pon_ports`
# .1.3.6.1.4.1.3902.1012.3.50.12.1.1.10.268763392.1.1
# gpon-onu_0/5/1:1


# for i in range(40,128):
#     signal_values = get_signal("gpon-onu_0/5/1:" + str(i))
#     log("Signal loss: " + str(signal_values[0]) + "/" + str(signal_values[1]))
#
#     traffic_values = get_traffic("gpon-onu_0/5/1:" + str(i))
#     log("Input: " + str(traffic_values[0][0]) + traffic_values[0][1] + "  " + traffic_values[1] + " pps" + " --- Output: "+ str(traffic_values[2][0]) + traffic_values[2][1] + "  " + traffic_values[3] + "pps")
#     log("Peak Input: " + str(traffic_values[4][0]) + traffic_values[4][1] + "  " + traffic_values[5] + " pps" + " --- Peak Output: "+ str(traffic_values[6][0]) + traffic_values[6][1] + "  " + traffic_values[7] + "pps")
#     log("-------------------------------------------------------")

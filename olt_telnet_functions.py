from utils import *
import mysql.connector
import telnetlib


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="olt_management"
)

mycursor = mydb.cursor()

def connect(HOST, user, password, port):
    tn_connection = telnetlib.Telnet(HOST, port)

    tn_connection.read_until(b"Username:")
    tn_connection.write(user.encode('ascii') + b"\n")
    tn_connection.read_until(b"Password:")
    tn_connection.write(password.encode('ascii') + b"\n")
    tn_connection.read_until(b"#")
    return tn_connection


def get_traffic_telnet(port, tn_connection):
    command = "show interface " + port + "\n"
    tn_connection.write(str.encode(command))
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)
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
        input_all_bdw = format_bytes(int(clean_traffic(raw_input_all)[0]))
        input_all_pps = clean_traffic(raw_input_all)[1]
        output_all_bdw = format_bytes(int(clean_traffic(raw_output_all)[0]))
        output_all_pps = clean_traffic(raw_output_all)[1]
        return [input_curr_bdw,input_curr_pps,output_curr_bdw,output_curr_pps,input_all_bdw,input_all_pps,output_all_bdw,output_all_pps]
    except Exception as e:
        print(e)
        return[["0","bps"],"0",["0","bps"],"0",["0","bps"],"0",["0","bps"],"0",]


def get_signal_telnet(port, tn_connection):

    command = "show pon power att " + port + "\n"
    tn_connection.write(str.encode(command))
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)
    try:
        split = response.split("Rx")
        value2 = split[1][2:9]
        value1 = split[2][1:8]
        return [value1,value2[:-1]]
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


def add_static_ip(port, ip, subnet, gateway, dns1, dns2, vlan, onu_port_nr, tn_connection):

    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")
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
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def set_pppoe(port, username, password, onu_port_nr, tn_connection):

    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")
    commands = [
    "pon-onu-mng {}".format(port),
    "no pppoe 1",
    "no ip-host 1"
    "no vlan-filter-mode ip host 1",
    "switchport-bind switch_0/1 iphost 1",
    "switchport-bind switch_0/1 veip 1",
    "vlan-filter-mode iphost 1 tag-filter vid-filter untag-filter discard",
    "vlan-filter iphost 1 priority 0 vid {}".format(vlan),
    "pppoe 1 nat enable connect always user {} password {}".format(username, password),
    ]
    for no in range(1,onu_port_nr):
        commands.append("dhcp-ip ethuni eth_0/{} from-onu".format(no))
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def set_bridge(port, vlan, onu_port_nr, tn_connection):
    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")


    commands = [
    "pon-onu-mng {}".format(port),
    "flow mode 1 tag-filter vid-filter untag-filter discard",
    "flow 1 priority 0 vid {}".format(vlan),
    "gemport 1 flow 1",
    "switchport-bind switch_0/1 veip 1",
    "security-mng 998 state enable mode permit ingress-type lan",
    "security-mng 999 state enable ingress-type lan protocol ftp telnet ssh snmp tr069"
    ]


    for no in range(1,onu_port_nr):
        commands.append("loop-detect ethuni eth_0/{} enable".format(no))
        commands.append("vlan port eth_0/{} mode tag vlan {}".format(no, vlan))
        commands.append("dhcp-ip ethuni eth_0/{} from-internet".format(no))
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def add_olt(name, ip, telnet_user, telnet_pass, telnet_port, snmp_port):
    global tn_connection
    tn_connection = telnetlib.Telnet(ip, telnet_port)

    log(tn_connection.read_until(b"Username:"))
    tn_connection.write(user.encode('ascii') + b"\n")
    log(tn_connection.read_until(b"Password:"))
    tn_connection.write(password.encode('ascii') + b"\n")
    log(tn_connection.read_until(b"#"))
    add_cards(tn_connection, mycursor.lastrowid)
    snmp_comms = init_olt(tn_connection)

    sql = "INSERT INTO `olts`(`name`, `ip`, `telnet_user`, `telnet_pass`, `telnet_port`, `r_community`, `rw_community`, `snmp_port`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (name, ip, telnet_user, telnet_pass, telnet_port, snmp_comms[0], snmp_comms[1], snmp_port)
    mycursor.execute(sql, val)
    mydb.commit()

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


def init_olt(tn_connection):
    from datetime import datetime
    now = datetime.now()
    formated_date = now.strftime("%H:%M:%S %m %d %y")
    r_comm = random_string(12)
    rw_comm = random_string(12)
    commands = [
    "conf t",
    "auto-write enable",
    "auto-write 18:00:00  everyday",
    "snmp-server view allview 1.3 included",
    "snmp-server community {} view allview ro".format(r_comm),
    "snmp-server community {} view allview rw".format(rw_comm),
    "clock set {}".format(formated_date),
    "ntp server 10.11.12.254 priority 2 version 3",
    "ntp server 93.190.144.3 priority 3 version 3",
    "no ntp alarm-threshold",
    "no ntp enable",
    "ntp enable",
    "line telnet idle-timeout 60",
    "line telnet absolute-timeout 9999",
    "end",
    "exit",
    ]


    mycursor.execute("SELECT * FROM speed_profiles")

    profiles = mycursor.fetchall()
    commands.append("conf t")
    commands.append("gpon")
    for profile in profiles:

        if profile[2] == 0:
            command.append("profile traffic {} sir {} pir {}".format("MNGR_"+profile[1]+"_DW", profile[3], profile[3]))

        if profile[2] == 1:
            commands.append("profile tcont {} type 5 fixed 64 assured 64 maximum {}".format("MNGR_"+profile[1]+"_UP", profile[3], profile[3]))


    commands.append("exit")
    commands.append("end")
    send_multiple(commands, tn_connection)
    return [r_comm, rw_comm]

def get_unconf(tn_connection):
    command = "show gpon onu uncfg\n"
    tn_connection.write(str.encode(command))
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)
    if "32310" not in response:
        response = response.splitlines()
        onus = []
        for line in response[3:-1]:
            values = line.split()
            onus.append([values[0], values[1]])
        return onus
    else:
        return []

def authorize(sn, unauth_port, name, address, device_type, vlan, olt_id, tn_connection):

    mycursor.execute("SELECT name, nr_ports, id FROM device_types WHERE id = {}".format(device_type))
    dev_type = mycursor.fetchone()

    commands = [
    "conf t",
    "interface {}".format(unauth_port.split(":")[0].replace("onu", "olt")),
    "no onu {}".format(unauth_port.split(":")[1]),
    "onu {} type {} sn {}".format(unauth_port.split(":")[1], dev_type[0], sn),
    "exit",
    "interface {}".format(unauth_port),
    "name {}".format(name.replace(" ", "_")),
    "description {}".format(sn),
    "tcont 1 profile smartolt-1g-up",
    "gemport 1 unicast tcont 1 dir both",
    "gemport 1 traffic-limit downstream smartolt-100m-down",
    "switchport mode hybrid vport 1",
    "switchport vlan 1236 tag vport 1",
    "exit"]


    commands.append("pon-onu-mng {}".format(unauth_port))
    commands.append("flow mode 1 tag-filter vid-filter untag-filter discard")
    commands.append("flow 1 priority 0 vid {}".format(vlan))
    commands.append("gemport 1 flow 1")
    commands.append("switchport-bind switch_0/1 veip 1")
    commands.append("security-mng 998 state enable mode permit ingress-type lan")
    commands.append("security-mng 999 state enable ingress-type lan protocol ftp telnet ssh snmp tr069")

    for no in range(1,int(dev_type[1])):
        commands.append("loop-detect ethuni eth_0/{} enable".format(no))
        commands.append("vlan port eth_0/{} mode tag vlan {}".format(no, vlan))
        commands.append("dhcp-ip ethuni eth_0/{} from-internet".format(no))
    commands.append("end")
    send_multiple(commands, tn_connection)
    sql = "INSERT INTO `clients`(`name`, `sn`, `address`, `device_type`, `olt_id`, `port`) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (name, sn, address, dev_type[2], olt_id, unauth_port)
    mycursor.execute(sql, val)
    mydb.commit()

def delete(onu_port, tn_connection):
    mycursor.execute("DELETE FROM clients WHERE port = '{}'".format(onu_port))
    mydb.commit()
    commands = [
    "conf t",
    "interface {}".format(onu_port.split(":")[0].replace("onu", "olt")),
    "no onu {}".format(onu_port.split(":")[1]),
    "end",
    ]
    send_multiple(commands, tn_connection)

def attach_vlan_onu(vlan, client_port, tn_connection):
    # TODO: add device type wlan and eth index

    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")

    commands = [
    "interface {}".format(client_port),
    "switchport vlan {} tag vport 1".format(vlan),
    "exit",
    "pon-onu-mng {}".format(client_port),
    "end"
    ]
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def add_vlan_onu_port(vlan, client_port, onu_port_nr, untag, tn_connection):

    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")

    commands = [
    "pon-onu-mng {}".format(client_port),
    "dhcp-ip ethuni eth_0/{} from-internet".format(onu_port_nr),
    "no vlan port eth_0/{} mode".format(onu_port_nr)
    ]
    if untag == 1:
        commands.append("vlan port eth_0/{} mode hybrid def-vlan {}".format(onu_port_nr, vlan))
    else:
        commands.append("vlan port eth_0/{} modetag vlan {}".format(onu_port_nr, vlan))
    commands.append("end")
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def set_wlan(port, wlan_port_nr, ssid, password, tn_connection):
    commands=[
    "conf t",
    "pon-onu-mng {}".format(port),
    "wifi enable",
    "interface wifi wifi_0/{}".format(wlan_port_nr),
    "ssid ctrl wifi_0/{} name {}".format(wlan_port_nr, ssid),
    "ssid auth wpa wifi_0/{} wpa2-psk encrypt aes key {}".format(wlan_port_nr, password),
    "end"
    ]
    send_multiple(commands, tn_connection)
    response = tn_connection.read_until(b"#").decode('ascii')
    log(response)

def parse_onu_config(config, port, tn_connection):
    lines = config.splitlines()
    main_vlan = 1
    # mycursor.execute("inner join get onu".format(device_type))
    # onu_port_nr = mycursor.fetchone()
    onu_port_nr = 4 #TODO get this from onu type

    for line in lines:
        line = line.split(":")
        if line[0]=="att_vlans":
            vlans = line[1].split(",")
            for vlan in vlans:
                print(vlan, port, tn_connection)
                # attach_vlan_onu(vlan, port, tn_connection)
        elif line[0] == "main_vlan":
            main_vlan = line[1]
            # set_bridge(port, line[1], onu_port_nr, tn_connection)
            # TODO add and test
            print(port, line[1], onu_port_nr, tn_connection)
        elif line[0] == "conn":
            if line[1] == "ip":
                settings = line[2].split(',')
                # add_static_ip(port, settings[0], settings[1], settings[2], settings[3], settings[4], vlan, onu_port_nr, tn_connection)
                # TODO add and test
                print(port, settings[0], settings[1], settings[2], settings[3], settings[4], main_vlan, onu_port_nr, tn_connection)
            if line[1] == "pppoe":
                settings = line[2].split(',')
                print(port, settings[0], settings[1], onu_port_nr, tn_connection)
                # set_pppoe(port, settings[0], setting[1], onu_port_nr, tn_connection)
                # TODO add and test
        elif "eth" in line[0]:
            onu_port = line[0].split('eth')
            onu_port_nr = onu_port[0]
            if line[1] == "vlan":
                settings = line[2].split("/")
                untag = settings[0].split(';')
                tag = settings[1].split(';')
                if untag[0]=="untag":
                    # add_vlan_onu_port(untag[1], port, port_nr, 1, tn_connection)
                    # TODO add and test
                    print(untag[1], port, onu_port_nr, 1, tn_connection)
                if tag[0] == "tag":
                    vlans = tag[1].split(",")
                    for vlan in vlans:
                        # add_vlan_onu_port(untag[1], port, onu_port_nr, 0, tn_connection)
                        # TODO add and test
                        print(vlan, port, onu_port_nr, 0, tn_connection)
        elif "wlan" in line[0]:
            wlan_port = line[0].split('wlan')
            wlan_port_nr = onu_port[0]
            if line[1] == "ssid":
                # set_wlan(port, wlan_port_nr, line[2], line[3], vlan,  tn_connection)
                print(port, wlan_port_nr, line[2], line[3], tn_connection)
                # TODO add and test

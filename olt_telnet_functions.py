from utils import *

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


def get_signal_telnet(port, tn_connection):

    command = "show pon power att " + port + "\n"
    tn_connection.write(str.encode(command))
    response = tn_connection.read_until(b"#").decode('ascii')
    try:
        split = response.split("Rx")
        value2 = split[1][2:9]
        value1 = split[2][1:8]
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


def add_static_ip(port, ip, subnet, gateway, dns1, dns2, vlan, tn_connection):

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

def set_bridge(port, vlan, onu_port_nr, tn_connection):
    tn_connection.write(str.encode("conf t\n"))
    tn_connection.read_until(b"#")


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
    response = response.splitlines()
    onus = []
    for line in response[3:-1]:
        values = line.split()
        onus.append([values[0], values[1]])
    return onus
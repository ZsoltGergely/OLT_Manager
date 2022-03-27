def get_data_onu():
    id = input("Client ID: ")
    mycursor.execute(
    """SELECT olts.ip, olts.telnet_user, olts.telnet_pass, olts.telnet_port, clients.port, clients.name  FROM `clients`
    INNER Join olts ON clients.olt_id = olts.id
    Where clients.id = {}""".format(id))
    client = mycursor.fetchone()
    # print(client)
    # print(client[0], client[1], client[2], client[3])
    tn_connection = connect(client[0], client[1], client[2], client[3])
    signal = get_signal_telnet(client[4], tn_connection)
    traffic = get_traffic_telnet(client[4], tn_connection)
    print("""
    _________________________________________________
    | Name: {}
    | Signal: {}/{}
    | Traffic:
    |   Inbound: {}{} {}pps - All-time: {}{} {}pps
    |   Outbound: {}{} {}pps - All-time: {}{} {}pps
    |
    |
    |
    -------------------------------------------------
    """.format(client[5], str(signal[0]), str(signal[1]), str(traffic[0][0]), str(traffic[0][1]), str(traffic[1]), str(traffic[4][0]), str(traffic[4][1]), str(traffic[5]), str(traffic[2][0]), str(traffic[2][1]), str(traffic[3]),
    str(traffic[6][0]), str(traffic[6][1]),str(traffic[7])))

def list_unconfig():
    mycursor.execute("SELECT id, ip, telnet_user, telnet_pass, telnet_port, name FROM olts")
    olts = mycursor.fetchall()
    for olt in olts:
        tn_connection = connect(olt[1], olt[2], olt[3], olt[4])
        onus = get_unconf(tn_connection)
        print("---------{}.{}---------".format(olt[0], olt[5]))
        for onu in onus:
            print(onu[0] + "    ------     " + onu[1] )

def list_clients():
    mycursor.execute("SELECT clients.port, clients.name, olts.ip, olts.telnet_user, olts.telnet_pass, olts.telnet_port, olts.name FROM clients INNER Join olts ON clients.olt_id = olts.id")
    clients = mycursor.fetchall()
    print("_________________________________________________________________")
    for client in clients:
        tn_connection = connect(client[2], client[3], client[4], client[5])
        signal = get_signal_telnet(client[0], tn_connection)
        print("| "+client[0] + " - " + client[6].strip() + " - " + client[1] + " - " + str(signal[0])+"/"+ str(signal[1]))
    print("----------------------------------------------------------------")
    
def cli_authorize():
    olt_id = input("OLT id: ")
    unauth_port = input("ONU Port: ")
    sn = input("ONU Serial Number: ")
    name = input("Client Name: ")
    address = input("Client Address: ")
    device_type = input("Device Type ID: ")
    vlan = input("Main Vlan id: ")
    mycursor.execute("SELECT id, ip, telnet_user, telnet_pass, telnet_port, name FROM olts WHERE id = {}".format(olt_id))
    olt = mycursor.fetchone()
    tn_connection = connect(olt[1], olt[2], olt[3], olt[4])
    try:
        authorize(sn, unauth_port, name, address, device_type, vlan, olt_id, tn_connection)
        print("SUCCESS")
    except:
        print("ONU authorization FAILED")

def edit_onu_config():
    client_id = input("Client id: ")
    newconfig = ""
    mycursor.execute("SELECT clients.port, clients.config, olts.ip, olts.telnet_user, olts.telnet_pass, olts.telnet_port FROM clients INNER Join olts ON clients.olt_id = olts.id WHERE id = {}".format(client_id))
    client = mycursor.fetchone()
    print(client[1])
    print("----------------------------------------------------------------")
    print("Enter new config line by line or press 'enter' to send /  'backspace + enter' to cancel:")
    newconfig = ""
    cancel = 0
    while True:
        line = input()
        if line == "\b":
            cancel = 1
            break
        elif line == "":
            break

        else:
            newconfig+=line+"\n"
    if not cancel:
        print("----------------------------------------------------------------")
        print(newconfig)
        if input("Are you sure about applying config?(y/n)") == "y":
            mycursor.execute("UPDATE clients SET config = '{}' WHERE id = {}".format(newconfig, client_id))
            mydb.commit()
            print("Uploaded to DB successfully")

            # tn_connection = connect(client[2], client[3], client[4], client[5])
            # parse_onu_config(newconfig, client[0], tn_connection)
            # print("Uploaded to OLT successfully")
            # TODO teston olt

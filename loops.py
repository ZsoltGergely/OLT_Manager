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
            val = (onu[0], signal[0], signal[1], traffic[0][0], traffic[1], traffic[2][0], traffic[3])
            mycursor.execute(sql, val)
            mydb.commit()
        tn_connection.close()

def options():
    print ("""
    -----OPTIONS-----
    1. List Unconfigured ONUs
    2. List Clients
    3. Authorize ONU
    4. Edit ONU Config
    5. Get data of ONU
    6. List OLTs
    7. Initialize OLT
    -----------------
    """)
    choice = input("Choice: ")
    if choice == "1":
        list_unconfig()
    elif choice == "2":
        list_clients()
    elif choice == "3":
        cli_authorize()
    elif choice == "4":
        edit_onu_config()
    elif choice == "5":
        get_data_onu()
    # elif input == 6:

    # elif input == 7:
    # elif input == 8:
    # elif input == 9:

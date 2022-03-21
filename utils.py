import string
import random
import telnetlib


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

def clean_traffic(raw):
    bps_ind = raw.find("bps")
    pps_ind = raw.find("pps")
    bps_val = raw[0:bps_ind]
    pps_val = raw[bps_ind+3:pps_ind]
    return [bps_val, pps_val]

def random_string(size):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = size))

def send_multiple(lines, tn_connection):
    for line in lines:
        tn_connection.write(str.encode(line+"\n"))
        log(tn_connection.read_until(b"#").decode('ascii'))

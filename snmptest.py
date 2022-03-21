from easysnmp import snmp_get, snmp_set, snmp_walk, snmp_get_next

unconf = snmp_get_next(
'1.3.6.1.4.1.3902.1012.3.13.3.1.2',
hostname='89.46.237.100',
community='ZwgBf9ieCItz',
version=2, remote_port=2161)

print(unconf)

# print(session.get_next("))

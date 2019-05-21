from OltZTE import OltZTE

olt_pass = '/home/sanduka/olt_pass'

with open(olt_pass, 'r') as file:
    user, passw = file.read().split()

hosts = ['10.133.244.2']

TEMPLATE = 'zte_gpon_onu.jnj'
CVLAN_START = 1001

for host in hosts:
    client = OltZTE(host,user,passw)
    client.connect()

    uncfg_onu = client.get_uncfg_onu()

    if uncfg_onu:
        reg_data = client.get_data(uncfg_onu, CVLAN_START)
        if reg_data:
            reg_template = client.generate_cfg_from_template(TEMPLATE, reg_data)
            client.register_onu(reg_template)


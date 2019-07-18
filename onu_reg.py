from OltZTE import OltZTE

HOSTS = ['192.168.100.2']
OLT_PASS = 'olt_pass'
TEMPLATE = 'zte_gpon_onu.jnj'
CVLAN_START = 1000

with open(OLT_PASS, 'r') as file:
    user, passw = file.read().split()

for host in HOSTS:
    client = OltZTE(host,user,passw)
    client.connect()

    uncfg_onu = client.get_uncfg_onu()

    if uncfg_onu:
        reg_data = client.get_data(uncfg_onu, CVLAN_START)
        if reg_data:
            reg_template = client.generate_cfg_from_template(TEMPLATE, reg_data)
            client.register_onu(reg_template)

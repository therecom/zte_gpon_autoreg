import time
import pexpect
import re

device_params = {'ip': '1.1.1.1', 'username': 'test1', 'password': 'test2'}

#def olt_ssh(ip, username, password):
#    ssh = pexpect.spawn('ssh {}@{}'.format(username,ip))
#    time.sleep(1)
#    ssh.sendline(password)
#    time.sleep(1)
#    ssh.expect('#')
#
#    ssh.sendline('sho ip in b')
#    ssh.expect('#')
#
#    show_output = ssh.before.decode('utf-8')
#    ssh.sendline('exit')
#    print(show_output)

'''
Создание подключения к olt
'''
def olt_ssh(ip, username, password):
    '''
    input: ip адрес и параметры
    авторизации для olt zte
    output: объект-подключение по ssh
    '''
    ssh = pexpect.spawn('ssh {}@{}'.format(username,ip))
    time.sleep(1)
    ssh.sendline(password)
    time.sleep(1)
    ssh.expect('#')
    return ssh

'''
Просмотр незарегистрированных ону и создание словарей вида {'1/1/4': ['HWTC155B8B9D']}
'''
def sh_onu_uncfg(olt_ssh):
    '''
    input:  подключение к olt
    output: False/Словарь
    '''
    olt_ssh.sendline('sho gp on u')
    olt_ssh.expect('#')
    show_output = ssh.before.decode('utf-8')
    if 'No related' in show_output:
        uncfg_onu_dict = False
    else:
        regex1 = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
        uncfg_onu_dict = {}
        uncfg_onu__raw = re.finditer(regex1, show_output)
        for match in uncfg_onu__raw:
            port = match.group('PON_PORT')
            sn = match.group('SN')
            if uncfg_onu_dict.get(port) == None:
                uncfg_onu_dict[port] = [{sn:[]}]
            else:
                uncfg_onu_dict[port].append({sn:[]})
    return uncfg_onu_dict

# for parsing output:
#show gpon onu uncfg command output:
#
#panorama-gpon#show gpon onu uncfg 
#%Code 32310-GPONSRV : No related information to show.
#panorama-gpon#
#
#panorama-gpon#show gpon onu uncfg 
#OnuIndex                 Sn                  State
#---------------------------------------------------------------------
#gpon-onu_1/1/2:1         HWTC12930F9D        unknown
#
#changed:
#
#regex = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
#
panorama-gpon#show gpon onu uncfg                 
OnuIndex                 Sn                  State
---------------------------------------------------------------------
gpon-onu_1/1/2:1         HWTC111            unknown
gpon-onu_1/1/2:1         HWTC222            unknown
gpon-onu_1/2/1:1         HWTC333            unknown


def cvlan_port(olt_ssh, uncfg_onu_dict, CVLAN_START):
'''
input: olt_connection, список незарегистрированных ону, старт диапазона для cvlan
output: словарь вида uncfg_onu_dict = {'1/1/2': [{'HWTC111': [7, 133]}, {'HWTC222': [12, 137]}], '1/2/1': [{'HWTC333': [5, 3077]}]}
'''
olt_connection.sendline('terminal length 0')
olt_connection.expect('#')
for pon_port in uncfg_onu_dict.keys(): # для каждого пон порта ищем список зарегистрированных ону из конфига
    print(pon_port)
    gpon_port = int(pon_port.split('/')[-1]) # pon_port - полный номер(1/1/2), gpon_port - номер порта на плате(2)
    olt_connection.sendline('show running-config interface gpon-olt_{}'.format(pon_port))
    olt_connection.expect('#')
    run_cfg_raw = olt_connection.before.decode('utf-8')
    run_cfg_raw = run_cfg_raw.split('\n')
    cur_onu_list = []
    for line in run_cfg_raw:
        if 'type' in line:
            cur_onu_list.append(line) # зарегистрированные ону
    cur_onu_nums = []
    for line in cur_onu_list: # собираем номера зарегистрированных ону
        cur_onu_nums.append(int(line.split()[1]))
    all_onu_nums = list(range(1,129)) # возможные номера ону
    for num in cur_onu_nums:
        all_onu_nums.remove(num) # из списка возможных номеров убираем зарегистрированные и получаем список свободных портов
    for sn in uncfg_onu_dict[pon_port]:  # проходимся по списку из незарегистрированных ону на пон порту
        for value in sn:         # записываем первый свободный слот для каждой незарегистрированной ону
            free_onu_num = all_onu_nums.pop(0)
            cvlan = CVLAN_START + (128 * gpon_port - 1) + free_onu_num # расчет cvlan на основании свободного порта и консанты
            sn[value] = [free_onu_num] # назначение номера для onu
            sn[value].append(cvlan)  # назначение cvlan для onu


#test
#pon_port = 1/1/2
#CVLAN_START = 1000
#cur_onu_list

uncfg_onu_dict = {'1/1/2': [{'HWTC111': []}, {'HWTC222': []}], '1/2/1': [{'HWTC333': []}]}

1/1/4
onu 1 type GPON sn HWTC1E4F089D
onu 2 type GPON sn HWTC17DA3C9D
onu 3 type GPON sn HWTC17D5069D
onu 4 type GPON sn HWTC18F3FB9B
onu 5 type GPON sn HWTC108AA99D
onu 6 type GPON sn HWTC1DE25F9B
onu 8 type GPON sn HWTC1FA3DB9D
onu 9 type GPON sn HWTC1785159D
onu 10 type GPON sn HWTC193D9B9D
onu 11 type GPON sn ZTEGC1400021
onu 13 type GPON sn ZTEGC11FC92D

Расчет номер cvlan для onu:
const = 1000
1/SHELF_NUM/PORT_NUM:ONU_NUM

const + (128 * (PORT_NUM - 1)) + ONU_NUM
для ону 1/1/5:32 cvlan = 1000 + (128 * (5 - 1)) + 32 = 1554


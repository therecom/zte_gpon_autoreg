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
def sh_onu_uncfg(ssh):
    '''
    input:  подключение к olt
    output: False/Словарь
    '''
    ssh.sendline('sho gp on u')
    ssh.expect('#')
    show_output = ssh.before.decode('utf-8')
    if 'No related' in show_output:
        result = False
    else:
        regex1 = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
        result = {}
        result_raw = re.finditer(regex1, show_output)
        for match in result_raw:
            port = match.group('PON_PORT')
            sn = match.group('SN')
            if result.get(port) == None:
                result[port] = [sn]
            else:
                result[port].append(sn)
    return result


#result = {}
#result_raw = re.finditer(regex1, show_output)
#for match in result_raw:
#    port = match.group('PON_PORT')
#    sn = match.group('SN')
#    if result.get(port) == None:
#        result[port] = [sn]
#    else:
#        result[port].append(sn)


show gpon onu uncfg command output:

panorama-gpon#show gpon onu uncfg 
%Code 32310-GPONSRV : No related information to show.
panorama-gpon#

panorama-gpon#show gpon onu uncfg 
OnuIndex                 Sn                  State
---------------------------------------------------------------------
gpon-onu_1/1/2:1         HWTC12930F9D        unknown

changed:

regex = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'

panorama-gpon#show gpon onu uncfg                 
OnuIndex                 Sn                  State
---------------------------------------------------------------------
gpon-onu_1/1/2:1         HWTC111            unknown
gpon-onu_1/1/2:1         HWTC222            unknown
gpon-onu_1/2/1:1         HWTC333            unknown



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
onu 12 type GPON sn ZTEGC14D1A51
onu 13 type GPON sn ZTEGC11FC92D



Расчет номер cvlan для onu:
const = 1000
1/SHELF_NUM/PORT_NUM:ONU_NUM

const + (128 * (PORT_NUM - 1)) + ONU_NUM
для ону 1/1/5:32 cvlan = 1000 + (128 * (5 - 1)) + 32 = 1554


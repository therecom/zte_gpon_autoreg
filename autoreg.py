import time
import pexpect
import re

'''
Создание подключения к olt
'''
def zte_ssh(ip, username, password):
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
    ssh.sendline('terminal length 0')
    ssh.expect('#')
    return ssh

'''
Просмотр незарегистрированных ону и создание словарей вида {'1/1/2': [{'HWTC111': []}, {'HWTC222': []}], '1/2/1': [{'HWTC333': []}]}
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

def params_gen(olt_ssh, uncfg_onu_dict, CVLAN_START):
    '''
    input: olt_ss, словарь незарегистрированных ону, старт диапазона для cvlan
    output: словарь вида uncfg_onu_dict = {'1/1/2': [{'HWTC111': [7, 133]}, {'HWTC222': [12, 137]}], '1/2/1': [{'HWTC333': [5, 3077]}]}
    '''
    for pon_port in uncfg_onu_dict.keys(): # для каждого пон порта ищем список зарегистрированных ону из конфига
        gpon_port = int(pon_port.split('/')[-1]) # pon_port - полный номер(1/1/2), gpon_port - номер порта на плате(2)
        #получаем конфиг пон порта в виде списка строк
        olt_ssh.sendline('show running-config interface gpon-olt_{}'.format(pon_port))
        olt_ssh.expect('#')
        run_cfg_raw = olt_ssh.before.decode('utf-8')
        run_cfg_raw = run_cfg_raw.split('\n')
        #получаем список зарегистрированных ону
        cur_onu_list = []
        for line in run_cfg_raw:
            if 'type' in line:
                cur_onu_list.append(line) # зарегистрированные ону
        #получаем номера зарег-х ону, считаем свободные порты
        cur_onu_nums = []
        for line in cur_onu_list:
            cur_onu_nums.append(int(line.split()[1]))
        all_onu_nums = list(range(1,129))
        for num in cur_onu_nums:
            all_onu_nums.remove(num)
        #назначаем свободный порт и cvlan незарегистрированным ону
        for sn in uncfg_onu_dict[pon_port]:
            for value in sn:
                free_onu_num = all_onu_nums.pop(0)
                cvlan = CVLAN_START + (128 * gpon_port - 1) + free_onu_num
                sn[value] = [free_onu_num]
                sn[value].append(cvlan)
    return uncfg_onu_dict

if __name__ == '__main__':

    device_params = {'ip': '1.1.1.1', 'username': 'test1', 'password': 'test2'}
    CVLAN_START = 1000

    ssh_connection = zte_ssh(**device_params)
    uncfg_onu_dict = sh_onu_uncfg(ssh_connection)
    onu_params = params_gen(ssh_connection, uncfg_onu_dict, CVLAN_START)



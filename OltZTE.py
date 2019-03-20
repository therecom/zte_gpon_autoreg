from Olt import Olt
import paramiko
import time
import re
from jinja2 import Environment, FileSystemLoader
from olt_logging import send_log

class OltZTE(paramiko.SSHClient, Olt):

    SLOTS = set(range(1, 129))
    logger = send_log('send_command')

    def __init__(self, host, username='', password=''):
        self.host = host
        self.username = username
        self.password = password
        super().__init__()

    def log_test(self, message):
        self.logger.warning(message)


    def connect(self):
        """Tries to make ssh connection. Log if errors occurs """

        try:
            super().set_missing_host_key_policy(paramiko.AutoAddPolicy())
            super().connect(self.host,
                            username=self.username,
                            password=self.password,
                            look_for_keys=False,
                            allow_agent=False)

        except paramiko.AuthenticationException:
            print("Authentication error occured.")

        except paramiko.SSHException:
            print("Connection error occured.")

        except paramiko.TimeouteError:
            print("Timeout error occured.")

        with super().invoke_shell() as ssh:
            ssh.send('terminal length 0\n')
            time.sleep(1)

        # FIXME
        # logging

    def send_commands(self, commands, timeout=1):

        with super().invoke_shell() as ssh:
            if type(commands) == str:
                ssh.send('{}\n'.format(commands))
            else:
                for command in commands:
                    ssh.send('{}\n'.format(command))
            time.sleep(timeout)
            output = ssh.recv(5000).decode('utf-8')
            if 'Invalid input' in output:
                self.logger.warning('Invalid input detected while executing command:\n"{}"'
                .format(commands))
            else:
                self.logger.debug(output)


        return output

    def get_uncfg_onu(self):
        """Returns dict with PON ports as keys and uncfg ONUs' sn's lists as
        values: {pon_port1: [sn1, sn2, snN], ...}"""
        UNCFG_ONU = ('show gp on u',)
        output = self.send_commands(UNCFG_ONU)
        if 'No related' in output:
            uncfg_onu_dict = False
        else:
            re_uncfg_onu = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
            uncfg_onu_dict = {}
            uncfg_onu_raw = re.finditer(re_uncfg_onu, output)
            for match in uncfg_onu_raw:
                port = match.group('PON_PORT')
                sn = match.group('SN')
                if uncfg_onu_dict.get(port) == None:
                    uncfg_onu_dict[port] = [{sn:[]}]
                else:
                    uncfg_onu_dict[port].append({sn:[]})
        return uncfg_onu_dict

    def get_free_slots(self, uncfg_onu_dict, CVLAN_START):
        """Returns dict with PON ports as keys and sorted lists of free
        slots as values.
        input: olt_ss, словарь незарегистрированных ону, старт диапазона для cvlan
        output: словарь вида uncfg_onu_dict = {'1/1/2': [{'HWTC111': [7, 133]}, {'HWTC222': [12, 137]}], '1/2/1': [{'HWTC333': [5, 3077]}]}
        """
        for pon_port in uncfg_onu_dict.keys(): # для каждого пон порта ищем список зарегистрированных ону из конфига
            gpon_port = int(pon_port.split('/')[-1]) # pon_port - полный номер(1/1/2), gpon_port - номер порта на плате(2)
            #получаем конфиг пон порта в виде списка строк
            PON_PORT_CFG = ('show running-config interface gpon-olt_{}\n'.format(pon_port),)
#            with super().invoke_shell() as ssh:
#                ssh.send('terminal length 0\n')
#                ssh.send('show running-config interface gpon-olt_{}\n'.format(pon_port))
#                time.sleep(1)
#                run_cfg_raw = ssh.recv(5000).decode('utf-8')
            run_cfg_raw = send_commands(PON_PORT_CFG)
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
                    cvlan = CVLAN_START + (128 * (gpon_port - 1)) + free_onu_num
                    sn[value] = [free_onu_num]
                    sn[value].append(cvlan)
        return uncfg_onu_dict

    def generate_cfg_from_template(self, template, data):
        env = Environment(loader=FileSystemLoader('.'), trim_blocks=True)
        onu_template = env.get_template(template)
        onu_config = onu_template.render(data=data)
        return onu_config

    def register_onu(self, CVLAN_START, template):
        uncfg_onu_dict = self.get_uncfg_onu()
        if uncfg_onu_dict:
            reg_data = self.get_free_slots(uncfg_onu_dict, CVLAN_START)
            onu_config = self.generate_cfg_from_template(template, reg_data)
            with super().invoke_shell() as ssh:
                ssh.send('conf t\n')
                ssh.send(onu_config)
                time.sleep(5)
                result =  ssh.recv(5000).decode('utf-8')
            print(result)
        else:
            print('No uncfg onu')
        #pass  # FIXME

    def get_onu_information(self, onu):

        onu_info = {}
        re_ifindex = '(\d+/\d+/\d+:\d+)'
        re_state = 'Phase state:\s+(\w+)'
        re_uptime = 'Online Duration:\s+(\d.+)'
        re_offline = '2\d{3}-\d\d-\d\d\s\d\d:\d\d:\d\d'
        re_lan_status = 'Operate status:(\w+)'
        re_lan_speed = 'Speed status:\s+(\S.+)'
        re_rx = '\s(\-.+\(dbm\))'

        ONU_BY_SN = ('show gpon onu by sn {}'.format(onu),)

        ifindex_raw = self.send_commands(ONU_BY_SN)
        ifindex = re.search(re_ifindex, ifindex_raw).group()

        DETAIL_INFO = ('show gpon onu detail-info gpon-onu_{}'.format(ifindex),)
        LAN_STATE = ('show gpon remote-onu interface eth gpon-onu_{}'.format(ifindex),)
        ONU_RX = ('show pon power onu-rx gpon-onu_{}'.format(ifindex),)
        OLT_RX = ('show pon power olt-rx gpon-onu_{}'.format(ifindex),)

        detail_info = self.send_commands(DETAIL_INFO)
        lan_port = self.send_commands(LAN_STATE)
        onu_rx = self.send_commands(ONU_RX)
        olt_rx = self.send_commands(OLT_RX)

        onu_info['state'] = re.search(re_state, detail_info).groups()[0]
        if onu_info['state'] == 'working':
            onu_info['uptime'] = (re.search(re_uptime, detail_info).groups()[0]).strip()
            onu_info['lan_state'] = re.search(re_lan_status, lan_port).groups()[0]
            onu_info['lan_speed'] = (re.search(re_lan_speed, lan_port).groups()[0]).strip()
            onu_info['onu_rx'] = re.search(re_rx, onu_rx).groups()[0]
            onu_info['olt_rx'] = re.search(re_rx, olt_rx).groups()[0]
        else:
            onu_info['last_online'] = re.findall(re_offline, detail_info)[-1]
            onu_info['lan_state'] = 'N/A'
            onu_info['lan_speed'] = 'N/A'
            onu_info['onu_rx'] = 'N/A'
            onu_info['olt_rx'] = 'N/A'

        print(onu_info)
        #pass  # FIXME

    def get_mac_table(self):
        with super().invoke_shell() as ssh:
            ssh.send('show mac\n')
            time.sleep(1)
            result = ssh.recv(5000).decode('utf-8')
            print(result)        #pass  # FIXME


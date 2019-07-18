from Olt import Olt
import paramiko
import time
import re
from jinja2 import Environment, FileSystemLoader
from olt_logging import send_log
from paramiko import ssh_exception

class OltZTE(paramiko.SSHClient, Olt):

    SLOTS = set(range(1, 129))
    logger = send_log('test') # DEBUG, WARNING, INFO

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
            self.logger.info('''Connecting to %s''', self.host)
            super().set_missing_host_key_policy(paramiko.AutoAddPolicy())
            super().connect(self.host,
                            username=self.username,
                            password=self.password,
                            look_for_keys=False,
                            allow_agent=False)

            self.logger.info('''Access granted(%s)''', self.host)

            with super().invoke_shell() as ssh:
                ssh.send('terminal length 0\n')
                time.sleep(1)

        except paramiko.AuthenticationException:
            self.logger.critical('''Authentication error occured while connecting to %s''', self.host)
#            print("Authentication error occured.")

        except ssh_exception.NoValidConnectionsError:
            self.logger.critical('''Can`t connect to %s''', self.host)
#            print("Connection error occured.")

        # FIXME
        # logging

    def send_commands(self, commands, timeout=1):

        with super().invoke_shell() as ssh:
            if type(commands) == str:
                ssh.send('{}\n'.format(commands))
            elif type(commands) == list:
                for command in commands:
                    ssh.send('{}\n'.format(command))
            time.sleep(timeout)
            output = ssh.recv(5000).decode('utf-8')

            if 'Invalid input' in output:
                self.logger.warning('''Host %s:\nInvalid input detected while executing command "%s"'''
                , self.host, commands)
            else:
                self.logger.debug('''Host %s:\n%s''', self.host, output)

        return output

    def get_uncfg_onu(self):
        """Returns dict with PON ports as keys and uncfg ONUs' sn's lists as
        values: {pon_port1: [sn1, sn2, snN], ...}"""
        output = self.send_commands('show gpon onu uncfg')

        if 'No related' in output:
            uncfg_onu_list = False
            self.logger.info('''Host %s:\nNo unconfigured onus found.''', self.host)
        else:
            uncfg_onu_list = []
            re_uncfg_onu = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
            uncfg_onu_raw = re.finditer(re_uncfg_onu, output)

            for match in uncfg_onu_raw:
                port = match.group('PON_PORT')
                sn = match.group('SN')
                uncfg_onu_list.append([port, sn])
            self.logger.info('''Host %s:\nFound uncfg onus:\n%s''', self.host, uncfg_onu_list)

        return uncfg_onu_list

    def get_duplicate(self,uncfg_onu_list):
        regex = 'gpon-onu_(?P<PON_PORT>\d+/\d+/\d):(?P<LLID>\d+)'
        dup = []
        for onu in uncfg_onu_list:
            output = self.send_commands('show gpon onu by sn {}'.format(onu[1]))
            if 'gpon-onu_'in output:
                clear_out = re.finditer(regex, output)
                for match in clear_out:
                    port = match.group('PON_PORT')
                    llid = match.group('LLID')
                    dup.append([onu[1], port, llid])
                    self.logger.warning('''Host %s: Duplicate onu %s detected on gpon-olt_%s.'''
, self.host, onu[1], port)
        return dup

    def del_duplicate(self,dup):
        for onu in dup:
            remove_onu =  ['conf t','interface gpon-olt_{}'.format(onu[1]),'no onu {}'
.format(onu[2]),'end']
            self.send_commands(remove_onu)
            self.logger.warning('''Host %s: ONU %s was removed from PON port %s : %s.'''
, self.host, onu[0], onu[1], onu[2])

    def get_free_slots(self, pon_port):
        """
        input: pon_port like '1/1/2'
        output: set like {13, 14, 15}
        """
        pon_port_cmd = ('show running-config interface gpon-olt_{}\n'.format(pon_port))
        pon_port_cfg_raw = self.send_commands(pon_port_cmd)
        pon_port_cfg_raw = pon_port_cfg_raw.split('\n')
        cur_onu_list = []

        for line in pon_port_cfg_raw:
            if 'type' in line:
                cur_onu_list.append(line)
        cur_onu_nums = []

        for line in cur_onu_list:
            cur_onu_nums.append(int(line.split()[1]))
        cur_onu_nums = set(cur_onu_nums)
        free_slots = self.SLOTS - cur_onu_nums
        if free_slots:
            self.logger.info('''Host %s: %s onu slots available on gpon-olt_%s.''', self.host, len(free_slots), pon_port)
            pass
        else:
            self.logger.warning('''Host %s: No free slots available on gpon-olt_%s.''', self.host, pon_port)

        return free_slots

    def get_data(self, onu_list, cvlan_start):
        '''return list of lists like [['1/1/2', zte1, 24, 1025], ... ] '''
        free_slots = {}
        data = []
        onu_to_reg = []

        for onu in onu_list:
            pon_port, sn = onu

            if not pon_port in free_slots.keys():
                free_slots[pon_port] = self.get_free_slots(pon_port)

            if free_slots[pon_port]:

                if not len(free_slots[pon_port]) == 0:
                    free_slot = free_slots[pon_port].pop()
                    cvlan = cvlan_start + (128 * (int(pon_port.split('/')[-1]) - 1)) + free_slot
                    data.append([pon_port, sn, free_slot, cvlan])
                    onu_to_reg.append(sn)
                else:
                    self.logger.warning('''Host %s: No free slot for onu %s on gpon-olt_%s.''', self.host, sn, pon_port)
        self.logger.info('''Host %s: Onues: %s will be registered.''', self.host, onu_to_reg)
        return data

    def generate_cfg_from_template(self, template, data):
        env = Environment(loader=FileSystemLoader('.'), trim_blocks=True)
        onu_template = env.get_template(template)
        onu_config = onu_template.render(data=data)
        self.logger.debug('''Host %s:\n%s''', self.host, onu_config)

        return onu_config


    def register_onu(self, onu_config):
        self.send_commands('conf t')
        time.sleep(1)
        for line in onu_config.split('\n'):
            self.send_commands(line)
            time.sleep(1)
#        self.send_commands(onu_config)


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


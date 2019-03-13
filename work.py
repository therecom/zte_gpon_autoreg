import paramiko
import time



class Olt:

    def __init__(self, username, password, hostname):
        print('Подключаюсь к {}'.format(hostname))
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=hostname, username=username, password=password,
                         look_for_keys=False, allow_agent=False)

    def ShowVlan(self):
        with self.ssh.invoke_shell() as con:
            con.send('show vlan summ\n')
            time.sleep()
            result = con.recv(5000).decode('utf-8')
            print(result)

    def GetUncfgOnu(self):
        '''
        input:  подключение к olt
        output: False/Словарь
        '''
        with self.ssh.invoke_shell() as con:
            con.send('terminal length 0\n')
            con.send('show gp on u\n')
            time.sleep(1)
            output = con.recv(5000).decode('utf-8')
            if 'No related' in output:
                uncfg_onu_dict = False
            else:
                regex1 = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
                uncfg_onu_dict = {}
                uncfg_onu_raw = re.finditer(regex1, output)
                for match in uncfg_onu_raw:
                    port = match.group('PON_PORT')
                    sn = match.group('SN')
                    if uncfg_onu_dict.get(port) == None:
                        uncfg_onu_dict[port] = [{sn:[]}]
                    else:
                        uncfg_onu_dict[port].append({sn:[]})
            return uncfg_onu_dict


#        olt_ssh.sendline('sho gp on u')
#        olt_ssh.expect('#')
#        show_output = olt_ssh.before.decode('utf-8')
#        if 'No related' in show_output:
#            uncfg_onu_dict = False
#        else:
#            regex1 = 'u_(?P<PON_PORT>\S+):\d\s+(?P<SN>\S+)'
#            uncfg_onu_dict = {}
#            uncfg_onu__raw = re.finditer(regex1, show_output)
#            for match in uncfg_onu__raw:
#                port = match.group('PON_PORT')
#                sn = match.group('SN')
#                if uncfg_onu_dict.get(port) == None:
#                    uncfg_onu_dict[port] = [{sn:[]}]
#                else:
#                    uncfg_onu_dict[port].append({sn:[]})
#        return uncfg_onu_dict









    def onu_reg(self):
        with self.ssh.invoke_shell() as connection:
            connection.send('''ping 10.133.201.21
conf t
interface gpon-olt_1/1/1
onu 6 type GPON sn HWTC10AE5A9B
onu 6 profile  line line-gpon remote CVLAN_2
exit
pon-onu-mng gpon-onu_1/1/1:6
loop-detect ethuni eth_0/1 enable
exit
interface gpon-onu_1/1/1:6
  switchport mode trunk vport 1
  switchport vlan 296  tag vport 1
  port-location format ti vport 1
  dhcp-option82 enable vport 1
  ip dhcp snooping enable vport 1
exit
exit''')
            time.sleep(1)
            result = connection.recv(5000).decode('utf-8')
            print(result)


con = Olt(username,password,hostname)


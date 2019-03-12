from test import Olt


device_dict = {'username': 'backup', 'password': 'Backup-Gfhjkm'}

import paramiko
import time

username = 'backup'
password = 'Backup-Gfhjkm'
hostname = '10.133.248.41'


class Olt:

    def __init__(self, username, password, hostname):
        print('Подключаюсь к {}'.format(hostname))
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=hostname, username=username, password=password,
                         look_for_keys=False, allow_agent=False)

    def show_vlan(self):
        with self.ssh.invoke_shell() as connection:
            connection.send('show vlan summ\n')
            time.sleep(1)
            result = connection.recv(5000).decode('utf-8')
            print(result)


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

'''
ping 10.133.201.21
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
exit'''




con = Olt(username,password,hostname)

IP = '10.133.248.41'
USER = 'backup'
PASSWORD = 'Backup-Gfhjkm'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=IP, username=USER, password=PASSWORD,
                   look_for_keys=False, allow_agent=False)



with client.invoke_shell() as ssh:
    ssh.send('show vlan summ\n')
    time.sleep(1)
    result = ssh.recv(5000).decode('utf-8')
    print(result)

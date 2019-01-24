#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import paramiko
import time

def connect(user,host,dev_pass):
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(username=user, hostname=host, password=dev_pass, look_for_keys=False, allow_agent=False)
    with connection.invoke_shell() as ssh:
        ssh.send('terminal length 0\n')
        time.sleep(1)
        ssh.recv(100).decode('utf-8')
    return connection

def send_command(connection, command):
    with connection.invoke_shell() as ssh:
        ssh.send('{}\n'.format(command))
        time.sleep(1)
        result = ssh.recv(5000).decode('utf-8')
        print(result)
#    return(result)

def close_ssh_connection(connection):
    connection.close()


test_command = 'show running-config interface gpon-onu_1/1/1:4'

HOSTNAME = '1.1.1.1'
USER = 'test'
PASS = 'test_pass'


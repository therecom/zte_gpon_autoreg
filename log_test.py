import paramiko
import time
import logging
import os


logger = logging.getLogger('olt_connect')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logfile = logging.FileHandler('logfile_test1.log')
logfile.setLevel(logging.INFO)

formatter_console = logging.Formatter('{asctime} - {name} - {levelname} - {message}',
                              datefmt='%H:%M:%S', style='{')

formatter_logfile = logging.Formatter('{asctime} - {name} - {levelname}: {message}',
                              datefmt='%H:%M:%S', style='{')


console.setFormatter(formatter_console)
logger.addHandler(console)

logfile.setFormatter(formatter_logfile)
logger.addHandler(logfile)


name = 'backup'
password = 'Backup-Gfhjkm'
host = '10.133.248.43'

def olt_con(name,password, host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,username=name,password=password,
                    look_for_keys=False,
                    allow_agent=False)

    return client


def send_command(command):
    with client.invoke_shell() as ssh:
        ssh.send('{}\n'.format(command))
        time.sleep(1)
        out = ssh.recv(5000).decode('utf-8')

    logger.debug('\n\n{}'.format(out))
    if 'Invalid input' in out:
        logger.info('\n\n{}'.format(out))

client = olt_con(name,password, host)

send_command('show ip interf br')




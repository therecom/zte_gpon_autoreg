from paramiko import SSHClient
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import BadHostKeyException

"""Main module"""


class Device:
    pass


class Olt(SSHClient, Device):

    def __init__(self, host, username='', password=''):
        self.host = host
        self.username = username
        self.password = password
        super().__init__()

    def connect(self):
        """Tries to make ssh connection. Log if errors occurs """

        try:
            super().connect(self.host,
                            username=self.username,
                            password=self.password)

        except AuthenticationException:
            print("Authentication error occured.")

        except SSHException:
            print("Connection error occured.")

        except BadHostKeyException:
            print("Host key error occured.")

        # FIXME
        # logging


class OltBDCOM(Olt):
    pass


class OltZTE(Olt):

    SLOTS = set(range(1, 129))

    def run_command(self, command):
        pass

    def run_commands(self, commands):
        pass

    def get_uncfg_onu(self):
        """Returns dict with PON ports as keys and uncfg ONUs' sn's lists as
        values: {pon_port1: [sn1, sn2, snN], ...}"""
        pass  # FIXME

    def get_free_slots(self):
        """Returns dict with PON ports as keys and sorted lists of free
        slots as values"""
        # pon_ports = keys(self.uncfg_onu)
        pass  # FIXME

    def register_onu(self):
        # onu_list = self.get_uncfg_onu()
        # free_slots = self.get_free_slots()
        pass  # FIXME

    def get_onu_information(self, onu):
        pass  # FIXME

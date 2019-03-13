from abc import ABC, abstractmethod
import paramiko
"""Main module"""


class Device:
    pass


class Olt(ABC, Device):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_uncfg_onu(self):
        pass

    @abstractmethod
    def get_free_slots(self):
        pass

    @abstractmethod
    def register_onu(self):
        pass

    @abstractmethod
    def get_onu_information(self, onu):
        pass


class OltBDCOM:
    pass


class OltZTE(paramiko.SSHClient, Olt):

    SLOTS = set(range(1, 129))

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

        except paramiko.AuthenticationException:
            print("Authentication error occured.")

        except paramiko.SSHException:
            print("Connection error occured.")

        # FIXME: there is not such exception
        except paramiko.TimeoutError:
            print("Timeout error occured.")

        # FIXME
        # logging

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

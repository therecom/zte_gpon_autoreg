from abc import ABC, abstractmethod
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

    @abstractmethod
    def get_mac_table(self):
        pass

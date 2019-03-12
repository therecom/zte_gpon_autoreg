"""Main module"""
# import logging
import paramiko


class Olt(paramiko.SSHClient):

    SLOTS = set(range(1, 129))

    def __init__(self, host, **kwargs):
        self.username = username#kwargs['username']
        self.password = password#kwargs['password']
        self.host = host
        super().__init__()

    def connect(self):
        """Tries to make ssh connection. Log if errors occurs """
        try:
            super().connect(self.host, username=self.username,
                            password=self.password)
        except paramiko.AuthentificationException:
            print("Authentification error occured.")
        except paramiko.SSHException:
            print("Connection error occuredi.")

        pass  # TODO

    def get_uncfg_onu(self):
        """Returns dict with PON ports as keys and uncfg ONUs' sn's lists as
        values: {pon_port1: [sn1, sn2, snN], ...}"""
        pass  # TODO

    def get_free_slots(self):
        """Returns dict with PON ports as keys and sorted lists of free
        slots as values"""
        # pon_ports = keys(self.uncfg_onu)
        pass  # TODO

    def register_onu(self):
        # onu_list = self.get_uncfg_onu()
        # free_slots = self.get_free_slots()

        # FIXME

        self.close()
        pass


def main():
    pass


if __name__ == "__main__":
    main()

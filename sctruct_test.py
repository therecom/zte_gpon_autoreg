"""Main module"""


class Olt:

    SLOTS = set(range(1, 129))

    def __init__(self, auth_params):
        self.connection = None
        self.uncfg_onu = None
        self.free_slots = None

    def connect(self):
        """Tries to make ssh connection. Returns self.connection in case of
        success """
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


def main():
    pass


if __name__ == "__main__":
    main()

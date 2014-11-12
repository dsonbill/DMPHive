from HiveLib import HiveLoop, HiveRPC

__author__ = 'William C. Donaldson'


class StateControl():

    @staticmethod
    def shutdown():
        HiveLoop.MAIN_LOOP.stop()
        return 'foobar' # Return value will not make it, on account of the loop stopping.
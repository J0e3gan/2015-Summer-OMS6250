#!/usr/bin/python

" Assignment 2 - static-forwarding.py - \
    First part of the assignment. This is to create a static-forwarding table."


from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import packets
from helpers import *


class StaticSwitch(Policy):
    def __init__(self):
        """ 
        Initialization of static switch. Set up your forwarding tables  here.
        You need to key off of Switch and MAC address to determine forwarding
        port.
        Suggested routes: 
          - Array with switch as index, dictionary for MAC to switch port
          - dictionary of dictionaries
        """

        # Initialize the parent class
        super(StaticSwitch, self).__init__()

        # TODO: set up forwarding tables. Create this however you wish. As
        # a suggestion, using a list of tuples will work.
        self.forwarding_table = [
            {'00:00:00:00:00:01': 1, '00:00:00:00:00:02': 2, '00:00:00:00:00:03': 3, '00:00:00:00:00:04': 3},  # sA
            {'00:00:00:00:00:01': 3, '00:00:00:00:00:02': 3, '00:00:00:00:00:03': 1, '00:00:00:00:00:04': 2}   # sB
        ]

        open_log('static-forwarding.log')
        i = 1
        for switch_mappings in self.forwarding_table:
            for mac_address, port_number in switch_mappings.iteritems():
                write_forwarding_entry(i, port_number, mac_address)
            i += 1
        finish_log()


    def build_policy(self):
        """ 
        This creates the pyretic policy. You'll need to base this on how you 
        created your forwarding tables. You need to compose the policies 
        in parallel. 
        """

        # TODO: Rework below based on how you created your forwarding tables.
        
        subpolicies = []

        i = 1
        for switch_mappings in self.forwarding_table:
            for mac_address, port_number in switch_mappings.iteritems():
                subpolicies.append(match(switch=i, dstmac=mac_address) >> fwd(port_number))
            subpolicies.append(match(switch=i, dstmac='ff:ff:ff:ff:ff:ff') >> parallel(
                [xfwd(port_number) for port_number in switch_mappings.values()]))
            i += 1
        #subpolicies.append(match(switch=1, dstmac="00:00:00:00:00:01") >> fwd(3))
        #subpolicies.append(match(switch=1, dstmac="00:00:00:00:00:02") >> fwd(2))
        # NOTE: this will flood for MAC broadcasts (to ff:ff:ff:ff:ff:ff).
        # You will need to include something like this in order for ARPs to 
        # propogate. xfwd() is like fwd(), but will not forward out a port a
        # packet came in on. Useful in this case.
        #subpolicies.append(match(switch=1, dstmac="ff:ff:ff:ff:ff:ff") >> parallel([xfwd(1), xfwd(2), xfwd(3)]))
        #subpolicies.append(match(switch=2, dstmac="ff:ff:ff:ff:ff:ff") >> parallel([xfwd(1), xfwd(2), xfwd(3)]))

        # This returns a parallel composition of all the subpolicies you put
        # together above.
        return parallel(subpolicies)

        
def main():
    return StaticSwitch().build_policy()

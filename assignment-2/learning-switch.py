#!/usr/bin/python

"Assignment 4 - This is the controller code that students will have to \
    implement sections of. It is Pyretic based, but this is somewhat\
    unimportant at the moment, as we only care about the learning\
    behaviors."

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import packets
from helpers import *


class LearningSwitch(DynamicPolicy):
    def __init__(self):
        """ Initialization of the Learning Switch. The important piece
            is the definition of the switch mapping. This is a nested
            dictionary. """

        # Initialize the parent class
        super(LearningSwitch, self).__init__()

        # TODO: Initialize your forwarding tables. Create this however you wish.
        # Couple of suggestions: Dictionary of dictionaries, Dictionary of 
        # tuples.
        self.forwarding_table = {}  # empty dictionary to be a dict of dicts as routes are learned

        open_log('learning-switch.log')


        # only use one flood instance - this is the default policy when there 
        # isn't a known path.
        self.flood = flood()

        # Get the first packet from each new MAC address on a switch. This
        # is how we are able to learn new routes.
        new_pkts = packets(1, ['srcmac', 'switch'])
        new_pkts.register_callback(self.learn_route)
        self.query = new_pkts

        # Initialize the policy
        self.build_policy() 


    def print_switch_tables(self):
        # TODO - You will need to implement this based on how your forwarding
        # table are set up. Us the functions in the first half of helpers.
        # Format should be to call write_forwarding_entry() for each entry in
        # the forwarding table, then finish up with finish_printing().
        for switch, switch_mappings in self.forwarding_table.iteritems():
            for mac_address, port_number in switch_mappings.iteritems():
                write_forwarding_entry(switch, port_number, str(mac_address))

        next_entry()

        import helpers
        helpers.logfile.flush()

        pass


    def learn_route(self, pkt):
        """  This function adds new routes into the fowarding table. """

        # TODO - create a new entry in the fowarding table. Use the functions 
        # in the second half of helpers to simplify all your work.
        pkt_src_mac = get_src_mac(pkt)
        #print('pkt_src_mac == ' + str(pkt_src_mac))  # FORNOW
        if str(pkt_src_mac)[:-2] != '00:00:00:00:00:':  # only host-sent packets
            return

        pkt_dst_mac = get_dst_mac(pkt)
        pkt_switch = get_switch(pkt)
        pkt_inport = get_inport(pkt)
        #pkt_outport = get_outport(pkt)
        #print('pkt_dst_mac == ' + str(pkt_dst_mac))  # FORNOW
        #print('pkt_switch == ' + str(pkt_switch))    # FORNOW
        #print('pkt_inport == ' + str(pkt_inport))    # FORNOW
        #print('pkt_outport == ' + str(pkt_outport))  # FORNOW
        if not(pkt_switch in self.forwarding_table.keys()):
            self.forwarding_table[pkt_switch] = {pkt_src_mac: pkt_inport}
        elif not(pkt_src_mac in self.forwarding_table[pkt_switch].keys()):
            self.forwarding_table[pkt_switch][pkt_src_mac] = pkt_inport

        # print out the switch tables:
        self.print_switch_tables()

        # Call build_policy to update the fowarding tables of the switches.
        #self.build_policy()  # FORNOW

        pass


    def build_policy(self):
        """ 
        This is similar to the build_policy() function in StaticSwitch. 
        There is a major difference: If there isn't a rule, you need to flood
        the packets. The example code should help.
        """
        new_policy = None
        not_flood_pkts = None
        

        # TODO: Example code. You will need to edit this based on how you're 
        # storing your policies. You should only have to replace the details in
        # rule entries.
        for switch, switch_mappings in self.forwarding_table.iteritems():
            for mac_address, port_number in switch_mappings.iteritems():
                if new_policy == None:
                    # First entry, prime the pump
                    new_policy = (match(switch=int(switch), dstmac=(mac_address)) >>
                                  fwd(port_number))
                else:
                    new_policy += (match(switch=int(switch), dstmac=(mac_address)) >>
                                   fwd(port_number))
                if not_flood_pkts == None:
                    not_flood_pkts = (match(switch=int(switch), dstmac=(mac_address)))
                else:
                    not_flood_pkts |= (match(switch=int(switch), dstmac=(mac_address)))
        #rule1 = 1, "00:00:00:00:00:01", 3
        #rule2 = 1, "00:00:00:00:00:02", 2
        #for rule in (rule1, rule2):
        #    if new_policy == None:
        #        # First entry, prime the pump
        #        new_policy = (match(switch=int(rule[0]), dstmac=(rule[1])) >>
        #                      fwd(rule[2]))
        #    else:
        #        new_policy += (match(switch=int(rule[0]), dstmac=(rule[1])) >>
        #                       fwd(rule[2]))
        #    if not_flood_pkts == None:
        #        not_flood_pkts = (match(switch=int(rule[0]), dstmac=(rule[1])))
        #    else:
        #        not_flood_pkts |= (match(switch=int(rule[0]), dstmac=(rule[1])))
                        
                

        # If you follow the pattern above, you won't have to change this below. 
        # We don't know of any rules yet, so flood everything.
        if not_flood_pkts == None:
            self.policy = self.flood + self.query
        else:
            self.policy = if_(not_flood_pkts, new_policy, self.flood) + self.query
        
        # The following line can be uncommented to see your policy being
        # built up, say during a flood period. 
        # print self.policy  # FORNOW: Print the policy presently in place.


    def __del__(self):
        finish_log()


def main():
    return LearningSwitch()

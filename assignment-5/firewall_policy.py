#!/usr/bin/python

"Assignment 5 - This creates the firewall policy. "

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import packets
from pyretic.core.packet import IPV4, TCP_PROTO

def make_firewall_policy(config):
    # TODO - This is where you need to write the functionality to create the
    # firewall. What is passed in is a list of rules that you must implement
    # using the Pyretic syntax that was used in Assignment 2. 

    # feel free to remove the following "print config" line once you no longer need it
    print config # for demonstration purposes only, so you can see the format of the config

    rules = []
    for entry in config:
        # TODO - build the individual rules
        filtered_entry = dict(
            (k, v if k != "srcport" and k != "dstport" else int(v)) for k, v in entry.iteritems() if v != '*')
        rule = match(ethtype=IPV4, protocol=TCP_PROTO, **filtered_entry)

        ## examples:
        #rule = match(dstport=entry['dstport'])
        #rule = match(srcmac=MAC(entry['srcmac']))
        #rule = match(srcip=entry['srcip'])
        #rule = match(dstmac=MAC(entry['dstmac']), srcport=entry['srcport'])
        rules.append(rule)
        pass
    
    allowed = ~(union(rules))

    return allowed

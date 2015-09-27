#!/usr/bin/python
import dateutil.parser
from datetime import datetime
from dateutil.relativedelta import *
import os
import trolly

import pdb

#Trello API_KEY, trello TOKEN
client = trolly.client.Client(os.environ['API_KEY'], os.environ['TOKEN'])
openstack_ci = [board for board in client.get_boards() if board.name == "openstack-ci"][0]

#get the current time
now = datetime.utcnow()

cards = openstack_ci.get_cards()

cards_in_progress = []
[cards_in_progress.append(card) for card in cards if card.get_list().name == "In Progress"]

print 'There are %s cards in progress' % len(cards_in_progress)
for card in cards_in_progress:
    id = card.id
    hex_date = (int(id[0:8],16))
    created_on_human = unicode(datetime.fromtimestamp(hex_date))
    #created_on = datetime.strptime(created_on_human, '%Y-%m-%d %H:%M:%S')
    created_on = dateutil.parser.parse(created_on_human)
    delta = relativedelta(now, created_on)
    #pdb.set_trace()
    members = card.get_members()
    if len(members) > 1:
       member_list = []
       for member in members:
           #pdb.set_trace()
           member_list.append(member.name)
    else:
        member_list = members[0].name
    if delta.months > 0:
        print '%s is marked in progress but is %s months old. Owner(s) are %s ' % (card.name, delta.months, str(member_list))



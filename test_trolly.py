#!/usr/bin/python

from datetime import datetime
import os
import trolly

#Trello API_KEY, trello TOKEN
client = trolly.client.Client(os.environ['API_KEY'], os.environ['TOKEN'])
openstack_ci = [board for board in client.get_boards() if board.name == "openstack-ci"][0]

cards = openstack_ci.get_cards()

cards_in_progress = []
[cards_in_progress.append(card) for card in cards if card.get_list().name == "In Progress"]

print 'There are %s cards in progress' % len(cards_in_progress)
for card in cards_in_progress:
    id = card.id
    created_on = datetime.fromtimestamp(int(id[0:8],16))
    print '%s was created on %s' %(card.name, created_on)
#print(cards)


#Update rdopkg workflow [src_gate]

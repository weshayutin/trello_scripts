#!/usr/bin/python

import ast
import dateutil.parser
from datetime import datetime
from dateutil.relativedelta import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import os
import smtplib
import trolly

import pdb

#get team members
team = ast.literal_eval(os.environ['TEAM'])
email_server = smtplib.SMTP('smtp.corp.redhat.com', 25)

#Trello API_KEY, trello TOKEN
client = trolly.client.Client(os.environ['API_KEY'], os.environ['TOKEN'])
openstack_ci = [board for board in client.get_boards() if board.name == "openstack-ci"][0]

#get the current time
now = datetime.utcnow()

cards = openstack_ci.get_cards()

cards_in_progress = []
[cards_in_progress.append(card) for card in cards if card.get_list().name == "In Progress"]

print 'There are %s cards in progress' % len(cards_in_progress)

#create a dict, key = member name and list for values
msg_dict = {}
for key in team.iterkeys():
    msg_dict[key] = []

for card in cards_in_progress:
    id = card.id
    #Determine the creation date of the card
    hex_date = (int(id[0:8],16))
    created_on_human = unicode(datetime.fromtimestamp(hex_date))
    created_on = dateutil.parser.parse(created_on_human)
    delta = relativedelta(now, created_on)
    members = card.get_members()
    if len(members) > 1:
       member_list = []
       for member in members:
           if team.has_key(member.name):
               member_list.append(member.name)
       member_list_str = (", ".join(member_list))
    else:
        member_list_str = members[0].name
    #convert member_list_str back into a list
    member_list = member_list_str.split(",")

    if delta.months > 0:
        msg = 'CARD URL: %s\nNAME: %s\n Card is marked in progress but is %s months old.\n Owner(s) are %s\n ' % (card.get_card_information()['url'], card.name, delta.months, member_list_str)
        for member in member_list:
            msg_dict[str(member).strip()].append(msg)
    if delta.months == 0 and delta.days > 7:
        msg = 'CARD URL: %s\nNAME: %s\n Card is marked in progress but is %s days old.\n Owner(s) are %s\n ' % (card.get_card_information()['url'], card.name, delta.days, member_list_str)
        for member in member_list:
            msg_dict[str(member).strip()].append(msg)

email_list = ast.literal_eval(os.environ['TEAM_TO_EMAIL'])
email_server.starttls()

#email each owner w/ a list of cards that require attention
for name, msg in msg_dict.iteritems():
    if name in email_list:
      email_from = "whayutin@redhat.com"
      email_to = email_list[name]
      email = MIMEMultipart()
      email['From'] = email_from
      email['To'] = email_to
      email['Subject'] = "[trello report] Trello cards need attention"
      body = '\n\n'.join(msg)
      email.attach(MIMEText(body,'plain'))
      text = email.as_string()
      email_server.sendmail(email_from, email_to, text)

#email report
all_msg = ""
for name, msg in msg_dict.iteritems():
      #print(name, msg)
      all_msg += 'There are %s cards in progress' % len(cards_in_progress)
      all_msg += '\n\n'
      all_msg += '\n'.join(msg)

email_from = "whayutin@redhat.com"
email_to = "whayutin@redhat.com"
email = MIMEMultipart()
email['From'] = email_from
email['To'] = email_to
email['Subject'] = "[trello rollup report] Trello cards need attention"
#body = '\n\n'.join(all_msg)
body = all_msg
email.attach(MIMEText(body,'plain'))
text = email.as_string()
email_server.sendmail(email_from, email_to, text)

email_server.quit()


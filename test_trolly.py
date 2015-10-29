#!/usr/bin/python3

import ast
import dateutil.parser
from datetime import datetime
from dateutil.relativedelta import *
from email.mime.text import MIMEText
import os
import pprint
import pytz
import smtplib
import trolly

import pdb

#Global variables
now = datetime.now(pytz.utc)
msg_dict = {}
cards_in_progress = []

#get team members
team = ast.literal_eval(os.environ['TEAM'])
email_server = smtplib.SMTP('smtp.corp.redhat.com', 25)

#Trello API_KEY, trello TOKEN
client = trolly.client.Client(os.environ['API_KEY'], os.environ['TOKEN'])
openstack_ci = [board for board in client.get_boards() if board.name == "openstack-ci"][0]

def get_list(list_name):
    for this_list in openstack_ci.get_lists():
      if this_list.name == list_name:
        return this_list

def email_send(email_from, email_to, subject, body):
    email = MIMEText(str(body))
    email['From'] = email_from
    email['To'] = email_to
    email['Subject'] = subject
    email_server.send_message(email)

def generate_report_body():
    for card in cards_in_progress:
      id = card.id
      #Determine the creation date of the card
      hex_date = (int(id[0:8],16))
      created_on_human = str(datetime.fromtimestamp(hex_date))
      created_on = dateutil.parser.parse(created_on_human).replace(tzinfo = pytz.utc)
      card_age = relativedelta(now, created_on)

      #set a due date (1 week), if none set
      if card.get_card_information()['due']:
        print("due date already set")
      else:
        in_one_week = now+relativedelta(weeks=+1)
        in_one_week = in_one_week.strftime('%Y-%m-%dT%H:%M:%S')
        card.update_card({'due':in_one_week})
      due = dateutil.parser.parse(card.get_card_information()['due'])
      delta = relativedelta(now, due)

      #only generate date on team members
      members = card.get_members()
      if len(members) > 0:
        member_list = []
        for member in members:
          if member.name in team:
            member_list.append(member.name)
      else:
        break # no members found
      #convert member_list_str back into a list
      member_list_str = (", ".join(member_list))

      # If card is past it's due date
      if delta.days > 0:
        msg = 'CARD URL: %s\nNAME: %s\n \
              Card is overdue by %s months %s days.\n \
              Card is %s months %s days old.\n \
              Owner(s) are %s\n  \
              Last updated on %s\n ' \
              % (card.get_card_information()['shortUrl'],\
                 card.name,\
                 delta.months,\
                 delta.days,\
                 card_age.months,\
                 card_age.days,\
                 member_list_str,\
                 dateutil.parser.parse(card.get_card_information()['dateLastActivity']).strftime('%Y-%m-%d %H:%M:%S')
                 )
        for member in member_list:
          msg_dict[str(member).strip()].append(msg)

      # If user has set the due date greater than 1 week
      if delta.days < -7 or delta.months < 0:
        msg = 'CARD URL: %s\nNAME: %s\n \
              Card due date is greater than 7 days\n \
              Card is %s months %s days old.\n \
              Owner(s) are %s\n ' \
              % (card.get_card_information()['shortUrl'],\
                 card.name,\
                 card_age.months,\
                 card_age.days,\
                 member_list_str)
        for member in member_list:
          msg_dict[str(member).strip()].append(msg)

def generate_stats(column):
  stats = {}
  for member in team.keys():
    stats[member] = 0
  column_list = []
  this_list = get_list(column)
  [column_list.append(card) for card in this_list.get_cards()]
  for card in column_list:
    members = card.get_members()
    for member in members:
      if member.name in team: stats[member.name] += 1
  return stats

def nothing_in_progress():
  nada = []
  in_progress = generate_stats("In Progress")
  for key, value in in_progress.items():
    if value == 0:
      nada.append(key)
  return nada

def generate_report():
  # get card list
  this_list = get_list('In Progress')
  [cards_in_progress.append(card) for card in this_list.get_cards()]

  #create a dict, key = member name and list for values
  for key in team.keys():
    msg_dict[key] = []

  #Generate Report
  generate_report_body()

#MAIN

#Generate Report
generate_report()

#EMAIL SECTION
email_list = ast.literal_eval(os.environ['TEAM_TO_EMAIL'])
email_server.starttls()

#email each owner w/ a list of cards that require attention

for name, msg in msg_dict.items():
  if name in email_list and msg:
    intro_msg = os.environ['TEAM_INTRO_MSG']
    msg = intro_msg + '\n\n' + '\n\n'.join(msg)
    email_send(os.environ['REPORT_OWNER'], email_list[name], "[trello report] Trello cards that need attention", msg)

#email report
report_intro_msg = os.environ['REPORT_INTRO_MSG']
all_msg = ""
all_msg += report_intro_msg + '\n\n'
all_msg += 'There are %s cards in progress\n\n' % len(cards_in_progress)
all_msg += 'cards in complete:\n %s\n\n' % generate_stats("Complete")
all_msg += 'cards in next:\n %s\n\n' % generate_stats("Next")
all_msg += 'cards in progress:\n %s\n\n' % generate_stats("In Progress")

for name, msg in msg_dict.items():
  if msg:
    all_msg += '\n'
    all_msg += '\n'.join(msg)

email_send(os.environ['REPORT_OWNER'], os.environ['REPORT_LIST'], "[trello rollup report] Trello cards that need attention", all_msg)

#email team members w/ nothing in progress
nada = nothing_in_progress()
for name in nada:
  if name in email_list:
    all_msg = '%s, you are not a member of any cards marked in progress in trello.  Please pick up a card and begin work' % name
    email_send(os.environ['REPORT_OWNER'], team[name], "[trello report] no cards found in progress", all_msg)

#shutdown the connection to smtp/email
email_server.quit()


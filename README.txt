README

This tool uses https://github.com/plish/Trolly

Requirements:
git clone https://github.com/plish/Trolly
git clone https://github.com/weshayutin/trello_scripts.git

Get your trello api key from:
https://trello.com/app-key

Obtain a token from trello, (WHEN_TO_EXPIRE defaults to one day)
python authorise.py -a API_KEY APPLICATION_NAME WHEN_TO_EXPIRE

Cut and paste the API_KEY and TOKEN into the trello_scripts/auth file
Fill out your team members and email in the trello_scripts/team file


Install:
git clone https://github.com/plish/Trolly
git clone https://github.com/weshayutin/trello_scripts.git

yum install python-httplib2 python-dateutil

cd Trolly
python setup.py install


Execute:
source auth
source team
./test_trolly.py





# XMPPchat
<b>Rodrigo Alvarado - 16106</b>

XMPP chat implementation for [CC037 REDES]

## Installation
```bash
git clone https://github.com/alv16106/XMPPchat
pip install -r requirements.txt
```
then you can run the proyect by simply using main.py with or without arguments
```bash
python main.py -j [jid] -p [password] -n [nick]
```
* <b>jid</b> is your identifier in the server, make sure to add the domain <i>ex. chatter@genericserver.xyz</i>.
* <b>password</b> is the password for your user in the server.
* <b>nick</b> is your nickname, used for chat rooms.

In case you are not registered in the server, the client will try to register you with the given password. If it can't, get in contact with your server's manager

## Characteristics
This is a simple XMPP cliente writen in python to demonstrate the use of the XMPP standard. For the managing of such standard, the proyect uses [Slixmpp](https://slixmpp.readthedocs.io/ "Slixmpp documentation"). As for the interface, this proyect uses [Blessed](https://pypi.org/project/blessed/ "Blessed page"), a dialed down version of <b>ncurses</b>.

## Functionalities
The client can manage the commands listed below
```python
{
  '/dc': 'Disconect',
  '/list': 'List users',
  '/add': 'Add user to contacts - /add [contact]',
  '/peek': 'See details for user /peek [contact]',
  '/jr': 'Join Room - /jr [room]',
  '/lr': 'Leave Room - /lr [message](optional)',
  '/cpm': 'Change presence message - /cpm [new-message]',
  '/sf': 'Send File - /sf [path-to-file]',
  '/rm': 'Remove account from server',
  '/h': 'Help, shows this menu again'
}
```

Note that all commands start with a '/ ', when a line starts with '/ ' but no command is matched, the cliente will show an error and do nothing untill you input a valid command

When no command is issued, the client will attempt to send a message to the latest person you talked to or the group you are in.
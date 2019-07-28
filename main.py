from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
import logging
from getpass import getpass
from argparse import ArgumentParser

class TestClient(ClientXMPP):

  def __init__(self, jid, password, nick):
    ClientXMPP.__init__(self, jid, password)
    self.add_event_handler("session_start", self.session_start)
    self.room = 'alumnos'
    self.nick = nick
    self.add_event_handler("message", self.message)
    self.add_event_handler("register", self.register)

  def session_start(self, event):
    print('start')
    self.send_presence()
    self.get_roster()
  
  def message(self, msg):
    print('memencho')
    print(msg)
    if msg['type'] in ('chat', 'normal'):
      msg.reply("Thanks for sending\n%(body)s" % msg).send()

  def muc_message(self, msg):
    if msg['mucnick'] != self.nick and self.nick in msg['body']:
      self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')
  
  def muc_online(self, presence):
    if presence['muc']['nick'] != self.nick:
      self.send_message(mto=presence['from'].bare,
        mbody="Hello, %s %s" % (presence['muc']['role'], presence['muc']['nick']), 
        mtype='groupchat')

  async def register(self, iq):
    resp = self.Iq()
    resp['type'] = 'set'
    resp['register']['username'] = self.boundjid.user
    resp['register']['password'] = self.password
    try:
      await resp.send()
      logging.info("Account created for %s!" % self.boundjid)
    except IqError as e:
      logging.error("Could not register account: %s" %e.iq['error']['text'])
      self.disconnect()
    except IqTimeout:
      logging.error("No response from server.")
      self.disconnect()


if __name__ == '__main__':
  parser = ArgumentParser()
  xmpp = TestClient('amiguito@alumchat.xyz', 'yeah_boi', 'amiguito')
  xmpp.register_plugin('xep_0030') # Service Discovery
  xmpp.register_plugin('xep_0004') # Data forms
  xmpp.register_plugin('xep_0066') # Out-of-band Data
  xmpp.register_plugin('xep_0077') # In-band Registration
  xmpp['xep_0077'].force_registration = True
  parser.add_argument("-j", "--jid", dest="jid", help="JID to use")
  parser.add_argument("-p", "--password", dest="password", help="password to use")

  args = parser.parse_args()

  # Setup logging.
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

  if args.jid is None:
    args.jid = input("Username: ")
  if args.password is None:
    args.password = getpass("Password: ")

  xmpp.connect()
  xmpp.process()

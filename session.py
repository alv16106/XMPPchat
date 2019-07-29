from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
import logging

class Session(ClientXMPP):

  def __init__(self, jid, password, nick):
    ClientXMPP.__init__(self, jid, password)
    self.add_event_handler("session_start", self.session_start)
    self.add_event_handler("message", self.message)
    self.room = 'alumnos'
    self.nick = nick
    # self.add_event_handler("register", self.register)

  def session_start(self, event):
    print('start')
    self.send_presence()
    self.get_roster()

  def message_error(self, msg):
    print('ha ocurrido un error')
    print(msg)
  
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
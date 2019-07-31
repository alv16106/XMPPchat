from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio
from threading import Thread
from menu import menu
import logging
import uuid
import blessed

term = blessed.Terminal()

class Session(ClientXMPP):

  def __init__(self, jid, password, nick):
    ClientXMPP.__init__(self, jid, password)
    self.add_event_handler("session_start", self.session_start)
    self.add_event_handler("message", self.message)
    self.add_event_handler("socks5_connected", self.stream_opened)
    self.add_event_handler("socks5_data", self.stream_data)
    self.add_event_handler("socks5_closed", self.stream_closed)
    self.room = 'alumnos'
    self.nick = nick
    functions = {
      'dc': lambda args: print('Desconectado canino'),
      'list': lambda args: print('Users listados prro'),
      'add': lambda args: print('A;adido sabueso'),
      'peek': lambda args: print('peekeado hermano'),
      'jr': self.join_room,
      'lr': self.leave_room,
      'cpm': lambda args: print('concha de tu puta madre'),
      'sf': self.send_file,
      'rm': lambda args: print('Remove account from server'),
    }
    self.menuInstance = Thread(target = menu, args = (functions,))
    # self.add_event_handler("register", self.register)

  def session_start(self, event):
    self.send_presence()
    self.get_roster()
    self.menuInstance.start()
    
  def message_error(self, msg):
    print('ha ocurrido un error')
    print(msg)
  
  def message(self, msg):
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

  def stream_opened(self, sid):
    logging.info('Stream opened. %s', sid)
    self.file = open(str(uuid.uuid4())+'.txt', 'wb')

  def stream_data(self, data):
    self.file.write(data)

  def stream_closed(self, exception):
    logging.info('Stream closed. %s', exception)
    self.file.close()
  
  def muc_online(self, presence):
    if presence['muc']['nick'] != self.nick:
      print(term.bold(presence['muc']['nick'] + ' se ha unido a la sala'))
      self.send_message(mto=presence['from'].bare, mbody="Hello, %s %s" % (presence['muc']['role'], presence['muc']['nick']), mtype='groupchat')
  
  def join_room(self, room):
    self.add_event_handler("muc::%s::got_online" % room, self.muc_online)
    self.plugin['xep_0045'].join_muc(room, self.nick, wait=True)

  def leave_room(self, msg = ''):
    try:
      xmpp.plugin['xep_0045'].leave_muc(self.jid, self.nick, msg)
    except KeyError:
      log.debug(
        "muc.leave_groupchat: could not leave the room %s",
        self.jid,
        exc_info=True)


  async def send_file(self, filename, receiver):
    try:
      file = open(filename, 'rb')
      # Open the S5B stream in which to write to.
      proxy = await self['xep_0065'].handshake(receiver)
      # Send the entire file.
      while True:
        data = file.read(1048576)
        if not data:
          break
        await proxy.write(data)
        proxy.transport.write_eof()
    except (IqError, IqTimeout):
      print('File transfer errored')
    else:
      print('File transfer finished')
    finally:
      file.close()

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
    
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio
from threading import Thread
from menu import menu
import logging
import sys
import uuid
import blessed

term = blessed.Terminal()

status = [
  'available',
  'unavailable'
]

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
    self.current_reciever = 'alumchat.xyz'
    self.auto_subscribe = True
    functions = {
      'dc': self.dc_and_exit,
      'list': self.get_contacts,
      'add': self.add_contact,
      'peek': lambda args: print('peekeado hermano'),
      'jr': self.join_room,
      'lr': self.leave_room,
      'cpm': self.change_status,
      'sf': self.send_file,
      'rm': self.delete_account,
      'send_message': self.message_sender,
      'jc': self.join_conversation
    }
    self.menuInstance = Thread(target = menu, args = (functions,))
    self.add_event_handler("register", self.register)

  def session_start(self, event):
    self.send_presence()
    self.get_roster()
    self.menuInstance.start()
    
  def dc_and_exit(self, args):
    self.disconnect(wait=2.0)
    sys.exit()
    sys.exit()

  def message_error(self, msg):
    print(term.bold_red('ha ocurrido un error'))
    print(msg)
  
  def message(self, msg):
    if msg['type'] in ('chat', 'normal'):
      print(term.magenta(str(msg['from'])+ ' > ') + term.color(55)(msg['body']))

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
      self.plugin['xep_0045'].leave_muc(self.jid, self.nick, msg)
    except KeyError:
      print(term.bold_red(
        "muc.leave_groupchat: could not leave the room %s",
        self.jid))

  def add_contact(self, contact):
    self.send_presence_subscription(pto=contact)
  
  def get_contacts(self, args):
    print(term.magenta('Users in your contact list: '))
    for jid in self.roster[self.jid]:
      print(term.cyan(jid))
  
  def change_status(self, args):
    if args in status:
      self.make_presence(pshow=args)
    else:
      print(term.bold_red('Estado no valido'))

  def join_conversation(self, args):
    if args in self.roster[self.jid]:
      self.current_reciever = args
    else:
      print(term.bold_red('ERROR: Usuario no en la lista de contactos'))

  def message_sender(self, args):
    self.send_message(mto=self.current_reciever, mbody=args, msubject='normal message', mfrom=self.boundjid)

  def file_sender(self, args):
    asyncio.run(self.send_file(args))

  async def send_file(self, args):
    params = args.strip().split()
    try:
      file = open(params[0], 'rb')
      # Open the S5B stream in which to write to.
      proxy = await self['xep_0065'].handshake(params[1])
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
     
  def delete_account(self, args):
    asyncio.run(self.delete_account_send())

  async def delete_account_send(self):
    resp = self.Iq()
    resp['type'] = 'set'
    resp['from'] = self.boundjid.jid
    resp['register'] = ' '
    resp['register']['remove'] = ' '
    try:
      await resp.send()
      print('')
    except IqError:
      print(term.bold_red('Error al eliminar cuenta'))
    except IqTimeout:
      print(term.bold_red('timeout'))
      self.disconnect()

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
    
from session import Session
import logging
from getpass import getpass
from argparse import ArgumentParser


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument("-j", "--jid", dest="jid", help="JID to use")
  parser.add_argument("-p", "--password", dest="password", help="password to use")
  args = parser.parse_args()

  if args.jid is None:
    args.jid = input("Username: ")
  if args.password is None:
    args.password = getpass("Password: ")

  xmpp = Session(args.jid, args.password, 'amiguito')
  xmpp.register_plugin('xep_0030') # Service Discovery
  xmpp.register_plugin('xep_0004') # Data forms
  xmpp.register_plugin('xep_0066') # Out-of-band Data
  xmpp.register_plugin('xep_0077') # In-band Registration
  xmpp['xep_0077'].force_registration = True

  # Setup logging.
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

  xmpp.connect()
  xmpp.process()

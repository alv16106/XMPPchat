import blessed

term = blessed.Terminal()

options = {
  '/dc': 'Disconect',
  '/list': 'List users',
  '/add': 'Add user to contacts - /add [contact]',
  '/peek': 'See details for user /peek [contact]',
  '/jr': 'Join Room - /jr [room]',
  '/lr': 'Leave Room - /lr [message](optional)',
  '/cpm': 'Change presence message - /cpm [new-message]',
  '/sf': 'Send File - /sf [path-to-file]',
  '/rm': 'Remove account from server',
  '/h': 'Help'
}


def showOptions():
  with term.location(0, int(term.height/2)):
    print(term.center(term.blink('press any key to continue.')))
    for key, value in options.items():
      print(term.bold(key + ': ' +value))

def menu(functions):
  showOptions()
  functions['h'] = showOptions
  while True:
    # get input from user
    message = input(term.move(term.height - 1, 0) + ':')
    # see if it is a command. If not, send message to current conversation
    if message.startswith('/'):
      command = message.strip().split()[0][1:]
      # is in command list?
      if command in functions:
        arg = message[2 + len(command):]
        functions[command](arg)
      else:
        print(term.bold_red('Command ' + command + ' not found, please try again (/h for help on available commands)'))
    else:
      functions['send_message'](message)

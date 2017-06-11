#!/usr/bin/env python
# IRC Bot Skeleton
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/irc
# irc.py

import socket
import ssl
import time

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None
channel  = '#dev'
key      = None

# Identity
nickname  = 'DevBot'
username  = 'devbot'
realname  = 'Python IRC Bot'
cert_file = None

# Login
nickserv_password = None
operator_password = None

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def debug(msg):
    print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
    if reason:
        print(f'{get_time()} | [!] - {msg} ({reason})')
    else:
        print(f'{get_time()} | [!] - {msg}')

def get_time():
    return time.strftime('%I:%M:%S')

class IRC(object):
    def __init__(self):
        self.sock = None

    def action(self, chan, msg):
        self.sendmsg(chan, f'\x01ACTION {msg}\x01')

    def color(self, msg, foreground, background=None):
        if background:
            return f'\x03{foreground},{background}{msg}{reset}'
        else:
            return f'\x03{foreground}{msg}{reset}'

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((server, port))
            if password:
                self.raw('PASS ' + password)
            self.raw(f'USER {username} 0 * :{realname}')
            self.nick(nickname)
        except socket.error as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if use_ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if vhost:
            self.sock.bind((vhost, 0))
        if use_ssl:
            self.sock = ssl.wrap_socket(self.sock, certfile=cert_file)

    def ctcp(self, target, data):
        self.sendmsg(target, f'\001{data}\001')

    def event_connect(self):
        if nickserv_password:
            self.identify(nickname, nickserv_password)
        if operator_password:
            self.oper(username, operator_password)
        self.join_channel(channel, key)

    def event_ctcp(self, nick, chan, msg):
        pass

    def event_disconnect(self):
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_invite(self, nick, chan):
        pass

    def event_join(self, nick, chan):
        pass

    def event_kick(self, nick, chan, kicked):
        if kicked == nickname and chan == channel:
            time.sleep(3)
            self.join_channel(channel, key)

    def event_message(self, nick, chan, msg):
        if msg == '!test':
            self.sendmsg(chan, 'It works!')

    def event_nick_in_use(self):
        error('The bot is already running or nick is in use.')

    def event_part(self, nick, chan):
        pass

    def event_private(self, nick, msg):
        pass

    def event_quit(self, nick):
        pass

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] in ('INVITE','JOIN','KICK','PART','PRIVMSG','QUIT'):
            nick  = args[0].split('!')[0][1:]
            ident = args[0].split('!')[1]
            host  = ident.split('@')[1]
            if nick != nickname:
                if args[1] == 'INVITE':
                    chan = args[3][1:]
                    self.event_invite(nick, chan)
                elif args[1] == 'JOIN':
                    chan = args[2][1:]
                    self.event_join(nick, chan)
                elif args[1] == 'KICK':
                    chan   = args[2]
                    kicked = args[3]
                    self.event_kick(nick, chan, kicked)
                elif args[1] == 'PART':
                    chan = args[2]
                    self.event_part(nick, chan)
                elif args[1] == 'PRIVMSG':
                    chan = args[2]
                    msg  = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
                    if msg.startswith('\001'):
                        self.event_ctcp(nick, chan, msg)
                    elif chan == nickname:
                        self.event_private(nick, msg)
                    else:
                        self.event_message(nick, chan, msg)
                elif args[1] == 'QUIT':
                    self.event_quit(nick)

    def identify(self, nick, passwd):
        self.sendmsg('nickserv', f'recover {nick} {passwd}')
        self.sendmsg('nickserv', f'identify {nick} {passwd}')

    def invite(self, nick, chan):
        self.raw(f'INVITE {nick} {chan}')

    def join_channel(self, chan, key=None):
        if key:
            self.raw(f'JOIN {chan} {key}')
        else:
            self.raw('JOIN ' + chan)

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in (line for line in data.split('\r\n') if line):
                        debug(line)
                        if len(line.split()) >= 2:
                            if line.startswith('ERROR :Closing Link:'):
                                raise Exception('Connection has closed.')
                            else:
                                self.handle_events(line)
                else:
                    error('No data recieved from server.')
                    break
            except (UnicodeDecodeError,UnicodeEncodeError):
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def mode(self, target, mode):
        self.raw(f'MODE {target} {mode}')

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def notice(self, target, msg):
        self.raw(f'NOTICE {target} :{msg}')

    def oper(self, nick, password):
        self.raw(f'OPER {nick} {password}')

    def part(self, chan, msg=None):
        if msg:
            self.raw(f'PART {chan} {msg}')
        else:
            self.raw('PART ' + chan)

    def quit(self, msg=None):
        if msg:
            self.raw('QUIT :' + msg)
        else:
            self.raw('QUIT')

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')

    def topic(self, chan, text):
        self.raw(f'TOPIC {chan} :{text}')

IRC().connect()
# Chatbot based on sleekxmpp http://sleekxmpp.com/
# Uses the echobot template.

# init:
# python3 annabot.py -d -j brukernavn@chat.uio.no -r room@conference.chat.uio.no -n Anna -rtu brukernavn
"""                                                                                          
Initial usage is simple statistics from RequestTracker through xmpp chat.                    
Initial goals for functionality:                                                             
    - Read messages in specific chatroom(s)                                                  
    - If message contains string that matches and RT ticket number, reply with full URL for  
      ticket.                                                                                
        - Ignore messages sent by the bot itself, to prevent loops.                          
"""                                                                                          

import sleekxmpp

import sys
import logging
import getpass

import rt

import re
from optparse import OptionParser

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class AnnaBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, room, nick, rt_user, rt_pw):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)

        # RT tracker setup and login
        tracker = rt.Rt('https://rt.uio.no/rt/REST/1.0/', rt_user, rt_pw)
        tracker.login()





    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event --    An empty dicionary. The session_start
                        event does not provide any additional
                        data.
        """

        #self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # if room pw needed,
                                        # use password = room_pw
                                        wait=True)

    def muc_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """

        #if msg['mucnick'] != self.nick and self.nick in msg['body']:
        #    self.send_message(mto=msg['from'].bare,
        #                    mbody="I heard that, %s." % msg['mucnick'],
        #                    mtype='groupchat')
        
        # Check for rt ticket match and fetch info:
        reg = r"#\d{7}"
        if msg['mucnick'] != self.nick:
            found = re.search(reg,msg['body'])
            if found not None:
                ticket_id = found.group(1)
                ticket_data = rt.get_ticket(ticket_id)



                








if __name__ == "__main__":
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")
    optp.add_option("-rtu", "--rtuser", dest="rt_user",
                    help="RT username")
    optp.add_option("-rtp", "--rtpassword", dest="rt_pw",
                    help="RT password")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.room is None:
        opts.room = raw_input("MUC room: ")
    if opts.nick is None:
        opts.nick = raw_input("MUC nickname: ")
    if opts.rt_user is None:
        opts.rt_user = raw_input("RT username: ")
    if opts.rt_pw is None:
        opts.rt_pw = getpass.getpass("RT Password: ")

    # Setup the MUCBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = AnnaBot(opts.jid, opts.password, opts.room, opts.nick, rt_user, rt_pw)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('chat.uio.no', 5222)):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")





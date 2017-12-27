"""
Customized version of JabberBot:
    https://sourceforge.net/p/pythonjabberbot/code/ci/master/tree/jabberbot.py

Initial usage is simple statistics from RequestTracker through xmpp chat.
Initial goals for functionality:
    - Read messages in specific chatroom(s)
    - If message contains string that matches and RT ticket number, reply with full URL for
      ticket.
        - Ignore messages sent by the bot itself, to prevent loops.
"""

import os
import re
import sys
import xmpp

import time
import inspect
import logging
import traceback

class AnnaBot(object):

    PING_FREQUENCY = 0 # Set to the number of seconds, e.g. 60
    PING_TIMEOUT = 2 # Seconds to wait for a responce
    
    def __init__(self, username, password, res=None, debug=False,
            server=None, port=5222):
        """
        Initializes the bot and sets up commands.

        username and password should be clear


        """
        
        self.__debug = debug
        self.log = logging.getLogger(__name__)
        if server is not None:
            self.__server = (server, port)
        else:
            self.__server = None

        self.__username = username
        self.__password = password
        self.jid = xmpp.JID(self,__username)
        self.res = self.__class__.__name__
        self.conn = None
        self.__finished = None
        self.__show = None
        self.__status = None
        self.__seen = {}
        self.__threads = {}
        self.__lastping = time.time()


        # Original collects commands from source here.
        # Probably not needed for inital use?

    # ====================================================

    def connect(self):
        """
        Connects the bot to server or returns current connection,
        send initial presence stanza
        """
        
        if not self.conn:
            if self.__debug:
                conn = xmpp.Client(self.jid.getDomain())
            else:
                conn = xmpp.Client(self.jid.getDomain, debug=[])

        # Connection attempt
        if self.__server:
            conres = conn.connect(self.__server)
        else:
            conres = conn.connect
        
        if not conres:
            self.log.error('unable to establish secure connection - TLS failed!')

        if conres != 'tls':
            self.log.warning('unable to authorize with server.')
            return None
        if authres != 'sasl':
            self.log.warning("unable to perform SASL auth on %s. "\
                    "Old authentication method used!" % self.jid.getDomain())

        # Connection established - save connection
        self.conn = conn

        # Send initial presence stanza (say hello to everyone)
        self.conn.sendInitPresence()
        # Save roster and log items
        self.roster = self.conn.Roster.getRoster()
        self.log.info('*** roster ***')
        for contact in self.roster.getItems():
            self.log.info('  %s' % contact)
        self.log.info('*** roster ***')

        return self.conn

   
   ## XEP-0045 Multi User Chat # prefix: muc # START ###

    def muc_join_room(self, room, username=None, password=None, prefix=""):
        """Join the specified multi-user chat room or changes nickname

        If username is NOT provided fallback to node part of JID"""
        # TODO fix namespacestrings and history settings
        NS_MUC = 'http://jabber.org/protocol/muc'
        if username is None:
            # TODO use xmpppy function getNode
            username = self.__username.split('@')[0]
        my_room_JID = '/'.join((room, username))
        pres = xmpp.Presence(to=my_room_JID)
        if password is not None:
            pres.setTag('x', namespace=NS_MUC).setTagData('password', password)
        self.connect().send(pres)

    ## MUC END
    def get_sender_username(self, mess):
        """Extract the sender's user name from a message"""
        type = mess.getType()
        jid = mess.getFrom()
        if type == "groupchat":
            username = jid.getResource()
        elif type == "chat":
            username = jid.getNode()
        else:
            username = ""
        return username



    def callback_message(self, conn, mess):
        """Messages sent to the bot will arrive here.
        Command handling + routing is done in this function."""

        # Prepare to handle only conference type messages.
        type = mess.getType()
        jid = mess.getFrom()
        props = mess.getProperties()
        text = mess.getBody()
        username = self.get_sender_username(mess)

        if type not "conference":
            self.log.debug("unhandled message type: %s" % type)
            return

        # Ignore messages from before we joined
        if xmpp.NS_DELAY in props:
            return

        # Ignore messages from myself
        if self.jid.bareMatch(jid):
            return

        self.log.debug("*** props = %s" % props)
        self.log.debug("*** jid = %s" % jid)
        self.log.debug("*** username = %s" % username)
        self.log.debug("*** type = %s" % type)
        self.log.debug("*** text = %s" % text)

        # If a message format is not supported (eg. encrypted),
        # txt will be None
        if not text:
            return

        # Match regex and perform RT API call here
        # Needs function for sending a simple message.



    def idle_proc(self):
        """This function will be called in the main loop."""
        self._idle_ping()

    def _idle_ping(self):
        """Pings the server, calls on_ping_timeout() on no response.

        To enable set self.PING_FREQUENCY to a value higher than zero.
        """
        if self.PING_FREQUENCY \
            and time.time() - self.__lastping > self.PING_FREQUENCY:
            self.__lastping = time.time()
            #logging.debug('Pinging the server.')
            ping = xmpp.Protocol('iq', typ='get', \
                payload=[xmpp.Node('ping', attrs={'xmlns':'urn:xmpp:ping'})])
            try:
                res = self.conn.SendAndWaitForResponse(ping, self.PING_TIMEOUT)
                #logging.debug('Got response: ' + str(res))
                if res is None:
                    self.on_ping_timeout()
            except IOError, e:
                logging.error('Error pinging the server: %s, '\
                    'treating as ping timeout.' % e)
                self.on_ping_timeout()
    
    def on_ping_timeout(self):
        logging.info('Terminating due to PING timeout.')
        self.quit()

    def shutdown(self):
        """
        This function will be called when we're done serving

        Override this method in derived class if you
        want to do anything special at shutdown.
        """
        pass


    def serve_forever(self):
        """
        Connects to the server and handles messages.
        """
        conn = self.connect()
        if conn:
            self.log.info('Bot connected for eternal servitude.')
        else:
            self.log.warn('Could not connect to server - aborting')
            return

        while not self.__finished:
            try: 
                conn.Process(1)
                self.idle_proc()
            except KeyboardInterrupt:
                self.log.info('Bot stopped by user request. '\
                        'Shutting down.')
                break







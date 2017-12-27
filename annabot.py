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



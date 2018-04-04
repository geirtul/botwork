#!/usr/bin/perl

# ChatBot for houston based on: 
# https://codehacienda.wordpress.com/2011/02/25/perl-xmpp-library-for-creating-a-chat-bot-anyeventxmpp-example/


use utf8;
use AnyEvent;
use AnyEvent::XMPP::IM::Connection;
use AnyEvent::XMPP::IM::Presence;
use AnyEvent::XMPP::Util qw/split_jid/;
 
my $j = AnyEvent->condvar;



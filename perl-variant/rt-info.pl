#!/usr/bin/perl
use utf8;
use strict;
use warnings;

use Term::ReadKey;
use LWP::UserAgent;
use Data::Dumper;

# Get user credentials
print "RT Username: \n";
chomp(my $uname = <STDIN>);
print "RT Password: \n";
ReadMode('noecho'); 	# Disable echo
chomp(my $upass = <STDIN>);
ReadMode('restore'); 	# Reenable echo

# Set variables for RT ticket lookup
my $uri = "https://rt.uio.no/REST/1.0/";
my $access_user = $uname;
my $access_password = $upass;
my $ticket_number = "2916486";
#print "RT Ticket to look up:\n";
#chomp(my $ticket_number = <STDIN>);

# Set up user agent ua
my $ua = LWP::UserAgent->new;
$ua->timeout(10);
$ua->agent("Mozilla/5.0");

# Get ticket info
my $response = $ua->post($uri."ticket/$ticket_number",
	['user' => $access_user, 'pass' => $access_password],
	 'Content_Type' => 'form-data');
my $returned_content = $response->decoded_content(default_charset => 'UTF-8');

# Store content as hash table using a nice regex <3
my %content = $returned_content =~ /(.+): (.+)\n/g;

print Dumper \%content;



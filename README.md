# irc
A class for the Internet Relay Chat (IRC) protocol.

###### Information
A simple skeleton IRC bot that handles some common events.

The only command it has, as an example, is `!test`, which will reply "It Works!" into the channel.

More events and data can be parsed and handled by making changes to the `handle_events` function.

If the configuration nick is in use, it will try to add an underscore to the end and connection.

###### IRC RCF 2812 Reference
 - https://tools.ietf.org/html/rfc2812
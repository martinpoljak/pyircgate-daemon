
 PyIRCGate Daemon 0.1
#####################
(c) 2009 - 2010 Martin Kozák (martinkozak@martinkozak.net)

Framework should be stable, but it hasn't been tested in real 
production environment.


Short Tutorial for Example Plugins Set
--------------------------------------

Example applications allows connect to daemon through RPC and send a message to
predefined multiple IRC channels through it.

Targets are groups of channels and/or users.

Configuration for modules (plugins, transfer agents) are placed in the agent's
and module's folders. Automatic authorization to NickServ isn't supported, only 
standard IRC password authorization is. But it's posible to send to NickServ an 
authorization message manually by creating appropriate target and sending it to 
this target manually.

Crucial part of the example application is module ./modules/ircgate/ircgate.py,
functions shutdown() and reload() are general, so they are defined in 
./modules/system/system.py. Framework as is defined in main.py. 
XML-RPC a JSON-RPC are supported. API is:

 * shutdown([password])
 * reload([password])
 * ircgate(target, message[, password])
 
Or directly from (and through) IRC protocol:

 * shutdown[ password] (via query) -- shutdown server
 * reload[ password] (via query) -- reload server including (for example 
      new one) configuration

Bot can be run through 'python main.py'. Small examples of RPC clients are 
available at ./clients. 

Modules can be deactivated by joing the ".off" extension.



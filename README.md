# mcp-slave
Listens to commands from master to do a few tests

# Version 0.2
-   removed threads in favour of one listener, was easier to actually close and re-open connections.
    There is still some leftovers, hopefully I'll be able to remove them in the next Version
-   modules are unchanged and still won't do the stuff you'd expect them to do, sorry
-   Works fine locally

# rpi-ddns-hover

## Description

This is a Python script that I created for use with my Raspberry Pi to auto update Hover DNS entries with the Pi's current Public IP address. This can be used to make your own DDNS service. Services like DynDNS and NOIP are great for simple solutions, but DynDNS requires a yearly fee and NOIP requires the user to confirm the host address every 30 days.

This script creates a ip.db SQLite database in its directory which will log the current IP address and a timestamp. If the IP address changes, it will log the new IP address and update the corresponding Hover domain.

## Requirements

* SQLite3
* Python Requests library from pip

## Credit

Thank you to [bryfry](https://github.com/bryfry) for the main Hover API functions, which can be found at the [bryfry/dynhover](https://github.com/bryfry/dynhover) GitHub repo.
# General
prtg_automation_scripts is a set of scripts for automating tasks leveraging a PRTG and PHPIPAM that can automatically bounce an interface for a PoE endpoint that is not reconnecting after a power event. 

The credentials can be swapped out with the preferred credentialling method and credentials themselves. 
As well modify the API connections to IPAM. 

## prtg_api_check_down.py
### Checks for alarmed sensors, bounces interface to endpoint, auto-acknolwedges, notifies via email of action

The script checks into PRTG first to detect for alarms of "Down" devices. If an alarm is detected the flow is as such:
1. Checks if device is part of a group of devices
    1. If `True`: Proceed forward
    2. Else: Takes no action and moves onto next alarm
2. With the IP obtained for PRTG under Device properties, perform an API call to phpIPAM instance to gather network details (Switch, Interface)
3. With network details, will make a connection to the switch, check that the interface is `down`, then perform a port-bounce.
    1. sleep 5 secs, then check if interface is seen in `up` status on switch.
4. Acknoweldge the issue in PRTG (closes issue)
5. Send Email Notification out to selected group.

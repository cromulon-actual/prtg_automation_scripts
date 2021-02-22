import requests
import urllib3

from modules.nice import prtg_creds  # created a local copy of stored credentials
from modules.utils import wr_to_json
from pprint import pprint as pp

urllib3.disable_warnings()
userName = prtg_creds.username
userPass = prtg_creds.userpass
prtg_base_url = prtg_creds.url
auth_string = f"&username={userName}&password={userPass}"
# XML Sensor Tree.
content = "table.json?content=sensors&columns=objid,group,device,sensor,status&"
get_type = "sensor_tree_objects"

# Requests
prtg_url = f"{prtg_base_url}{content}{auth_string}"
results = requests.get(prtg_url, verify=False)
pp(results.json())

wr_to_json(results.json(), f"files/{get_type}.json")

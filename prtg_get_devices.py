import requests
from modules.nice import prtg_creds  # created a local copy of stored credentials
from modules.utils import wr_to_json
from pprint import pprint as pp
import urllib3

urllib3.disable_warnings()
userName = prtg_creds.username
userPass = prtg_creds.userpass
prtg_base_url = prtg_creds.url
auth_string = f"&username={userName}&password={userPass}"

prtg_url = f"{prtg_base_url}table.json?content=sensors&columns=objid,device,group,sensor&{auth_string}"

results = requests.get(prtg_url, verify=False)

wr_to_json(results.json(), "files/prtg_sensors.json")
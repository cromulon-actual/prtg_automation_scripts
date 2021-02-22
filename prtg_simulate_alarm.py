import requests
import urllib3

from modules.nice import prtg_creds  # created a local copy of stored credentials
from modules.utils import pj, wr_to_json
from pprint import pprint as pp

urllib3.disable_warnings()
userName = prtg_creds.username
userPass = prtg_creds.userpass
prtg_base_url = prtg_creds.url
auth_string = f"&username={userName}&password={userPass}"
objectid = 2293
content = f"simulate.htm?id={objectid}&action=1"
prtg_url = f"{prtg_base_url}{content}{auth_string}"

results = requests.get(prtg_url, verify=False)
print(results.status_code)

pp(results.text)

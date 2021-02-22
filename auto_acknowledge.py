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

objectid = 2293

prtg_url = f"{prtg_base_url}acknowledgealarm.htm?id={objectid}&ackmsg=Auto-Acknowledged&{auth_string}"

r = requests.post(prtg_url, verify=False)
print(r.status_code)
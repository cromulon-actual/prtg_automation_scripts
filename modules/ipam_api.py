import phpipamsdk
import warnings
from modules.nice import ipam_creds  # personal credentials
from phpipamsdk.controllers.addresses_api import AddressesApi
from phpipamsdk.controllers.devices_api import DevicesApi


class ApiIpam(object):
    warnings.filterwarnings("ignore")
    IPAM = phpipamsdk.PhpIpamApi(
        api_uri=ipam_creds.url, api_appcode=ipam_creds.api, api_verify_ssl=True
    )

    IPAM.login()

    def __init__(self, ip=None):
        self.ip = ip

    def get_info(self):

        ip_info = AddressesApi(phpipam=self.IPAM).search_address(address=self.ip)
        mac = ip_info["data"][0]["mac"]
        mac = mac.split(" ")
        mac = ("").join(mac).lower()
        mac = (".").join(mac[i : i + 4] for i in range(0, len(mac), 4))

        deviceID = ip_info["data"][0]["deviceId"]
        switch = self.get_switch(deviceId=deviceID)

        interface = ip_info["data"][0]["port"]

        ip_info = {"ip": self.ip, "mac": mac, "switch": switch, "interface": interface}

        return ip_info

    def get_switch(self, deviceId=None):
        device_info = DevicesApi(phpipam=self.IPAM).get_device(device_id=deviceId)
        switch = device_info["data"]["hostname"]

        return switch

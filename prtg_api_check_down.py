import requests
import urllib3
import time
import multiprocessing

from modules.nice import prtg_creds  # created a local copy of stored credentials
from modules.utils import wr_to_json
from modules.ipam_api import ApiIpam
from modules.smtp_notification import Email
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result
from pprint import pprint as pp


def api_caller(method, content):
    urllib3.disable_warnings()
    userName = prtg_creds.username
    userPass = prtg_creds.userpass
    prtg_base_url = prtg_creds.url
    auth_string = f"&username={userName}&password={userPass}"
    prtg_url = f"{prtg_base_url}{content}{auth_string}"
    
    if method == "get":
        r = requests.get(prtg_url, verify=False)
        return r.json()
    elif method == "post":
        r = requests.post(prtg_url, verify=False)
        return f"Auto-Acknowledged status code: {r.status_code}"


def build_security_devices(prtg_devices):
    for info in prtg_devices.values():
        if type(info) is list:
            device_list = info
            device_list = list(
                item
                for item in device_list
                for (k, v) in item.items()
                if (k == "group" and v == "Lenel Security Cameras")
                or (k == "group" and v == "Stentophones")
            )
    security_devices = {"Security Devices": device_list}
    return security_devices


def detect_device_group(device):
    dev_group = ["Lenel Security Cameras", "Stentophones"]
    if device["group"] in dev_group:
        return device["group"]
    else:
        return None


def clear_endpoints(down_devices):
    for device in down_devices:
            dev_group = detect_device_group(device)
            if dev_group is None:
                down_devices.remove(device)
    return down_devices


def get_device_info(deviceName, security_devices):
    device_list = security_devices["Security Devices"]
    for device in device_list:
        if device["device"] == deviceName:
            if device["host"] != "":
                host_ip = device["host"]
                print(host_ip)
                return host_ip
            else:
                return None


def attempt_http(deviceIP):
    print(f"Starting http attempt for {deviceIP}")
    try:
        requests.get(f"http://{deviceIP}", verify=False, timeout=1)
        return True
    except requests.exceptions.ConnectionError:
        return False


def bounce_interface(switch, interface):
    port_bounce = [
        f"interface {interface}",
        "shutdown",
        "no shutdown",
        f"do show ip int bri | sec {interface}",
    ]
    nr = InitNornir(config_file="config.yaml")
    router = nr.filter(name=switch)

    port_check = router.run(
        task=netmiko_send_command,
        command_string=f"show ip int bri | sec {interface}",
        enable=True,
    )
    print_result(port_check)

    print(f"Bouncing interface {interface} on {switch}.")
    result = router.run(netmiko_send_config, config_commands=port_bounce)

    time.sleep(5)

    result = router.run(
        task=netmiko_send_command,
        command_string=f"show ip int bri | sec {interface}",
        enable=True,
    )
    
    print_result(result)


def device_action(device, security_devices):
    deviceName = device["device"]
    objectid = device["objid"]
    prtg_issue_ack = f"acknowledgealarm.htm?id={objectid}&ackmsg=Auto-Acknowledged&"
    deviceIP = get_device_info(deviceName, security_devices)
    if deviceIP is not None:
        test = attempt_http(deviceIP)
        if test is False:
            ip_info = ApiIpam(ip=deviceIP).get_info()
            switch = ip_info["switch"]
            interface = ip_info["interface"]
            if switch is not None and interface is not None:
                bounce_interface(switch, interface)
                api_caller("post", prtg_issue_ack)
                Email(
                    deviceName=deviceName,
                    switch=switch,
                    interface=interface,
                    ip=deviceIP,
                ).notify()
            else:
                with open("ipam_miss_info.txt", "a+") as f:
                    missing_info = {deviceIP: {'switch': switch, 'interface': interface}}
                    f.write(missing_info)
                pass

        else:
            print(f"{deviceName} is online")


def main():
    # Parse for Security devices (IP Cameras, and Stentofons)
    prtg_devices_api = "table.json?content=devices&columns=objid,group,device,host&output=json"
    prtg_devices = api_caller("get", prtg_devices_api)
    security_devices = build_security_devices(prtg_devices)
    wr_to_json(security_devices, "files/security_devices.json")

    # API Get for downed device alarms
    fil_stat = "5"
    prtg_api_detection = f"table.json?content=sensors&columns=objid,downtimesince,device,group,sensor,lastvalue,status,message,priority&filter_status={fil_stat}"
    sensors_detected = api_caller("get", prtg_api_detection)    
    wr_to_json(sensors_detected, "files/api_check.json")

    # take action if needed on devices
    if sensors_detected["treesize"] >= 1:
        print(f"There were a total of {len(sensors_detected['sensors'])} down devices detected")
        downed_devices = {"Down Devices": sensors_detected['sensors']}
        wr_to_json(downed_devices, "files/downed_devices.json")

        down_devices = list(clear_endpoints(sensors_detected["sensors"]))  
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
        
        for device in down_devices:            
            pool.apply_async(device_action(device, security_devices))
        
    else:
        print("Zero Offline Devices were detected.")
    
    
if __name__ == "__main__":
    main()
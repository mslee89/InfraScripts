import requests
import time
import logging

AMBARI_SERVER = "도메인 ex) https://ambari.com"
CLUSTER_NAME = "클러스터 이름"
USERNAME = "관리자 계정"
PASSWORD = "패스워드"
CHECK_INTERVAL = 300  # seconds. 해당 주기 동안 HBase 상태를 점검하고 구동하기 위한 Interval

# Logging 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_all_slave_hosts():
    url = f"{AMBARI_SERVER}/api/v1/clusters/{CLUSTER_NAME}/hosts"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    response.raise_for_status()
    hosts = [host["Hosts"]["host_name"] for host in response.json()["items"] if host["Hosts"]["host_name"].startswith("slave")]
    return hosts

def get_regionserver_status(host):
    url = f"{AMBARI_SERVER}/api/v1/clusters/{CLUSTER_NAME}/hosts/{host}/host_components/HBASE_REGIONSERVER"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 404:
        return "NOT_FOUND"  # If HBASE_REGIONSERVER component not found on host
    response.raise_for_status()
    return response.json()["HostRoles"]["state"]

def start_regionserver(host):
    url = f"{AMBARI_SERVER}/api/v1/clusters/{CLUSTER_NAME}/hosts/{host}/host_components/HBASE_REGIONSERVER"
    headers = {
        "X-Requested-By": "ambari",
        "Content-Type": "application/json"
    }
    data = {
        "RequestInfo": {
            "context": "Start HBase RegionServer via API",
            "operation_level": {
                "level": "HOST_COMPONENT",
                "cluster_name": CLUSTER_NAME,
                "host_name": host,
                "service_name": "HBASE"
            }
        },
        "Body": {
            "HostRoles": {
                "state": "STARTED"
            }
        }
    }
    response = requests.put(url, auth=(USERNAME, PASSWORD), headers=headers, json=data)
    response.raise_for_status()
    logging.info(f"HBase RegionServer started on host {host}")

def monitor_regionserver():
    while True:
        try:
            hosts = get_all_slave_hosts()
            for host in hosts:
                status = get_regionserver_status(host)
                if status != "STARTED":
                    logging.info(f"HBase RegionServer on host {host} is {status}. Restarting...")
                    start_regionserver(host)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_regionserver()
import requests
import time
import logging
import os

# 환경 변수에서 설정값을 읽고, 없으면 기본값 사용
AMBARI_SERVER = os.getenv("AMBARI_SERVER", "https://ambari.com")
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "my-cluster")
USERNAME = os.getenv("AMBARI_USER", "admin")
PASSWORD = os.getenv("AMBARI_PASS", "password")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))  # seconds

# Logging 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_all_slave_hosts():
    """
    Get all hosts whose name starts with 'slave' from Ambari API.
    """
    url = f"{AMBARI_SERVER}/api/v1/clusters/{CLUSTER_NAME}/hosts"
    try:
        response = requests.get(url, auth=(USERNAME, PASSWORD), timeout=10)
        response.raise_for_status()
        hosts = [host["Hosts"]["host_name"] for host in response.json()["items"] if host["Hosts"]["host_name"].startswith("slave")]
        return hosts
    except Exception as e:
        logging.error(f"[get_all_slave_hosts] {e}")
        return []

def get_regionserver_status(host):
    """
    Get the HBase RegionServer status for a specific host.
    """
    url = f"{AMBARI_SERVER}/api/v1/clusters/{CLUSTER_NAME}/hosts/{host}/host_components/HBASE_REGIONSERVER"
    try:
        response = requests.get(url, auth=(USERNAME, PASSWORD), timeout=10)
        if response.status_code == 404:
            return "NOT_FOUND"
        response.raise_for_status()
        return response.json()["HostRoles"]["state"]
    except Exception as e:
        logging.error(f"[get_regionserver_status] {host}: {e}")
        return "ERROR"

def start_regionserver(host):
    """
    Start the HBase RegionServer on a specific host.
    """
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
    try:
        response = requests.put(url, auth=(USERNAME, PASSWORD), headers=headers, json=data, timeout=10)
        response.raise_for_status()
        logging.info(f"[start_regionserver] HBase RegionServer started on host {host}")
    except Exception as e:
        logging.error(f"[start_regionserver] {host}: {e}")

def monitor_regionserver():
    """
    Periodically check the RegionServer status on all slave hosts and restart if not running.
    """
    while True:
        hosts = get_all_slave_hosts()
        if not hosts:
            logging.warning("[monitor_regionserver] No slave hosts found. Retrying after interval...")
            time.sleep(CHECK_INTERVAL)
            continue
        for host in hosts:
            status = get_regionserver_status(host)
            if status == "STARTED":
                logging.info(f"[monitor_regionserver] {host}: RegionServer is STARTED.")
            elif status == "NOT_FOUND":
                logging.warning(f"[monitor_regionserver] {host}: RegionServer component NOT FOUND.")
            elif status == "ERROR":
                logging.error(f"[monitor_regionserver] {host}: Failed to get status.")
            else:
                logging.warning(f"[monitor_regionserver] {host}: RegionServer is {status}. Restarting...")
                start_regionserver(host)
        time.sleep(CHECK_INTERVAL)

def main():
    logging.info("[main] Auto HBase RegionServer Monitor started.")
    monitor_regionserver()

if __name__ == "__main__":
    main()
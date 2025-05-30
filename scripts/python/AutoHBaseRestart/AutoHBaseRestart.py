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
    Ambari API를 통해 slave로 시작하는 모든 호스트 목록을 반환
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
    특정 호스트의 HBase RegionServer 상태를 반환
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
    특정 호스트의 HBase RegionServer를 시작
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
    모든 slave 호스트의 RegionServer 상태를 주기적으로 점검하고, 비정상 시 재시작
    """
    while True:
        hosts = get_all_slave_hosts()
        if not hosts:
            logging.warning("[monitor_regionserver] No slave hosts found. 재시도 대기...")
            time.sleep(CHECK_INTERVAL)
            continue
        for host in hosts:
            status = get_regionserver_status(host)
            if status == "STARTED":
                logging.info(f"[monitor_regionserver] {host}: RegionServer is STARTED.")
            elif status == "NOT_FOUND":
                logging.warning(f"[monitor_regionserver] {host}: RegionServer component NOT FOUND.")
            elif status == "ERROR":
                logging.error(f"[monitor_regionserver] {host}: 상태 조회 실패.")
            else:
                logging.warning(f"[monitor_regionserver] {host}: RegionServer is {status}. Restarting...")
                start_regionserver(host)
        time.sleep(CHECK_INTERVAL)

def main():
    logging.info("[main] Auto HBase RegionServer Monitor 시작")
    monitor_regionserver()

if __name__ == "__main__":
    main()
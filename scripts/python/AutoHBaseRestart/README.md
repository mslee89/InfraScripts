# AutoHBaseRestart

이 스크립트는 Ambari API를 이용해 HBase RegionServer의 상태를 주기적으로 점검하고 비정상 상태일 경우 자동으로 재시작하는 Python 기반 자동화 도구입니다.

## 주요 기능
- Ambari API를 통해 slave 노드 목록을 조회
- 각 slave 노드의 HBase RegionServer 상태를 주기적으로 점검
- RegionServer가 비정상(중지, 에러 등)일 경우 자동으로 재시작
- 모든 설정은 환경 변수로 관리 가능
- 로깅을 통해 상태 및 에러 내역 기록

## 환경 변수 설정
| 변수명            | 설명                              | 예시 값                  |
|-------------------|-----------------------------------|--------------------------|
| AMBARI_SERVER     | Ambari 서버 주소                  | https://ambari.example.com |
| CLUSTER_NAME      | Ambari 클러스터 이름              | my-cluster               |
| AMBARI_USER       | Ambari 관리자 계정                | admin                    |
| AMBARI_PASS       | Ambari 관리자 비밀번호            | password                 |
| CHECK_INTERVAL    | 점검 주기(초)                     | 300                      |

환경 변수는 실행 전 export 하거나, systemd 서비스 파일에서 `Environment=`로 지정할 수 있습니다.

## 실행 방법
```bash
# 환경 변수 설정 예시
export AMBARI_SERVER=https://ambari.example.com
export CLUSTER_NAME=my-cluster
export AMBARI_USER=admin
export AMBARI_PASS=yourpassword
export CHECK_INTERVAL=300

# 실행
python3 AutoHBaseRestart.py
```

## systemd 서비스 등록 예시
`auto-hbase-restart.service` 파일을 참고하여 등록할 수 있습니다.

## 참고 사항
- Ambari API 계정은 HBase RegionServer 제어 권한이 필요합니다.
- 로그는 표준 출력에 기록되며 필요시 리다이렉트 또는 systemd의 journalctl로 확인할 수 있습니다.
- 네트워크 장애, 인증 오류 등으로 인해 일시적으로 점검/재시작이 실패할 수 있습니다.
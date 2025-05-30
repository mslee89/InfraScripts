#!/bin/sh
# CentOS 6 이하에서 패스워드 해시 알고리즘을 sha512로 변경하는 스크립트
# 기존 알고리즘이 md5일 때만 변경, 이미 sha512면 변경하지 않음
# 기타 값이거나 실패 시 에러 반환

set -e  # 에러 발생 시 즉시 종료

get_current_algo() {
    authconfig --test | grep algorithm | awk '{print $5}'
}

main() {
    HOST=$(hostname)
    CUR_ALGO=$(get_current_algo)

    case "$CUR_ALGO" in
        md5)
            authconfig --passalgo=sha512 --update
            NEW_ALGO=$(get_current_algo)
            echo "$HOST: Password algorithm updated - $CUR_ALGO → $NEW_ALGO"
            ;;
        sha512)
            echo "$HOST: No change needed - Current algorithm is $CUR_ALGO"
            ;;
        *)
            echo "$HOST: Failed to detect password algorithm (got: $CUR_ALGO)" >&2
            exit 2
            ;;
    esac
}

main "$@"
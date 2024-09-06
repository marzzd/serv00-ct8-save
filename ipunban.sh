#!/bin/bash

# 生成随机用户代理
gen_random_useragent() {
    local browsers=("Chrome" "Firefox" "Safari" "Edge" "Opera")
    local browser="${browsers[RANDOM % ${#browsers[@]}]}"
    local version=$((RANDOM % 100))
    local fake_os=("Windows NT 10.0" "Macintosh" "X11")
    local selected_os="${fake_os[RANDOM % ${#fake_os[@]}]}"
    local os_version="Win64; x64"

    if [[ "$selected_os" == "X11" ]]; then
        os_version="Linux x86_64"
    elif [[ "$selected_os" == "Macintosh" ]]; then
        os_version="Intel Mac OS X 10_15_7"
    fi

    echo "User-Agent:Mozilla/5.0 ($selected_os; $os_version) AppleWebKit/537.36 (KHTML, like Gecko) $browser/$version.0.0.0 Safari/537.36"
}

# IP解锁
ipunban() {
    local ip="$1"
    local hostname="$2"
    local now_time="$3"

    local ip_unban_url="https://www.serv00.com/ip_unban/"
    if [[ "$hostname" != *"serv00"* ]]; then
        ip_unban_url="https://www.ct8.pl/ip_unban/"
    fi

    user_agent=$(gen_random_useragent)
    command="curl -X GET -i $ip_unban_url -H 'user-agent:$user_agent'"
    response=$(eval $command)

    if [[ ! $response == *"$ip"* ]]; then
        echo "服务器ip：$ip 于北京时间: $now_time 解锁域名：$hostname 失败，原因：官方解锁界面ip与本地不一致"
        exit 1
    fi

    local servnum=$(echo "$response" | awk -v search="$hostname" -F'value="|">' '$0 ~ search {print $2}')
    local csrf=$(echo "$response" | awk -F"value='" '/name='\''csrfmiddlewaretoken'\''/ {print $2}' | awk -F"'" '{print $1}')

    post_command="curl -X POST -i $ip_unban_url -H 'user-agent:$user_agent' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Referer: $ip_unban_url' -H 'cookie: csrftoken=$csrf' --data-raw 'server=$servnum'"
    post_response=$(eval $post_command)

    if [[ $post_response == *"status: 201"* ]] && [[ $post_response == *"{\"status\": \"OK\"}" ]]; then
        echo "服务器ip：$ip 于北京时间: $now_time 解锁域名：$hostname 成功"
    else
        echo "服务器ip：$ip 于北京时间: $now_time 解锁域名：$hostname 失败，原因：解锁返回结果失败，请手动解锁，返回内容：$post_response"
    fi
}


# 获取当前主机IP和其他信息
main() {
    local ip=$(ping -c 1 $(hostname) | awk -F'[()]' '/PING/{print $2}')
    local now_time=$(TZ='Asia/Shanghai' date +"%Y-%m-%d %H:%M:%S")

    # 如果一个hostname都没传，则自己解锁自己
    if [ "$#" -eq 0 ]; then
        local hostname=$(hostname)
        ipunban "$ip" "$hostname" "$now_time"
        exit 1
    fi

    # Loop through all the provided hostnames
    for hostname in "$@"; do
        # 调用ipunban函数
        ipunban "$ip" "$hostname" "$now_time"
    done
}

# 调用main函数并传入所有的hostname参数
main "$@"

#!/bin/bash

# 设置hysteria的定时任务

# 获取当前用户名
USER=$(whoami)
USER_HOME=$(readlink -f /home/$USER) # 获取标准化的用户主目录
HYSTERIA_WORKDIR="$USER_HOME/.hysteria"

add_crontab_task() {
  local txt="$HYSTERIA_WORKDIR/web server $HYSTERIA_WORKDIR/config.yaml"
  local file="/tmp/crontab.bak"

  crontab -l > $file
  # 使用 grep 搜索字符串
  if ! grep -q "$txt" "$file"; then
    echo "*/12 * * * * if ! pgrep -x web; then nohup $txt >/dev/null 2>&1 & fi" >> $file
    crontab $file
    echo "任务添加完成"
  else
      echo "任务已存在，无需添加"
  fi
  rm $file
}

add_crontab_task

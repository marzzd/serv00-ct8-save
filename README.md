
# 说明 
由于pm2容易被封号，本项目通过python实现定期批量登录serv00与ct8，从而达到保活的目的。
主要实现功能包括ssh登录并触发ip解锁（如果存在多个vps配置，则每个vps均会访问其他vps进行ip解锁操作，如果只有1个vps，则只会使用自己的ip进行解锁，意义不大），
以及管理页面登录，并将登录结果推送至telegram

**喜欢的话麻烦动动小指头点个Star🌟🌟🌟支持下**

### 准备serv00或ct8账号，用户名，密码，ssh连接地址，管理后台连接地址

### 获取Telegram的Chat ID以及Bot Token
- **BOT_TOKEN**
    - 示例值: `1234567890:ABCDEFghijklmnopQRSTuvwxyZ`
    - 获取方法: 在 Telegram 中使用 `@BotFather` 创建 Bot 并获取 API Token。
- **CHAT_ID**
    - 示例值: `1234567890`
    - 获取方法: 发送一条消息给你创建的 Bot，然后浏览器访问 `https://api.telegram.org/bot<your_bot_token>/getUpdates` ，chat对象里的id值，即Chat ID。

#### Fork 仓库
- 点击仓库页面右上角的 "Fork" 按钮，将仓库 fork 到你的 GitHub 账户下。


### 设置 GitHub Secrets
- 转到你 fork 的仓库页面。
- 点击 `Settings`，然后在左侧菜单中选择 `Secrets and variable`下的`Actions`。
- 在 `Secrets` 栏添加以下配置：
  - **配置SAVE_INFO**
    - `SAVE_INFO`：包含SSH与管理后台连接信息的JSON字符串。以下是示例
      ```json
      [
        {"ssh_url": "ssh连接地址", "panel_url":"管理后台地址", "username": "用户名", "password": "密码","script": "额外命令"},
        {"ssh_url": "s5.serv00.com","panel_url":"panel5.serv00.com", "username": "user", "password": "password"},
        {"ssh_url": "s1.ct8.pl","panel_url":"panel.ct8.pl", "username": "user6", "password": "password6","script": "bash <(curl -s https://raw.githubusercontent.com/marzzd/serv00-ct8-save/main/script.sh)"}
      ]
      ```
      注意：script属性是针对ip解封命令执行完毕后的额外单行命令，用户可自行设置，用于满足其他需求
  - **配置TEL_INFO**
    - `TEL_INFO`：包含telegram的bot token与telegram chat id**
    - 格式如下：

      ```json
        {"tel_bot_token": "telegram的bot token", "tel_chat_id":"telegram的chat id"}
      ```
    - 示例如下：
      ```json
        {"tel_bot_token": "1234567890:ABCDEFghijklmnopQRSTuvwxyZ", "tel_chat_id":"1234567890"}
      ```

### 测试运行

- 1.点击fork仓库的`Actions`选项卡中
- 2.选中左侧的`Auto Save`工作流程
- 3.点击右侧的`Run workflows`，选择`main`分支
- 4.点击绿色图标的`Run workflows`，手动触发运行一次工作流程。
- 5.检查运行结果，没有报错说明就是运行成功了，可以点击运行记录的列表进去查看运行的详细情况
- 6.确认telegram是否正常返回结果，如工作流程执行结束后任未有提示消息，可确认TEL_INFO是否配置错误，重新调整后再执行步骤1到5

### 定时自动运行

- 每周1跟周四9点30分触发，北京时间17点30分

  - 可以根据自己的需求调整项目运行时间，文件路径为.github/workflows/save.yaml

    ```yaml
    on:
      schedule:
        - cron: '30 9 * * 1,4'  # 每周1跟周四9点30分触发，北京时间17点30分
    ```
  

### 注意事项

- **保密性**: Secrets 是敏感信息，请确保不要将它们泄露到公共代码库或未授权的人员。
- **更新和删除**: 如果需要更新或删除 Secrets，可以通过仓库的 Secrets 页面进行管理。

通过以上步骤，你就可以成功将代码 fork 到你的仓库下并运行它了。如果需要进一步的帮助或有其他问题，请随时告知！

import json
import os
from datetime import datetime, timezone, timedelta

import utils
from ssh import SshBase

beijing_timezone = timezone(timedelta(hours=8))

# todo 逻辑错了 应该是用常用ip去解锁，后面调整  ip解封命令 通过vps自己的ip访问官网解封地址进行解封
ipunban_command = 'bash <(curl -s https://raw.githubusercontent.com/marzzd/serv00-ct8-save/main/ipunban.sh)'

def ssh_connections(infos):
    flags = []
    fail_msgs = []
    success_msgs = []
    script_msgs = []
    hostnames = ' '.join([urlparse(item['ssh_url']).hostname for item in infos])
    for info in infos:
        ssh_url = info['ssh_url']
        bak_url = info['panel_url']
        username = info['username']
        password = info['password']
        script = info['script']
        ssh = None
        try:
            ssh = SshBase(ssh_url, bak_url, username, password)
            # 只需要解锁其他域名即可，本地意义不大
            ssh_hostname = urlparse(ssh_url).hostname
            exit_status, output, errors = ssh.exec(f'{ipunban_command} {hostnames.replace(ssh_hostname, "")}')
            if exit_status == 0:
                flags.append(1)
                success_msgs.append(f'{utils.get_time()} 用户：{username} 执行ssh链接成功，ip解封成功，返回内容：{output}')
            else:
                flags.append(0)
                fail_msgs.append(f'{utils.get_time()} 用户：{username} 执行ssh链接成功但ip解锁失败，原因：{errors}')
            if script is not None and script != '':
                try:
                    script_exit_status, script_output, script_errors = ssh.exec(script)
                    if script_exit_status == 0:
                        script_msgs.append(f'{utils.get_time()} 用户：{username} 执行ssh额外脚本成功，返回内容：{script_output}')
                    else:
                        script_msgs.append(
                            f'{utils.get_time()} 用户：{username} 执行ssh额外脚本失败，原因：{script_errors}')
                except Exception as e1:
                    script_msgs.append(str(e1))
        except Exception as e:
            flags.append(0)
            fail_msgs.append(str(e))
        finally:
            if ssh is not None:
                del ssh
    return len(infos), sum(flags), "\n".join(fail_msgs), "\n".join(success_msgs), "\n".join(script_msgs)


def accounts_login(infos):
    flags = []
    fail_msgs = []
    success_msgs = []
    for info in infos:
        panel_url = info['panel_url']
        username = info['username']
        password = info['password']
        result_flag, result_msg = account_login(panel_url, username, password)
        flags.append(result_flag)
        if result_flag == 0:
            fail_msgs.append(result_msg)
        else:
            success_msgs.append(result_msg)
    return len(infos), sum(flags), "\n".join(fail_msgs), "\n".join(success_msgs)


def account_login(url, username, password):
    # 访问登录页
    user_agent = utils.get_useragent()
    now_time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')
    if username is None or username == '' or password is None and password == '':
        return 0, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 失败，原因：用户名或密码为空"
    new_url = utils.domain_url(url)
    if url is None or url == '' or new_url is None:
        return 0, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 失败，原因：后台地址格式错误"

    panel_url = f'https://{new_url}/login/?next=/'
    try:
        response = utils.request({'User-Agent': user_agent}, {}, 'get', panel_url)
        page_content = response.text
        csrf_match = utils.re_value(page_content, r'name="csrfmiddlewaretoken" value="([^"]*)"', '', 1)
        initial_cookies = response.headers.get('set-cookie') or ''
        # 登录请求
        login_response = utils.request({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': panel_url,
            'User-Agent': user_agent,
            'Cookie': initial_cookies,
        }, {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_match,
            'next': '/'
        }, 'post', panel_url, timeout=180, is_redirect=False)
        status_code = login_response.status_code
        login_response_body = login_response.text
        if status_code == 302 and login_response.headers.get('location') == '/':
            login_cookies = login_response.headers.get('set-cookie') or ''
            all_cookies = utils.combine_cookies(initial_cookies, login_cookies)
            new_panel_url = f'https://{new_url}?next=/'
            dashboard_response = utils.request({'Cookie': all_cookies, 'User-Agent': user_agent}, {}, 'get',
                                               new_panel_url)
            dashboard_content = dashboard_response.text
            if 'href="/logout/"' in dashboard_content or 'href="/wyloguj/"' in dashboard_content:
                return 1, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 成功"
            else:
                return 0, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} ，可能失败，原因：未找到登出链接"
        elif 'Nieprawidłowy login lub hasło' in login_response_body:
            return 0, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 失败，原因：用户名或密码错误"
        else:
            return 0, f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 失败，原因未知，请检查用户名和密码是否正确"

    except Exception as e:
        result = f"管理后台用户: {username} 于北京时间: {now_time} 登录: {url} 失败，原因：登录时出现错误 {str(e)}"
        return 0, result


def tel_push(info, message):
    url = f"https://api.telegram.org/bot{info['tel_bot_token']}/sendMessage"
    data = {
        'chat_id': info['tel_chat_id'],
        'text': message,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    # 指定application/json 则传入的data需要转换为json对象
    utils.request(headers, json.dumps(data), 'post', url)


save_infos = json.loads(os.getenv('SAVE_INFO', '[]'))
tel_info = json.loads(os.getenv('TEL_INFO', '{}'))

ssh_num, ssh_succe_num, ssh_fail_msgs, ssh_success_msgs, ssh_script_msgs = ssh_connections(save_infos)
tel_push(tel_info, f'ssh连接结果统计:\n总账号数: {ssh_num}\n连接成功账号数: {ssh_succe_num}\n'
                   f'连接失败账号数: {ssh_num - ssh_succe_num}\n\n'
                   f'失败信息如下:\n{ssh_fail_msgs}\n\n'
                   f'成功信息如下:\n{ssh_success_msgs}\n\n'
                   f'额外脚本信息如下:\n{ssh_script_msgs}\n')

account_num, account_succe_num, account_fail_msgs, account_success_msgs = accounts_login(save_infos)
tel_push(tel_info, f'管理后台登录结果统计:\n总账号数: {account_num}\n登录成功账号数: {account_succe_num}\n'
                   f'登录失败账号数: {account_num - account_succe_num}\n\n失败信息如下:\n{account_fail_msgs}\n\n'
                   f'成功信息如下:\n{account_success_msgs}\n')

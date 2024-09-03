import random
import re
import requests
from datetime import datetime, timezone, timedelta

beijing_timezone = timezone(timedelta(hours=8))


# 根据正则获取数值
def re_value(content, pattern, def_val, group_num):
    match = re.search(pattern, content)
    if match:
        return match.group(group_num)
    return def_val


# 格式化domain域名
def domain_url(url):
    if url is None or url == '':
        return None
    # 使用正则表达式提取域名部分
    pattern = re.compile(r'(https?://)?([^/]+)')
    match = pattern.search(url)
    if match:
        # 提取域名
        return match.group(2)
    else:
        return None


# 获取北京时间
def get_time():
    return f"北京时间:{datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')}"


# 获取随机浏览器代理
def get_useragent():
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
    browser = browsers[random.randint(0, len(browsers) - 1)]
    version = random.randint(0, 100)
    fake_os = ['Windows NT 10.0', 'Macintosh', 'X11']
    selected_os = fake_os[random.randint(0, len(fake_os) - 1)]
    os_version = 'Win64; x64'
    if selected_os == 'X11':
        os_version = 'Linux x86_64'
    elif selected_os == 'Macintosh':
        os_version = 'Intel Mac OS X 10_15_7'
    return f'Mozilla/5.0 ({selected_os}; {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version}.0.0.0 Safari/537.36'


# is_redirect表示是否处理重定向 默认是处理
def request(headers, data, method, url, timeout=120.0, is_redirect=True):
    try:
        response = requests.request(method=method, url=url, data=data, headers=headers, allow_redirects=is_redirect,
                                    timeout=timeout)
        return response
    except Exception as e:
        return None


# 整合cookies
def combine_cookies(cookies1: str, cookies2: str) -> str:
    cookie_map = {}
    def parse_cookies(cookie_string: str):
        # 将 cookies 字符串分割成多个 cookie
        for cookie in cookie_string.split(','):
            # 分割 cookie 字符串以获取 name 和 value
            parts = cookie.strip().split(';')
            if '=' in parts[0]:
                name, value = parts[0].split('=', 1)
                cookie_map[name.strip()] = value.strip()

    # 解析两个 cookie 字符串
    parse_cookies(cookies1)
    parse_cookies(cookies2)

    # 将合并后的 cookies 转换为字符串
    combined_cookies = '; '.join(f'{name}={value}' for name, value in cookie_map.items())
    return combined_cookies
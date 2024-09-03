import paramiko

import utils


# ssh类
class SshBase:
    def __init__(self, url, bak_url, username, password):
        self.username = username
        self.password = password
        if url is None or url == '' or username is None or username == '' or password is None and password == '':
            raise Exception(f'{utils.get_time()} 用户：{self.username} 构建ssh连接失败，原因：ssh地址，用户名或密码为空')
        ssh_url = utils.domain_url(url)
        if ssh_url is None:
            raise Exception(f'{utils.get_time()} 用户：{self.username} 构建ssh连接失败，原因：ssh地址格式错误')
        self.ssh_url = ssh_url
        try:
            # ssh登录
            self.__connect__(ssh_url, username, password)
        except Exception as e:
            # 有时候官方提供的ssh地址会连接不上，可使用panel地址进行连接
            try:
                bak_ssh_url = utils.domain_url(bak_url)
                if bak_url is not None and bak_ssh_url is not None:
                    self.__connect__(bak_ssh_url, username, password)
                    return
                raise Exception(f'{utils.get_time()} 用户：{self.username} 构建ssh连接失败，原因：{str(e)}')
            except Exception as e2:
                raise Exception(f'{utils.get_time()} 用户：{self.username} 构建ssh连接失败，原因：{str(e2)}')

    def __connect__(self, url, username, password):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh登录
            self.ssh.connect(hostname=url, port=22, username=username, password=password)
        except Exception as e:
            raise Exception(f'{utils.get_time()} 用户：{self.username} 构建ssh连接失败，原因：{str(e)}')

    # 对象销毁时关闭ssh连接 通过"del 对象名"来销毁
    def __del__(self):
        if self.ssh is not None:
            self.ssh.close()

    # 执行命令 返回码(0表示正常执行，非0表示存在错误)，返回内容，错误内容
    def exec(self, command):
        if self.ssh is None:
            raise Exception(f'{utils.get_time()} 用户：{self.username} 执行ssh命令失败，原因：缺少有效的ssh连接')
        try:
            # 执行命令
            stdin, stdout, stderr = self.ssh.exec_command(command)
            # 获取命令执行的标准输出与标准错误
            output = stdout.read().decode('utf-8')
            errors = stderr.read().decode('utf-8')
            # 获取命令的返回码
            exit_status = stdout.channel.recv_exit_status()
            return exit_status, output, errors
        except Exception as e:
            raise Exception(f'{utils.get_time()} 用户：{self.username} 执行ssh命令失败，原因：{str(e)}')

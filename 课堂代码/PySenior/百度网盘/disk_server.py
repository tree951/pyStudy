from socket import *
import struct
import os


class Server:
    def __init__(self, ip, port):
        """
        服务器初始化
        :param ip:
        :param port:
        """
        self.listenSocket: socket = None
        self.ip = ip
        self.port = port

    def tcp_init(self):
        """
        建立tcp连接
        :return:
        """
        self.listenSocket = socket(AF_INET, SOCK_STREAM)
        self.listenSocket.bind((self.ip, self.port))
        self.listenSocket.listen(128)

    def task(self):
        cs_socket, client_addr = self.listenSocket.accept()
        user = User(cs_socket)
        user.handle_command()


FILE_PROTOCAL_SIZE = 4


class User:
    def __init__(self, cs_socket):
        self.cs_socket: socket = cs_socket
        self.user_name = None
        # 获取用户当前路径
        self.path = os.getcwd()

    def handle_command(self):
        while True:
            command = self.transmission_recv_handle().decode('utf8')
            if command[:2] == 'ls':
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd(command)
            elif command[:3] == 'pwd':
                self.do_pwd()
            elif command[:2] == 'rm':
                self.do_rm(command)
            elif command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            else:
                print('wrong command')

    def transmission_send_handle(self, send_bytes):
        recv_head = struct.pack('I', len(send_bytes))
        self.cs_socket.send(recv_head + send_bytes)

    def transmission_recv_handle(self):
        recv_head = self.cs_socket.recv(FILE_PROTOCAL_SIZE)
        train_content = struct.unpack('I', recv_head)
        return self.cs_socket.recv(train_content[0])

    def do_ls(self):
        data = ''
        for file in os.listdir(self.path):
            data += file + ' ' * 5 + str(os.stat(file).st_size) + '\n'
        self.transmission_send_handle(data.encode('utf8'))

    def do_cd(self, command):
        path = command.split()[1]
        os.chdir(path)
        self.path = os.getcwd()
        self.transmission_send_handle((self.path.encode('utf8')))

    def do_pwd(self):
        self.transmission_send_handle(self.path.encode('utf8'))

    def do_rm(self, command):
        pass

    def do_gets(self, command):
        """
        下载文件
        先发文件名，及头部
        告诉文件大小，C完整接收
        循环发送文件内容
        :param command:
        :return:
        """
        filename = command.split()[1]
        file_size = os.stat(filename).st_size
        self.cs_socket.send(struct.pack('I', file_size))
        with open(filename, 'rb') as f:
            while True:
                file_content = f.read(1000)
                if file_content:
                    self.cs_socket.send(file_content)
                else:
                    break
            f.close()
            # socket 关闭？

    def do_puts(self, command):
        filename = command.split()[1]
        file_content_size = self.cs_socket.recv(4)
        filesize = struct.unpack('I', file_content_size)
        total = 0
        with open("下载" + filename, 'wb')as f:
            while total <= filesize[0]:
                data = self.cs_socket.recv(1000)
                f.write(data)
                total += len(data)
                print('\r %5.2f%s' % (total / filesize[0] * 100, '%'), end='')
            print('\r100.00%')
        f.close()


if __name__ == '__main__':
    Server = Server('', 4001)
    Server.tcp_init()
    Server.task()

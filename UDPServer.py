import socket
import struct
import time
import random
import threading

class UDPServer:
    def __init__(self, host_ip, host_port, loss_rate=0.3):
        """
        UDP服务器类，用于接收客户端请求并响应
        参数:
            host_ip (str): 服务器IP地址
            host_port (int): 服务器端口号
            loss_rate (float): 模拟丢包率，默认为0.3
        """
        self.host_ip = host_ip
        self.host_port = host_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host_ip, self.host_port))
        self.loss_rate = loss_rate  # 丢包率

    def connect(self, data, client_address):
        """
        模拟TCP连接建立过程
        参数:
            data (bytes): 客户端发送的数据
            client_address (tuple): 客户端地址和端口号

        返回值:
            bool: 连接是否建立成功
        """
        type = struct.unpack('!H', data[:2])[0]
        if type == 1:  # SYN
            response = struct.pack('!H', 2)  # SYN-ACK
            self.server_socket.sendto(response, client_address)
            data, client_address = self.server_socket.recvfrom(1024)
            type = struct.unpack('!H', data[:2])[0]
            if type == 3:  # ACK
                print(f"\n与客户端 {client_address} 建立连接")
                return True
        return False

    def handle_client(self):
        """
        处理客户端请求的线程函数
        """
        while True:
            message, client_address = self.server_socket.recvfrom(1024)
            type = struct.unpack('!H', message[:2])[0]
            if type == 5:  # 数据传输
                seq_no, version, length = struct.unpack('!HBI', message[2:9])
                data = struct.unpack(f'{length}s', message[9:])[0].decode('utf-8')
                print(f"\n从客户端 {client_address} 接收到: 序号: {seq_no}, 版本: {version}, 数据：{data}")

                if random.random() > self.loss_rate:
                    current_time = time.strftime('%H-%M-%S', time.localtime()).encode()
                    response = struct.pack('!HHB8s', 6, seq_no, version, current_time)  # 数据响应
                    self.server_socket.sendto(response, client_address)
                    print(f"响应客户端 {client_address}: 序号: {seq_no}, 服务器时间: {current_time.decode()}")
                else:
                    print(f"模拟丢包，序号: {seq_no}")
            elif type == 7:  # FIN
                response = struct.pack('!H', 8)  # FIN-ACK
                self.server_socket.sendto(response, client_address)
                print(f"\n与客户端 {client_address} 断开连接")
                break

    def run(self):
        """
        服务器运行函数，接收客户端连接并创建线程处理请求
        """
        print(f"服务器运行在 {self.host_ip}:{self.host_port}")
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            if self.connect(data, client_address):  # 建立连接
                client_thread = threading.Thread(target=self.handle_client)
                client_thread.start()

if __name__ == '__main__':
    server = UDPServer('127.0.0.1', 9999)
    server.run()

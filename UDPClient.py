import socket
import time
import struct
import sys
import statistics


class UDPClient:
    def __init__(self, server_ip, server_port):
        """
        UDP客户端类，用于与服务器进行通信

        参数:
            server_ip (str): 服务器IP地址
            server_port (int): 服务器端口号
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(0.1)  # 设置超时时间为100ms
        self.sequence_number = 1  # 初始序列号
        self.version = 2
        self.received_packets = 0  # 接收的数据包数量
        self.rtt_list = []  # 存储 RTT 的列表
        self.start_time = None
        self.end_time = None
        self.total_send = 12  # 发送的总数

    def build_message(self, type, seq_no=None, version=2):
        """
        构建UDP报文消息

        参数:
            type (int): 报文类型
            seq_no (int): 序列号
            version (int): 版本号

        返回值:
            bytes: 构建的UDP报文消息
        """
        message = None
        if type == 1:  # SYN
            message = struct.pack('!H', type)
        elif type == 3:  # ACK
            message = struct.pack('!H', type)
        elif type == 5:  # 数据请求
            data = '221002207'.encode('utf-8')  # 示例数据
            length = len(data)
            message = struct.pack(f'!HHBI{length}s', type, seq_no, version, length, data)
        elif type == 7:  # FIN
            message = struct.pack('!H', type)
        elif type == 9:  # FIN-ACK
            message = struct.pack('!H', type)
        return message

    def send_message(self, type, seq_no=None, version=2):
        """
        发送UDP消息和接受回复，并计算RTT

        参数:
            type (int): 报文类型
            seq_no (int): 序列号
            version (int): 版本号

        返回值:
            tuple: (回复消息, RTT)
        """
        message = self.build_message(type, seq_no, version)
        attempts = 0
        while attempts < 3:
            self.client_socket.sendto(message, (self.server_ip, self.server_port))
            start = time.time()  # 记录发送消息的起始时间
            try:
                response, _ = self.client_socket.recvfrom(1024)
                rtt = (time.time() - start) * 1000  # 计算RTT
                if type == 5:
                    self.received_packets += 1
                    self.rtt_list.append(rtt)
                return response, rtt
            except socket.timeout:
                attempts += 1
        return None, None

    def connect(self):
        """
        建立连接，模拟TCP三次握手

        返回值:
            bool: 连接是否成功建立
        """
        response, _ = self.send_message(1)
        if response and struct.unpack('!H', response)[0] == 2:  # 接收SYN-ACK
            self.client_socket.sendto(self.build_message(3), (self.server_ip, self.server_port))  # 发送ACK
            print(f"与服务器 {self.server_ip}:{self.server_port} 建立连接\n")
            return True
        return False

    def disconnect(self):
        """
        断开连接，模拟TCP四次挥手
        """
        response, _ = self.send_message(7)
        if response and struct.unpack('!H', response)[0] == 8:  # 接收FIN-ACK
            response, _ = self.client_socket.recvfrom(1024)
            message = self.build_message(9)  # 发送FIN-ACK
            self.client_socket.sendto(message, (self.server_ip, self.server_port))
            print(f"\n与服务器 {self.server_ip}:{self.server_port} 断开连接")
        else:
            print("\n模拟TCP四次挥手断开连接失败，未收到服务器的确认")

    def run(self):
        """
        客户端运行主逻辑
        """
        if self.connect():  # 建立连接
            self.start_time = time.time()
            for _ in range(self.total_send):
                response, rtt = self.send_message(5, self.sequence_number, self.version)  # 发送数据请求
                if response:
                    msg_type, seq_no, version, server_time = struct.unpack('!HHB8s', response)
                    print(
                        f"序号: {self.sequence_number}, 服务器IP: {self.server_ip}:{self.server_port}, RTT: {rtt:.2f}ms, 服务器时间: {server_time.decode().strip()}")
                else:
                    print(f"序号: {self.sequence_number}, 请求超时")
                self.sequence_number += 1
            self.end_time = time.time()
            self.print_summary()  # 打印汇总信息
            self.disconnect()  # 断开连接
        else:
            print("无法与服务器建立连接")

    def print_summary(self):
        """
        打印汇总信息
        """
        total_sent = self.total_send
        loss_rate = ((total_sent - self.received_packets) / total_sent) * 100  # 计算丢包率
        if self.rtt_list:
            max_rtt = max(self.rtt_list)
            min_rtt = min(self.rtt_list)
            avg_rtt = sum(self.rtt_list) / len(self.rtt_list)
            stddev_rtt = statistics.stdev(self.rtt_list)  # 计算RTT标准差
        else:
            max_rtt = min_rtt = avg_rtt = stddev_rtt = 0

        total_time = self.end_time - self.start_time  # 计算总体响应时间
        print("\n汇总信息:")
        print(f"接收到的报文数: {self.received_packets}")
        print(f"丢包率: {loss_rate:.2f}%")
        print(
            f"最大 RTT: {max_rtt:.2f}ms, 最小 RTT: {min_rtt:.2f}ms, 平均 RTT: {avg_rtt:.2f}ms, RTT 标准差: {stddev_rtt:.2f}ms")
        print(f"服务器响应总时间: {total_time:.2f}s")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python UDPClient.py <server_ip> <server_port>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client = UDPClient(server_ip, server_port)
    client.run()

UDP 服务端程序运行说明文档
运行环境：
Python 3.x
配置选项：
host_ip: 服务器监听的 IP 地址。
host_port: 服务器监听的端口号。
loss_rate: 模拟丢包率，范围为0到1，默认为0.3。
使用方法：
在命令行中执行以下命令启动服务端：
php
复制代码
python UDPServer.py <host_ip> <host_port>
<host_ip>: 服务器监听的 IP 地址。
<host_port>: 服务器监听的端口号。
注意事项：
确保在运行服务端之前，已经正确安装了 Python 3.x 环境。
确保端口号没有被其他程序占用。
UDP 客户端程序运行说明文档
运行环境：
Python 3.x
配置选项：
server_ip: 服务器的 IP 地址。
server_port: 服务器的端口号。
使用方法：
在命令行中执行以下命令启动客户端：
php
复制代码
python UDPClient.py <server_ip> <server_port>
<server_ip>: 服务器的 IP 地址。
<server_port>: 服务器的端口号。
注意事项：
确保在运行客户端之前，已经正确安装了 Python 3.x 环境。
确保指定的服务器 IP 地址和端口号正确，并且服务器程序已经在运行。
该客户端程序会发送 12 个请求数据包到服务器，然后等待服务器的响应。
#Maciej Kucab
#Proxy TCP

import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print(f"[!] Failed to listen on {local_host}:{local_port}")
        print(f"[!] Check for other services using the port")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"[-->] Received connection from {addr[0]}:{addr[1]}")

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def hexdump(src, length=16):
    result = []
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join([f"{x:02X}" for x in s])
        text = ''.join([chr(x) if 0x20 <= ord(x) < 0x7F else '.' for x in s])
        result.append(f"{i:04X}  {hexa:<{length*3}}  {text}")
    print('\n'.join(result))

def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print(f"[<--] Sending {len(remote_buffer)} bytes to localhost")
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[-->] Received {len(local_buffer)} bytes from localhost")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[-->] Sent to remote host")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<--] Received {len(remote_buffer)} bytes from remote host")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<--] Sent to localhost")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break

def main():
    if len(sys.argv[1:]) != 5:
        print("Python proxy client. Usage: ")
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]\nExample: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        print("Then use anther teminal to connect to such proxy, for example nc 127.0.0.1 9000 and see if it works!")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() in ['true', '1', 'yes']

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()


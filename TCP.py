#Maciej Kucab
#Prosty program ktory wysyla rzadanie get na odpowiedniego hosta
#Zadanie -- sprobuj przepisac ten kod tak, aby:
#1. wysylal dodatkowo cos hostowi 
#2. mial mozliwosc wyslania requesta na dowolny port
#2,a czyli sys.argv != 3 i drugim argumentem jest port

import socket
import sys
import ssl

def GET_http(host,port):
    try:

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port == 443:
            client = ssl.wrap_socket(client)
        client.connect((host,port))

        client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

        response = client.recv(4096)
        print(f"Response from {host} on port {port} :")
        print(response.decode('utf-8'))

    except Exception as e:
        print("Error: Failed to connect to {host} on port {port}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Simple TCP client, usage: python TCP.py http://example.com OR https://example2.io")
        sys.exit(1)

    url = sys.argv[1]
    if url.startswith("http://"):
        url = url[7:]
        GET_http(url,80)
    elif url.startswith("https://"):
        url = url[8:]
        GET_http(url,443)


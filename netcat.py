import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("Python listener, usage: ")
    print("python netcat.py -t <host> -p <port>")
    print(" additional flags: (none for now) ")
    print("-l --listen to listen on host:port")
    print("-e --execute=<file> executes given file when connection is established")
    print("-c --command initializes a command shell")
    print("-u --upload=<dest> uploads file and writes to <dest> when connection is established")
    print("Example : python netcat.py -t 192.168.0.1 -p 4444 -l -c")
    print("")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help","listen","execute","target","port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-t", "--target"):
            target = a
        else:
            raise ValueError("There is something very wrong")

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

def client_sender(buffer):
    global target
    global port
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode('utf-8'))
            print("Connection established, waiting for the data")

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096).decode('utf-8')
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response, end='')

            buffer = input("")
            buffer += "\n"
            client.send(buffer.encode('utf-8'))

    except Exception as e:
        print(f"An error has occurred: {e}")
        client.close()

def server_loop():
    global target
    global port

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = b"Failed to execute the command.\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = b""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            with open(upload_destination, "wb") as file_descriptor:
                file_descriptor.write(file_buffer)
            client_socket.send(f"Success! File saved to {upload_destination}\r\n".encode('utf-8'))
        except:
            client_socket.send(f"Failed to save file to {upload_destination}\r\n".encode('utf-8'))

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send(b"Shell:#> ")
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer.decode('utf-8'))
            client_socket.send(response)

if __name__ == "__main__":
    main()


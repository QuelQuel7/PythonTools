#Maciej Kucab, prosty listener w pythonie 


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
    print("Example : python listener.py -t 192.168.0.1 -p 4444 -l -c")
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
#UWAGA -- proba przeparsowania inputu, przyda sie do innych programow 
    try: 
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help","listen","execute","target","port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o,a in opts: 
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
            raise ValueError(f"There is something very wrong")

#Tylko wysylanie danych
    if not listen and len(target) and port > 0: 
        buffer = sys.stdin.read()
        client_sender(buffer) #to trzeba zdefiniowac
#Nasluch
    if listen: 
        server_loop() # To trzeba zdefiniowac

def client_sender(buffer): 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
            print("connection established, waiting for the data")
        while True: 
            recv_len =1 
            response = ""
            while recv_len: 
                data = client_recv(4096)
                recv_len = len(data)
                response+= data
                if recv_len<4096: 
                    break

            print(f"{response}")
            buffer = raw_input("")
            buffer+= "\n"
            client.send(buffer)

    except: 
        print("An error has occured! Exiting...")
        client.close()


def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip() #to niszczy \n 
    try: 
        output = subprocess.check_output(command, stderr=subprocess,STDOUT, shell=True)
    except: 
        output = "Failed to execute the command. \r \n"
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command
    if len(upload_destination):
        file_buffer = ""
        while True: 
            data = client_socket.recv(1024)

            if not data:
                break
            else: 
                file_buffer += data 

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send("Success! file saved to %s\r\n"%upload_destination)

        except: 
            client_socket.send("Failed to save file to %s\r\n"%upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client.socket.send("Shell:#> ")
            cmd_buffer += client_socket.recv(1024)

        response = run_command(cmd_buffer)
        client_socket.send(response)

import socket , sys

def socket_open( host , port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)

    sock.bind((host,port))
    sock.listen(5)

    clientsocket , address = sock.accept()

    print("Client Info : {0} , {1}".format(clientsocket , address));

    return clientsocket

def socket_close( client ):

	client.close()


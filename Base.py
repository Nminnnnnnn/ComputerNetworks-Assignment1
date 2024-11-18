import json
import threading
import socket
from abc import abstractmethod

# the format in which encoding and decoding will occur

FORMAT = "utf-8"
BUFFER_SIZE = 2048

def get_current_IP_address():
    with open('Server_IP.txt', 'r') as file:
        server_ip = file.read().strip()
    return server_ip

class Base:
    def __init__(self, serverhost, serverport):
        # host and listening port of network peers/central server
        self.serverhost = serverhost
        self.serverport = int(serverport)
        
        # create server TCP socket (for listening)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to our local address
        self.socket.bind((self.serverhost, self.serverport))
        self.socket.listen(10)
        
        # peerlist: dict with key is peer name and value is tuple (host,port) 
        # Child class CentralServer: connected peers of a network peer
        # Child class NetworkPeer: list of registered peers managed by central server
        self.peerlist = {}
        # used for mapping from MESSAGE TYPE to corresponding function
        self.handlers = {}

    def add_handler(self, msgtype, function): 
        self.handlers[msgtype] = function

    def function_mapper(self, message):
        type_ = message['msgtype']
        data_ = message['msgdata']
        self.handlers[type_](data_)

    def recv_input_stream(self, conn):
        # receive from client 
        buf = conn.recv(BUFFER_SIZE)
        message = buf.decode(FORMAT)  
        # deserialize (json type -> python type)
        message = json.loads(message)
        # map into function
        self.function_mapper(message)

    def input_recv(self):
        while True:
            # wait until receive a connection request -> return socket for connection from client
            conn, addr = self.socket.accept()
            input_stream = threading.Thread(target=self.recv_input_stream, args=(conn,))
            input_stream.daemon = True
            input_stream.start()

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def client_send(address, msgtype, msgdata):
        # msgtype for mapping into corresponding function
        # msgdata contains sent data
        message = {'msgtype': msgtype, 'msgdata': msgdata}
        # serialize into JSON file for transmitting over network
        message = json.dumps(message).encode(FORMAT)
        # create client TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # request connection
            s.connect(address)
        except ConnectionRefusedError:
            print('Connection Error: Your Peer Refused')
            raise
        else:
            s.sendall(message)
        finally:
            s.close()

    # Method to announce file parts to tracker
    def announce_file_parts(self, file_name, file_size, num_parts):
        data = {
            'file_name': file_name,
            'file_size': file_size,
            'num_parts': num_parts,
            'peer': f"{self.serverhost}:{self.serverport}"
        }
        self.client_send((self.serverhost, self.serverport), 'announce_file', data)

    # Method to get peers with file parts
    def get_peers_with_parts(self, file_name):
        data = {'file_name': file_name}
        return self.client_send((self.serverhost, self.serverport), 'get_peers_with_parts', data)

    # Method to download file parts from peer
    def download_file_parts(self, peer, file_name, part_index):
        data = {'file_name': file_name, 'part_index': part_index}
        self.client_send((peer[0], peer[1]), 'download_file_part', data)

#!/bin/python3
import socket
import threading


class ClientsList:
    def __init__(self):
        self.counter = 0
        self.list = []

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter < len(self.list):
            item = self.list[self.counter]
            self.counter += 1
            return item
        else:
            self.counter = 0
            raise StopIteration()

    def add_client(self, client):
        client.my_private_chat = self
        self.list.append(client)

    def remove_client(self, client):
        self.list.remove(client)

    def get_client(self, nick):
        for client in self.list:
            print(client.get_nickname)
            if client.get_nickname == nick:
                return client


class PrivateChat:
    def __init__(self):
        self.__clients = ClientsList()

    def add_client(self, client):
        self.__clients.add_client(client)
        client.in_private_chat = True
        client.my_private_chat = self

    def send_my_data(self, message):
        for client in self.__clients:
            client.send_my_data(message)


class MyClient:
    def __init__(self):
        self.__address = None
        self.__nickname = None
        self.__connection = None
        self.in_private_chat = False
        self.my_private_chat = PrivateChat()

    def set_nickname(self, nickname):
        self.__nickname = nickname

    def get_nickname(self):
        return self.__nickname

    def set_connection(self, connection):
        self.__connection = connection[0]
        self.__address = connection[1]

    def get_connection(self):
        return self.__connection

    def close_connection(self):
        self.get_connection().close()

    def get_address(self):
        return self.__address

    def receive(self):
        data = self.__connection.recv(1024).decode('UTF-8')
        return data

    def send_my_data(self, message):
        self.__connection.send(message.encode('UTF-8'))


# Connection Data
host = '192.168.88.212'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = ClientsList()


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send_my_data(message)


# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.receive()
            print(message)
            if message.split(" ")[1] == 'chatwith':
                opponent_nick = message.split(" ")[2]
                opponent = clients.get_client(opponent_nick)
                print(opponent_nick)
                print(opponent)
                if opponent != None:
                    print("{} and {} in private chat".format(client.get_nickname, opponent.get_nickname))
                    client.my_private_chat.add_client(client)
                    client.my_private_chat.add_client(opponent)

            if client.in_private_chat:
                client.my_private_chat.send_my_data(message)
            else:
                broadcast(message)
        except:
            # Removing And Closing Clients
            client.close_connection()
            clients.remove_client(client)
            broadcast('{} left!'.format(client.get_nickname()))
            break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client = MyClient()
        client.set_connection(server.accept())
        print("Connected with {}".format(str(client.get_address())))
        # Request And Store Nickname
        client.send_my_data('NICK')
        client.set_nickname(client.receive())
        # clients_list.add_client(client)
        clients.add_client(client)
        # Print And Broadcast Nickname
        print("Nickname is {}".format(client.get_nickname()))

        broadcast("{} joined!".format(client.get_nickname()))
        client.send_my_data('Connected to server!')

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server if listening...")
receive()

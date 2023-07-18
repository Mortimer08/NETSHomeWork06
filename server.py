#!/bin/python3
import socket
import threading


class CommandParcer:
    def get_command(self, message: str):
        if " " in message:
            return message.split(" ")[1]

    def get_attr(self, message: str):
        if message.count(" ") > 1:
            return message.split(" ")[2]


class MyClient:
    def __init__(self):
        self.__address = None
        self.__nickname = None
        self.__connection = None
        self.in_private_chat = False
        self.my_private_chat = PrivateChat()

    def set_nickname(self, nickname: str):
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

    def send_my_data(self, message: str):
        self.__connection.send(message.encode('UTF-8'))


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

    def add_client(self, client: MyClient):
        self.list.append(client)

    def remove_client(self, client: MyClient):
        self.list.remove(client)

    def get_client(self, nick: str):
        for client in self:
            if client.get_nickname() == nick:
                return client


class PrivateChat:
    def __init__(self):
        self.__clients = ClientsList()

    def add_client(self, client: MyClient):
        self.__clients.add_client(client)
        client.in_private_chat = True
        client.my_private_chat = self

    def send_my_data(self, message):
        for client in self.__clients:
            client.send_my_data(message)

    def delete_client(self, client: MyClient):
        self.__clients.remove_client(client)
        client.in_private_chat = False
        # client.my_private_chat = None


# Connection Data
host = '192.168.88.212'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = ClientsList()
command_parcer = CommandParcer()


# Sending Messages To All Connected Clients
def broadcast(message: str):
    for client in clients:
        if (not client.in_private_chat):
            client.send_my_data(message)


# Handling Messages From Clients
def handle(client: MyClient):
    while True:
        try:
            # Broadcasting Messages
            message = client.receive()
            command = command_parcer.get_command(message)
            attribute = command_parcer.get_attr(message)
            if command == 'chatwith':
                opponent_nick = attribute
                opponent = clients.get_client(opponent_nick)
                if opponent != None:
                    print("{} and {} in private chat".format(client.get_nickname(), opponent.get_nickname()))
                    client.my_private_chat.add_client(client)
                    opponent.my_private_chat = client.my_private_chat
                    client.my_private_chat.add_client(opponent)
            if command == 'exit':
                if client.in_private_chat:
                    client.my_private_chat.send_my_data("{} exit chat".format(client.get_nickname()))
                    client.my_private_chat.delete_client(client)
                else:
                    client.close_connection()
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

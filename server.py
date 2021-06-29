import socket
import select
import json
import ast

lobbies = []

HEADER_LENGTH = 512
#Database values are placeholders until an actual server is set-up 
databsePull = 'C:/Users/Cinder/Documents/Mooncade/Database/Files/users.json'
databasePush = 'C:/Users/Cinder/Documents/Mooncade/Database/Files/user.json'

IP = "127.0.0.1"
PORT = 3000

#Kept this here for reusage. Honestly not really needed anymore. I'll kill this another day. Dont worry about it
#######################################################
def receive_message(client_socket):
    try:
        recvDict_header = client_socket.recv(HEADER_LENGTH)
        if not len(recvDict_header):
            print("Fuck")
            return False
        recvLength = int(recvDict_header.decode('utf-8').strip())
        recvDict = client_socket.recv(recvLength).decode('utf-8')
        returnDict = ast.literal_eval(recvDict)
    except:
        return False
    return returnDict

def verifyUser(client_socket):
    print("Verifying...")
    #RSA. Oh no.




#This is triggered when an incoming connection wants to create a lobby
#######################################################
def lobbyCreate(client_socket, recvDict):

    #Stores the new lobby in a dict value
    newLobby = {
        "lobbyID": str(len(lobbies)),
        "params": {
            "con1": [client_socket, recvDict['ID']],
            "gameMode": recvDict['gameMode'],
            "betAmount": recvDict['betAmount']
        }
    }

    #Adds the new dict value to an existing list
    lobbies.append(newLobby)

    return None

#Joins lobby. WIll retrieve ID and lobby to join. Currently bugged so that you can join a lobby that doesnt exist
#######################################################
def lobbyJoin(client_socket, recvDict):

    for i in lobbies:
        if i['lobbyID'] == recvDict['lobbyJID']:
            i['params']['con2'] = [client_socket, recvDict['ID']],
            lobbyRPS(i)
            lobbies.remove(i)
            return None

        print("Lobby not found")
    return None
  
#Take a guess 
#######################################################
def calculateResults(playerOne, playerTwo):
    print("Calculating winner")
    if(playerOne == playerTwo):
        return '-1'
    elif(playerOne == '1' and playerTwo == '2'):
        return '1'
    elif(playerOne == '1' and playerTwo == '3'):
        return '0'
    elif(playerOne == '2' and playerTwo == '1'):
        return '0'
    elif(playerOne == '2' and playerTwo == '3'):
        return '1'
    elif(playerOne == '3' and playerTwo == '1'):
        return '1'
    elif(playerOne == '3' and playerTwo == '2'):
        return '0'
    else:
        return '2'

 #RPS Lobby server side         

#RPS server side lobby. It works for now
#######################################################
def lobbyRPS(lobby):
    loopCount = 0
    loopContinue = 1

    playerOne = lobby['params']['con1'][0]
    #Player two is being stored as an array inside of a tuple. Dont know how to fix it right now. Works though so, fuck it
    playerTwo = lobby['params']['con2'][0][0]
    print("\n", playerTwo)

    message = "Welcome to rock paper scissors!".encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    
    while loopContinue == 1:
        if loopCount == 0:
            playerOne.send(message_header + message)
        playerOneResponse_header = playerOne.recv(HEADER_LENGTH)
        if not len(playerOneResponse_header):
            #Player one dc'd. Player two wins
            return False
        playerOneResponse_length = int(playerOneResponse_header.decode('utf-8'))
        playerOneResponse = playerOne.recv(playerOneResponse_length).decode('utf-8')

        if loopCount == 0:
            playerTwo.send(message_header + message)
        playerTwoResponse_header = playerTwo.recv(HEADER_LENGTH)
        if not len(playerTwoResponse_header):
            #Player two dc'd. Player one wins
            return False
        playerTwoResponse_length = int(playerTwoResponse_header.decode('utf-8'))
        playerTwoResponse = playerTwo.recv(playerTwoResponse_length).decode('utf-8')

        loopCount = loopCount + 1

        results = calculateResults(playerOneResponse, playerTwoResponse)

        if results == '-1':
            message = "Tie! Go again...".encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            #Tie
            #Loop again
        elif results == '0':
            message = "Player one wins!".encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            loopContinue = 0
            #P1
            #Kill loop
        elif results == '1':
            message = "Player two wins!".encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            loopContinue = 0
            #P2
            #Kill loop
        elif results == '2':
            message = "One or more invalid entries. Go again...".encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

        playerOne.send(message_header + message)
        playerTwo.send(message_header + message)

        results = results.encode('utf-8')
        results_header = f"{len(results):<{HEADER_LENGTH}}".encode('utf-8')
        
        playerOne.send(results_header + results)
        playerTwo.send(results_header + results)

        winnerAlter(int(lobby['params']['con1'][1]), int(lobby['params']['con2'][0][1]), int(lobby['params']['betAmount']))

    return None

#Take a guess. Based solely on the good graces of someone not signing in on other than their own ID. Will need ***SESSIONS*** 
#######################################################
def checkAmount(client_socket, recvDict):
    
    json_file = open(databasePush, 'r')
    data = json.load(json_file)
    json_file.close()

    try:
        sendAmount = f"You have {str(data['accounts'][int(recvDict['ID'])]['amount'])} SFM"
        sendAmount = sendAmount.encode('utf-8')
        sendAmount_header = f"{len(sendAmount):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendAmount_header + sendAmount)
    except:
        sendAmount = "Your given ID was not found...".encode('utf-8')
        sendAmount_header = f"{len(sendAmount):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendAmount_header + sendAmount)


    return None

#Checks available games
#######################################################
def checkGames(client_socket):
    if len(lobbies) == 0:
        response                 = "Yeah nah, mate".encode('utf-8')
        response_header          = f"{len(response):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(response_header + response)
        return None
    else:
        length = f"{len(lobbies)}".encode('utf-8')
        length_header = f"{len(length):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(length_header + length)


    for i in lobbies:
        response = f"LobbyID: {i['lobbyID']}\nGamemode: {i['params']['gameMode']}\nAmount bet: {i['params']['betAmount']}".encode('utf-8')
        response_header     = f"{len(response):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(response_header + response)

    return None


#Changes the stored data. Currently pulls from a clean file then stores on a new file. THat is overwritten over and over. It does not format, sadge
#######################################################
def winnerAlter(winnerID, loserID, changeAmount):

    #Reach out to server for downlink
    json_file = open(databsePull,'r')
    data = json.load(json_file)
    json_file.close()
    ###
    #Change data
    data['accounts'][3]['amount'] = data['accounts'][3]['amount'] + (changeAmount * 0.05)
    data['accounts'][winnerID]['amount'] = data['accounts'][winnerID]['amount'] + (changeAmount * 0.95) 
    data['accounts'][loserID]['amount'] = data['accounts'][loserID]['amount'] - changeAmount
    ###
    #Reach out to server for uplink
    json_file = open(databasePush, 'w')
    json.dump(data, json_file)
    json_file.close()

    return None

#Start of main!
#######################################################
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}

print(f"Listening for connections on {IP}:{PORT}...")

while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    print("test")

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            
            recvDict = receive_message(client_socket)
    
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")

            if recvDict['WTD'] == '0':
                lobbyCreate(client_socket, recvDict)
            elif recvDict['WTD'] == '1':
                lobbyJoin(client_socket, recvDict)
            elif recvDict['WTD'] == '2':
                checkAmount(client_socket, recvDict)
            elif recvDict['WTD'] == '3':
                checkGames(client_socket)
            else:
                print("Yeah, nah...")

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
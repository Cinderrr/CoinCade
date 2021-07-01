import socket
import getpass
import ast

HEADER_LENGTH = 512

IP = "127.0.0.1"
PORT = 3000

#Basic login function that takes the given ID at face value. Highly insecure. Will need to update with sessions down the line
def loginBase(client_socket):
    signChoice = input("Hello! Would you like to sign-up or sign in:\n1. Sign-Up\n2. Sign-In\n")
    if signChoice == '1':
        return loginSignUp(client_socket)
    elif signChoice == '2':
        return loginSignIn(client_socket)
    else:
        print("Invalid choice. Exiting...")
    
    return None

def loginSignIn(client_socket):
    username = input("Username: ")
    password = getpass.getpass()
    sendDict = {
        "WTD": '300',
        "username": username,
        "password": password
        }

    try:
        sendDict = str(sendDict)
        sendDict = sendDict.encode('utf-8')
        sendDict_header = f"{len(sendDict):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendDict_header + sendDict)
    except:
        print("There has been an issue sending you information. Exiting...")
        return None

    recvDict_header = client_socket.recv(HEADER_LENGTH)
    if not len(recvDict_header):
        return False
    recvLength = int(recvDict_header.decode('utf-8').strip())
    recvDict = client_socket.recv(recvLength).decode('utf-8')
    returnDict = ast.literal_eval(recvDict)

    print(returnDict)
    if returnDict['response'] == '1':
        
        return { "username": username,
                 "password": password,
                 "ID": returnDict['ID']
        }
    else:
        return '0'

def loginSignUp(client_socket):
    username = input("Username: ")
    password = getpass.getpass()
    sendDict = {
    "WTD": '301',
    "username": username,
    "password": password
    }

    try:
        sendDict = str(sendDict)
        sendDict = sendDict.encode('utf-8')
        sendDict_header = f"{len(sendDict):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendDict_header + sendDict)
    except:
        print("There has been an issue sending you information. Exiting...")
        return None

    recvDict_header = client_socket.recv(HEADER_LENGTH)
    if not len(recvDict_header):
        return False
    recvLength = int(recvDict_header.decode('utf-8').strip())
    recvDict = client_socket.recv(recvLength).decode('utf-8')
    returnDict = ast.literal_eval(recvDict)

    if returnDict['response'] == '1':
        print("Account created!")
        return '1'
    elif returnDict['response'] == '0':
        print("Account already exist!")
        return '0'
    else:
        print("There has been an issue")
        return '0'

def verifyUser(client_socket, user):
    message = str(user).encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

    recvDict_header = client_socket.recv(HEADER_LENGTH)
    if not len(recvDict_header):
        return False
    recvLength = int(recvDict_header.decode('utf-8').strip())
    returnDict = client_socket.recv(recvLength).decode('utf-8')

    print(returnDict)
    if returnDict['response'] == '1':
        return '1'
    else:
        return '0'

#Player starts a game. Will be prompted to select from Rock Paper Scissors or quiting.
def startGame(client_socket, user):

    #Prompting player for this before contacting the server side. Get everything now and send it in one quick burst of messages.
    gameMode = input("What would you like to play?\n0. Exit\n1. Rock Paper Scissors\n")

    #Self explanitory. Quiting or invalid entries will result in software exiting.
    if gameMode == '0':
        print("Exiting...")
        exit()
    elif gameMode == '1':
        print("You have chosen Rock Paper Scissors!")
    else:
        print("Invalid gamemode entered. Exiting...")
        exit()

    #Gather how much the user would like to bet. Going to need to add a function on server side to make sure that restricts users from betting more than they have
    betAmount = input("What would you like to bet?\n")

    #Invalid amount once again exits software
    try:
        if int(betAmount) > 0 :
            print("You have bet ", betAmount, " SFM")
        else:
            print("Invalid amount entered. Exiting...")
            exit()
    except:
        print("Invalid entry. Exiting...")
        exit()

    sendDict = {
        "WTD": "0",
        "gameMode": gameMode,
        "betAmount": betAmount
    }

    try:
        sendDict = str(sendDict)
        sendDict = sendDict.encode('utf-8')
        sendDict_header = f"{len(sendDict):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendDict_header + sendDict)
    except:
        print("There has been an issue sending you information. Exiting...")
        return None

    #Currently have only RPS. Will want to make this a state machine once new gamemodes are added
    clientRPS(client_socket)

def joinGame(client_socket, ID):
    #Ask the user which lobby they want to join.
    #########################################
    #Currently a bug that doesnt quit them out even if the lobby doesnt exist 
    #########################################
    lobbyID = input("What is the lobby's id: ")

    sendDict = {
        "WTD": '1',
        "ID" : ID,
        "lobbyJID": lobbyID 
    }

    try:
        sendDict = str(sendDict)
        sendDict = sendDict.encode('utf-8')
        sendDict_header = f"{len(sendDict):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendDict_header + sendDict)
    except:
        print("There has been an issue sending you information. Exiting...")
        return None

    #Player starts the game. Will need to switch to a state machine at some point.
    clientRPS(client_socket)

    return None

#Rock paper scissors. It works as far as I can tell
def clientRPS(client_socket):
    
    results = '-1'
    loopContinue = 1
    choiceRPS = -1

    print("Waiting on server...")

    message_header = client_socket.recv(HEADER_LENGTH)
    if not len(message_header):
        return False
    message_length = int(message_header.decode('utf-8'))
    message = client_socket.recv(message_length).decode('utf-8')
    print(message)

    while results == '-1' or results == '2':
        loopContinue = 1
        while loopContinue == 1:
            choiceRPS = input("Enter your choice:\n1. Rock\n2. Paper\n3. Scissors\n")
            if(choiceRPS == '1' or choiceRPS == '2' or choiceRPS == '3'):
                choiceRPS = choiceRPS.encode('utf-8')
                choiceRPS_header = f"{len(choiceRPS):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(choiceRPS_header + choiceRPS)
                loopContinue = 0
            else:
                print("Invalid choice. Go again...")
                
        
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8'))
            message = client_socket.recv(message_length).decode('utf-8')
            
            results_header = client_socket.recv(HEADER_LENGTH)
            if not len(results_header) :
                return False
            results_length = int(results_header.decode('utf-8'))
            results = client_socket.recv(results_length).decode('utf-8')
            
        if results == '-1':
            print("Tie! Go again...")
            #Tie
            #Loop again
        elif results == '0':
            print("Player one wins!")
            loopContinue = 0
            #P1
            #Kill loop
        elif results == '1':
            print("Player two wins!")
            loopContinue = 0
            #P2
            #Kill loop
        elif results == '2':
            print("One or more invalid entries. Go again...")

    return None

#This function checks the amount of money the passed ID has. Not too dangerous to have without a session, but would be QoL and protect people from phishing attacks
def checkAmount(client_socket, ID):
    
    sendDict = {
        "WTD": '2',
        "ID": ID
    }
    
    sendDict = str(sendDict)
    sendDict = sendDict.encode('utf-8')
    try:
        sendDict_header = f"{len(sendDict):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(sendDict_header + sendDict)
    except:
        print("There has been an issue retrieving you balance...")
        return None

    message_header = client_socket.recv(HEADER_LENGTH)
    if not len(message_header):
        return False
    message_length = int(message_header.decode('utf-8'))
    message = client_socket.recv(message_length).decode('utf-8')
    print(message)

    return None

#This function checks the available games there are to join. Totally safe to not have a session check as far as I can tell
def checkGames(client_socket):
    WTD = '3'
    
    try:
        WTD                 = WTD.encode('utf-8')
        WTD_header          = f"{len(WTD):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(WTD_header + WTD)

        loop_header = client_socket.recv(HEADER_LENGTH)
        if not len(loop_header):
            return False
        loop_length = int(loop_header.decode('utf-8'))
        loop = client_socket.recv(loop_length).decode('utf-8')

        try:
            loop = int(loop)
        except:
            print("No lobbies available...")
            return None
        
        for x in range(int(loop)):
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8'))
            message = client_socket.recv(message_length).decode('utf-8')
            print(message + "\n")
    except:
        print("There has been an issue retrieving available games...")

    return None

#Start of main
#############################################################
user = '0'

while user == '0':
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
    except:
        print("Connection could not be made...")
        exit()

    user = loginBase(client_socket)
    if user == '0':
        print("You connection was not accepted")
        

while True:
    WTD = input("What would you like to do: ")
    if WTD == '0':
        startGame(client_socket, user)
    elif WTD == '1':
        joinGame(client_socket, ID)
    elif WTD == '2':
        checkAmount(client_socket, ID)
    elif WTD == '3':
        checkGames(client_socket)
    else:
        print("Invalid entry... ")


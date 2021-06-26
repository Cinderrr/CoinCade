import socket

HEADER_LENGTH = 512

IP = "127.0.0.1"
PORT = 3000

#Basic login function that takes the given ID at face value. Highly insecure. Will need to update with sessions down the line
def loginID():
    ID = input("Sign in with your ID: ")
    return ID

#Player starts a game. Will be prompted to select from Rock Paper Scissors or quiting.
def startGame(client_socket, ID):
    WTD = '0'
    gameMode = '0'
    betAmount = '0'

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
    if betAmount > '0':
        print("You have bet " + betAmount + " SFM")
    else:
        print("Invalid amount entered. Exiting...")
        exit()

    #What to do. Will communicate with server what the next incoming data is. State machine or something like that.
    #Harmless if someone fucks with the code. All it'll do is error out and kill their software once exception handling is added to the server side
    WTD                 = WTD.encode('utf-8')
    WTD_header          = f"{len(WTD):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(WTD_header + WTD)

    #ID. Once again super insecure. But sessions are gonna be a thing. Then it'll be more secure
    ID                  = ID.encode('utf-8')
    ID_header           = f"{len(ID):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(ID_header + ID)

    #Gamemode. Harmless to fuck with. It'll just error out the dipshit's client side
    gameMode            = gameMode.encode('utf-8')
    gameMode_header     = f"{len(gameMode):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(gameMode_header + gameMode)

    #Amount bet. Take a guess
    betAmount           = betAmount.encode('utf-8')
    betAmount_header    = f"{len(betAmount):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(betAmount_header + betAmount)

    #Currently have only RPS. Will want to make this a state machine once new gamemodes are added
    clientRPS(client_socket)

def joinGame(client_socket, ID):
    WTD = '1'

    #Ask the user which lobby they want to join.
    #########################################
    #Currently a bug that doesnt quit them out even if the lobby doesnt exist 
    #########################################
    lobbyID = input("What is the lobby's id: ")

    #WTD. Same as startGame()
    WTD                 = WTD.encode('utf-8')
    WTD_header          = f"{len(WTD):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(WTD_header + WTD)

    #ID. Will need to change
    ID                  = ID.encode('utf-8')
    ID_header           = f"{len(ID):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(ID_header + ID)

    #LobbyID. Explained above
    lobbyID             = lobbyID.encode('utf-8')
    lobbyID_header      = f"{len(lobbyID):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(lobbyID_header + lobbyID)

    #Player starts the game. Will need to switch to a state machine at some point.
    clientRPS(client_socket)

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
            print(results)

    return None

#This function checks the amount of money the passed ID has. Not too dangerous to have without a session, but would be QoL and protect people from phishing attacks
def checkAmount(client_socket, ID):
    WTD = '2'
    
    WTD                 = WTD.encode('utf-8')
    WTD_header          = f"{len(WTD):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(WTD_header + WTD)

    sendID              = ID.encode('utf-8')
    sendID_header       = f"{len(sendID):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(sendID_header + sendID)

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

    return None


#Start of main
#############################################################
ID = loginID()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

WTD = input("What would you like to do: ")
if WTD == '0':
    startGame(client_socket, ID)
elif WTD == '1':
    joinGame(client_socket, ID)
elif WTD == '2':
    checkAmount(client_socket, ID)
elif WTD == '3':
    checkGames(client_socket)
else:
    print("Invalid entry... ")
lastSendend = [1,0,1,0]
def send(command): 
    str_command = []
    commandList = [(0, "forward"),(1, "backward"), (2, "left"), (3, "right")]
    for i,c in commandList: 
        if command[i] == 1 and lastSendend[i]==0: 
            str_command.append(f"push {c}")
        elif command[i] == 0 and lastSendend[i]==1: 
            str_command.append(f"release {c}")
    
    return str_command
print(send([0,0,0,1]))

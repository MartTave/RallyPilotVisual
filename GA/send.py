lastSendend = []
def send(command): 
    str_command = ""
    for new_command,last_command in zip(command, lastSendend): 
        if new_command[0] == 1 and last_command[0]==0: 
            str_command.append("push forward")
        elif new_command[0] == 0 and last_command[0]==1: 
            str_command.append("release forward")
        if new_command[1] == 1 and last_command[1]==0: 
            str_command.append("push backward")
        elif new_command[0] == 0 and last_command[0]==1: 
            str_command.append("release backward")
        if new_command[2] == 1 and last_command[2]==0: 
            str_command.append("push ")
        elif new_command[2] == 0 and last_command[2]==1: 
            str_command.append("release backward")

    
    return []
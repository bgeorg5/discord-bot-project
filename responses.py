import datetime
import dbconn
import random
from pymongo import MongoClient
from bson.objectid import ObjectId

def handle_response(username, nickname, message) -> str:
    
    db = dbconn.conn_to_db()["Chore-bot-db"]

    p_message = message.lower()

    print(f'message: {p_message}')

    # change to switch

    #----- main commands -----#


    #------------------------------ viewing stats ------------------------------#

    if p_message == 'view my stats':
        points = str(db.Roommate.find_one({"discordName" : str(username)})['points'])
        comp_cont = db.Roommate.find_one({"discordName" : str(username)})['completeContainer']
        incomp_cont = db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer']

        resp_msg = "--- Your current stats: --- \n Level:       "+points+"\n Tasks complete: "+str(len(comp_cont))+"\n Tasks Incomplete: "+str(len(incomp_cont))

        return resp_msg
        
    if p_message == 'view group stats':
        tRoommates = db.Roommate.find().sort("points", -1)
        tString = "--- Current stats: --- \nName          |    Level    |    Rank    |    Tasks to do\n"
        tCount = 1
        tPadding = ""

        tLastR = tRoommates[0]

        for r in tRoommates:

            if(len(str(r['roommateName'])) == 7):
                tPadding = ""
            elif(len(str(r['roommateName'])) == 6):
                tPadding = "   "
            elif(len(str(r['roommateName'])) == 5):
                tPadding = "    "
            elif(len(str(r['roommateName'])) == 4):
                tPadding = "       "

            if(str(r['roommateName']) == "Ricky" or str(r['roommateName']) == "Bridget"):
                tPadding += " "

            if(not (str(r['roommateName']) == str(tLastR['roommateName'])) and r['points'] != tLastR['points']):
                tCount += 1

            #update last r
            tLastR = r

            tString += ""+str(r['roommateName'])+tPadding+"      |        "+str(r['points'])+"        |        "+str(tCount)+"        |        "+str(len(r['incompleteContainer']))+"\n"
            
        return tString
    
    #------------------------------ end of viewing stats ------------------------------#

    #------------------------------viewing tasks ------------------------------#

    if p_message == 'view my tasks':
        return print_Indv_Tasks(db=db, username=username)
    
    if p_message == 'view group tasks':
        return print_Group_Tasks(db=db)
    
    #------------------------------ end of viewing tasks ------------------------------#




    #------------------------------ marking and unmarking chores ------------------------------#

    if p_message == 'mark chore':
        return print_Indv_Tasks(db=db, username=username)+"\n\n @ the chore-bot with the the phrase 'mark' and the number of the chore you would like to mark (ex. 'mark 1' will mark the chore listed as 1 on the list as complete). \n "
    
    if p_message == 'unmark chore':
        return print_Indv_Tasks(db=db, username=username)+"\n\n @ the chore-bot with the the phrase 'unmark' and the number of the chore you would like to unmark (ex. 'unmark 1' will unmark the chore listed as 1 on the list to show that it is incomplete). \n "

    #------------------------------ unmarking chores ------------------------------#

    # 2nd part of the prompt above, 'UNMARK chore'
    if has_word(p_message, "unmark") and has_digit(p_message=p_message):
        tStringArr = p_message.split(' ')
        tLastElement = tStringArr[len(tStringArr)-1]

        IncompCont = db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer']
        CompCont = db.Roommate.find_one({"discordName" : str(username)})['completeContainer']
        CompSize = len(db.Roommate.find_one({"discordName" : str(username)})['completeContainer'])
        InCompSize = len(db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer'])
        print(f'CompSize = {CompSize}')
        print(f'InCompSize = {InCompSize}')

        CompContItem = CompCont[int(tLastElement)-InCompSize-1]

        print(f'CompContItem = {CompContItem}')

        #get title 
        TaskTitle = db.Task.find_one({"_id" : ObjectId(CompContItem)})['title']

        #update complete and incomplete containers
        CompCont.remove(CompContItem)
        IncompCont.append(CompContItem)

        #ICC Update
        db.Roommate.update_one({"discordName" : str(username)}, {"$set": {"incompleteContainer" : IncompCont }})
        InCompSize = len(db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer'])
        print(f' AFTER UPDATE: ICC len = {InCompSize}')

        # CC Update
        db.Roommate.update_one({"discordName" : str(username)}, {"$set": {"completeContainer" : CompCont }})
        CompSize = len(db.Roommate.find_one({"discordName" : str(username)})['completeContainer'])
        print(f' AFTER UPDATE: CC len = {CompSize}')


        # markingIP = False
        return " This task has been unmarked!\n □ "+str(tLastElement)+") "+str(TaskTitle)+"\n"
    
    elif has_word(p_message, "unmark") and not (has_digit(p_message=p_message)):
        return "You're missing something there buddy. \nTry 'unmark chore' or 'unmark #' where # is the number of the chore on your list. \nType 'unmark chore' if you're not sure which one it is."

    # Incase of error or unexpected input
    elif has_word(p_message, "unmark") and not user_exists(db=db, username=username):
        return "This user is not participating in out chore game :("
    
    #------------------------------ end of unmarking chores ------------------------------#


    #------------------------------ marking chores ------------------------------#

    # 2nd part of the prompt above, 'MARK chore'
    if has_word(p_message, "mark") and has_digit(p_message=p_message):
        tStringArr = p_message.split(' ')
        tLastElement = tStringArr[len(tStringArr)-1]
        IncompCont = db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer']
        CompCont = db.Roommate.find_one({"discordName" : str(username)})['completeContainer']
        CompSize = len(db.Roommate.find_one({"discordName" : str(username)})['completeContainer'])
        InCompSize = len(db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer'])

        IncompContItem = IncompCont[int(tLastElement)-CompSize-1]

        #get title 
        TaskTitle = db.Task.find_one({"_id" : ObjectId(IncompContItem)})['title']

        #update complete and incomplete containers
        IncompCont.remove(IncompContItem)
        CompCont.append(IncompContItem)

        #ICC
        db.Roommate.update_one({"discordName" : str(username)}, {"$set": {"incompleteContainer" : IncompCont }})
        InCompSize = len(db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer'])

        # CC
        db.Roommate.update_one({"discordName" : str(username)}, {"$set": {"completeContainer" : CompCont }})
        CompSize = len(db.Roommate.find_one({"discordName" : str(username)})['completeContainer'])

        # markingIP = False
        return " This task has been marked!\n ☑ "+str(tLastElement)+") "+str(TaskTitle)+"\n"
    
    elif has_word(p_message, "mark") and not (has_digit(p_message=p_message)):
        return "You're missing something there buddy. \nTry 'mark chore' or 'mark #' where # is the number of the chore on your list. \nType 'mark chore' if you're not sure which one it is."

    # Incase of error or unexpected input
    elif has_word(p_message, "mark") and not user_exists(db=db, username=username):
        return "This user is not participating in out chore game :("

    #------------------------------ end of marking chores ------------------------------#

    #------------------------------ end of marking and unmarking chores ------------------------------#




    #------------------------------ trade tasks ------------------------------#

    # --- initiate trade
    if p_message == 'trade':
        tIString = "\n**Incoming Trade requests:**"
        tOString = "**Outgoing Trade requests:**"

        tICount = db.Pending.count_documents({"receiver": username})
        tOCount = db.Pending.count_documents({"sender": username})

        if tICount == 0:
            tIString += " NONE"
        else:
            tPendingReqs = db.Pending.find({"receiver" : username})
            
            count = 1

            for req in tPendingReqs:
                tSTTitle = str(db.Task.find_one({"_id" : req['senderTask']})['title'])
                tRTTitle = str(db.Task.find_one({"_id" : req['receiverTask']})['title'])
                tSName = str(db.Roommate.find_one({"discordName": req['sender']})['roommateName'])

                tIString += "\n"+str(count)+") "+tSName+ " wants to give you: " + "\n ------------ \n \t"+tSTTitle+" \n\t  for  \n \t"+tRTTitle+"\n ------------ \n"

        if tOCount == 0:
            print("h")
            tOString += " NONE"
        else:
            print("i")
            tPendingReqs = db.Pending.find({"sender" : username})
            

            print("j SIZE = "+str(db.Pending.count_documents({"sender" : username})))

            for req in tPendingReqs:
                tSTTitle = str(db.Task.find_one({"_id" : req['senderTask']})['title'])
                tRTTitle = str(db.Task.find_one({"_id" : req['receiverTask']})['title'])
                tRName = str(db.Roommate.find_one({"discordName": req['receiver']})['roommateName'])                

                tOString += "\n Gave "+tRName+": " + "\n ------------ \n \t"+tSTTitle+" \n\t  for  \n \t"+tRTTitle+"\n ------------ \n"


        return "**Who would you like to trade tasks with?** \n @ chore bot with the phrase: \n'trade <my task number> with <Name> for <their task number>' \n where <my task number> and <their task number> is the number of the task and <Name> is the First name of the person you would like to trade with. (ex. 'trade 1 with Jamal for 2'). \n To accept or reject a trade, @Chore-bot with the phrase 'accept trade <#>' or 'reject trade <#>'. Where # corresponds to your Incoming trade request.\n"+print_Group_Assigned_IC_Tasks(db=db)+"\n"+tIString+"\n"+tOString
    
    # 2nd part of the prompt above, 'trade'
    # expected input: "trade m with user for n"
    if has_word(p_message, "trade") and has_word(p_message, "with") and has_word(p_message, "for") and len(message.split(" ")) == 6 and has_digit(p_message=p_message) and user_exists(db=db, username=username) and user_exists_by_name(db=db, name=str(message.split(" ")[3])):
        tWords = message.split(" ")
        print(f'tWords = {tWords}')

        tReceiverUsername = db.Roommate.find_one({"roommateName": tWords[3].capitalize()})['discordName']
        tSenderUsername = str(username)
        tSTaskIndex = int(tWords[1])-1
        tRTaskIndex = int(tWords[5])-1

        print(f'S uname = {tSenderUsername}, s task index = {tSTaskIndex}')
        print(f'R uname = {tReceiverUsername}, s task index = {tRTaskIndex}')

        if task_exists(db=db, username=tReceiverUsername, index=tRTaskIndex) and task_exists(db=db, username=tSenderUsername, index=tSTaskIndex):

            tSTaskOID = ObjectId(db.Roommate.find_one({"discordName": tSenderUsername})['incompleteContainer'][tSTaskIndex])
            tRTaskOID = ObjectId(db.Roommate.find_one({"discordName": tReceiverUsername})['incompleteContainer'][tRTaskIndex])

            print(f'R Task OID = {str(tRTaskOID)}')

            
            # check if trade exists
            if db.Pending.count_documents({"action": "trade", "receiver" : tReceiverUsername, "receiverTask": tRTaskOID, "sender": tSenderUsername, "senderTask": tSTaskOID}) > 0 :
                return "You have already initated this trade, maybe bug them to get your trade moving along ;)"
            else:
                # add trade to pending
                #(!) NEW try an array instead OR Update after insertion
                
                #if >=1 trade has already been intiated before this one
                #       --> we need to update the array of task obj IDs
                if db.Pending.count_documents({"action": "trade", "receiver" : tReceiverUsername, "sender": tSenderUsername}) > 0:

                    #retrieve
                    tRTaskList = db.Pending.find_one({"action": "trade", "receiver" : tReceiverUsername, "sender": tSenderUsername})['receiverTask']
                    tSTaskList = db.Pending.find_one({"action": "trade", "receiver" : tReceiverUsername, "sender": tSenderUsername})['senderTask']

                    #update value locally
                    tRTaskList.append(tRTaskOID)
                    tSTaskList.append(tSTaskOID)

                    #update db
                    db.Pending.update_one({"receiver" : tReceiverUsername,  "sender": tSenderUsername}, {"$set": {"receiverTask": tRTaskOID, "senderTask": tSTaskOID}})

                else:
                    tRTaskList = []
                    tSTaskList = []
                    tRTaskList.append(tRTaskOID)
                    tSTaskList.append(tSTaskOID)

                    db.Pending.insert_one({"action": "trade", "receiver" : tReceiverUsername, "receiverTask": tRTaskList, "sender": tSenderUsername, "senderTask": tSTaskList})



            # Chore-bot response
            tSTTitle = str(db.Task.find_one({"_id" : tSTaskOID})['title'])
            tRTTitle = str(db.Task.find_one({"_id" : tRTaskOID})['title'])
            tRName = str(db.Roommate.find_one({"discordName": tReceiverUsername})['roommateName'])
            tSName = str(db.Roommate.find_one({"discordName": tSenderUsername})['roommateName'])

            print(f'S title = {tSTTitle}')

            return "@"+tReceiverUsername+" "+tRName+", do you accept this trade from "+tSName+"?\n ------------ \n \t"+tSTTitle+" \n\t  for  \n \t"+tRTTitle+"\n ------------ \nThe choice is yours. @ Chore-bot with 'accept trade' or 'deny trade' to respond."

        else:
            return "Either the user you are trying to trade with or one of the task you are trying to trade do not exist. Check yourself"

    elif has_word(p_message, "trade with ") and not (has_digit(p_message=p_message)):
        return "You're missing something there buddy. \n type 'trade <#> with <discord name>' where # is the number of the task and <discord name> is the username of the person you would like to trade with.  \nType 'trade my task' if you're not sure which tasks are available."
    
    elif has_word(p_message, "trade with ") and not user_exists_by_name(db=db, name=message.split(" ")[3]):
        return "Are you trying to trade with a chore?\n  type 'trade <#> with <discord name>' where # is the number of the task and <discord name> is the username of the person you would like to trade with. \nType 'trade my task' if you're not sure which tasks are available."

    # -- Accept trade
    if p_message == 'accept trade':
        tCount = db.Pending.count_documents({"receiver": username})
        
        # There are NO trades
        if tCount == 0:
            return "It appears that no one wants to trade with you :("

        # There is only 1 trade
        elif tCount == 1:


            tTradeReq = db.Pending.find_one({"receiver" : username})
            tReceiverName = db.Roommate.find({"discordName" : username})['roommateName']
            tSenderName = db.Roommate.find({"discordName" : tTradeReq['sender']})['roommateName']
            switch_trade_tasks(db=db, username=username, TradeReq=tTradeReq)
            
            # tReceiverUsername = username
            # tSenderUsername = tTradeReq['sender']
            # tSCont = db.Roommate.find({"discordName" : str(tSenderUsername)})['incompleteContainer']
            # tRCont = db.Roommate.find({"discordName" : str(tReceiverUsername)})['incompleteContainer']
            # tSTaskOID = tTradeReq['650fa3645bcc238ce99260bf']
            # tRTaskOID = tTradeReq['650fa4d35bcc238ce99260c0']

            # #switch Tasks
            # tSCont.remove(tSTaskOID)
            # tSCont.append(tRTaskOID)
            # tRCont.remove(tRTaskOID)
            # tRCont.append(tSTaskOID)

            # db.Roommate.update_one({"discordName" : str(tReceiverUsername)}, {"$set": {"incompleteContainer" : tRCont }})
            # db.Roommate.update_one({"discordName" : str(tSenderUsername)}, {"$set": {"incompleteContainer" : tSCont }})
            return "The following are your new tasks: \n"+tReceiverName+": \n"+print_Indv_Tasks(db=db, username=username)+"\n "+tSenderName+": \n"+print_Indv_Tasks(db=db, username=tTradeReq["sender"])
    
        # There are multiple trades pending
        elif tCount > 1:
            return 'There is more than one request from a user to trade with you. Below are the trade options: \n'+print_trade_options(db=db, username=username)+'\n Respond with "accept trade <#>" to accept a trade by its number (ex. accept trade 2 allows you to accept the trade listed next to "2)" '

    if has_word(p_message, 'accept trade') and len(message.split(" ")) == 3 and has_digit(p_message=p_message):
        tTaskNum = int(message.split(" ")[2])

        tReceiverName = db.Roommate.find({"discordName" : username})['roommateName']
        tSenderName = db.Roommate.find({"discordName" : tTradeReq['sender']})['roommateName']

        # do same query as above for multiple trades pending
        # store the trade item locally
        tTradeReq = get_trade_dict(db=db, username=username, index=tTaskNum)
        
        # switch tasks
        switch_trade_tasks(db=db, username=username, TradeReq=tTradeReq)
        
        return "The following are your new tasks: \n"+tReceiverName+": \n"+print_Indv_Tasks(db=db, username=username)+"\n "+tSenderName+": \n"+print_Indv_Tasks(db=db, username=tTradeReq["sender"])



    # -- Deny trade
    if p_message == 'deny trade':
        tCount = len(db.Pending.count_documents({"receiver": username}))
        
        # There are NO trades
        if tCount == 0:
            return "It appears that no one wants to trade with you :("

        # There is only 1 trade
        elif tCount == 1:
            tTradeReq = db.Pending.find_one({"receiver" : username})
            tReceiverName = db.Roommate.find({"discordName" : username})['roommateName']
            tSenderName = db.Roommate.find({"discordName" : tTradeReq['sender']})['roommateName']
            
            # delete the pending trade
            db.Pending.delete_one({"_id": ObjectId(tTradeReq['_id'])})
            
            return "A trade between "+tReceiverName+" and "+tSenderName+" has been denied. It no longer exists..."
    
        # There are multiple trades pending
        elif tCount > 1:
            return 'There is more than one request from a user to trade with you. Below are the trade options: \n'+print_trade_options(db=db, username=username)+'\n Respond with "deny trade <#>" to deny a trade by its number (ex. deny trade 2 allows you to deny the trade listed next to "2)" '



    if has_word(p_message, 'deny trade') and len(message.split(" ")) == 3 and has_digit(p_message=p_message):
        tTaskNum = int(message.split(" ")[2])

        tReceiverName = db.Roommate.find({"discordName" : username})['roommateName']
        tSenderName = db.Roommate.find({"discordName" : tTradeReq['sender']})['roommateName']

        # do same query as above for multiple trades pending
        # store the trade item locally
        tTradeReq = get_trade_dict(db=db, username=username, index=tTaskNum)
        
        # delete the pending trade
        db.Pending.delete_one({"_id": ObjectId(tTradeReq['_id'])})
        
        return "A trade between "+tReceiverName+" and "+tSenderName+" has been denied. It no longer exists..."
    


    #------------------------------ end of trading tasks ------------------------------#

    #------------------------------ Stealing tasks ------------------------------#

    if p_message == 'steal a Task':
        return "Who would you like to steal from? \n @ chore bot with the phrase: \n'steal <victim's task number> from <victim's first name>' \n where <victim's task number> and <their task number> is the number of the task and <victim's first name> is the First name of the person you would like to steal from. (ex. 'steal 1 from Jamal')\n"+print_Group_Assigned_IC_Tasks(db=db)
    
    # expected input: 'steal <#> from <first name>'
    if has_word(p_message, "steal") and has_word(p_message, "from") and len(message.split(" ")) == 4 and has_digit(p_message=p_message) and user_exists_by_name(db=db, name=str(message.split(" ")[3])):

        tWords = message.split(" ")
        print(f'tWords = {tWords}')

        tReceiverUsername = db.Roommate.find_one({"roommateName": tWords[3].capitalize()})['discordName']
        tSenderUsername = str(username)
        tRTaskIndex = int(tWords[1])-1

        print(f'S uname = {tSenderUsername} ')
        print(f'R uname = {tReceiverUsername}, s task index = {tRTaskIndex}')

        if task_exists(db=db, username=tReceiverUsername, index=tRTaskIndex):

            tRTaskOID = ObjectId(db.Roommate.find_one({"discordName": tReceiverUsername})['incompleteContainer'][tRTaskIndex])
            tRCont = ObjectId(db.Roommate.find_one({"discordName": tReceiverUsername})['incompleteContainer'])
            tSCont = ObjectId(db.Roommate.find_one({"discordName": tSenderUsername})['incompleteContainer'])

            print(f'R Task OID = {str(tRTaskOID)}')

            # add trade to pending
            db.Pending.insert_one({"action": "trade", "receiver" : tReceiverUsername, "receiverTask": tRTaskOID, "sender": tSenderUsername, "senderTask": tSTaskOID})

            # Chore-bot response
            tTask = db.Task.find_one({"_id" : tRTaskOID})
            tRTTitle = str(tTask['title'])
            tRName = str(db.Roommate.find_one({"discordName": tReceiverUsername})['roommateName'])
            tSName = str(db.Roommate.find_one({"discordName": tSenderUsername})['roommateName'])

            # steal: remove, add, and update
            tRCont.remove(tRTaskOID)
            tSCont.append(tRTaskOID)
            db.Roommate.update_one({"discordName" : str(tReceiverUsername)}, {"$set": {"incompleteContainer" : tRCont }})
            db.Roommate.update_one({"discordName" : str(tSenderUsername)}, {"$set": {"incompleteContainer" : tSCont }})

            return "@"+tReceiverUsername+" "+tRName+", Your shit just got SNAGGED by "+tSName+"!! \n Remeber, what matters most is who completes it first, you might still be able to steal it back ;)"

    #------------------------------ end of stealing tasks ------------------------------#


    #------------------------------ Forfeit tasks ------------------------------#
    if p_message == 'forfeit my task':
        return "Who would you like to forfeit to? \n @ chore bot with the phrase: \n'forfeit <recepient's task number> to <recepient's first name>' \n where <recepient's task number> and <their task number> is the number of the task and <recepient's first name> is the First name of the person you would like to forfeit to. (ex. 'forfeit 1 to Jamal')\n"+print_Group_Assigned_IC_Tasks(db=db)
           
    # expected input: 'forfeit <#> to <first name>'
    if has_word(p_message, "forfeit") and has_word(p_message, "to") and len(message.split(" ")) == 4 and has_digit(p_message=p_message) and user_exists_by_name(db=db, name=str(message.split(" ")[3])):

        tWords = message.split(" ")
        print(f'tWords = {tWords}')

        tReceiverUsername = db.Roommate.find_one({"roommateName": tWords[3].capitalize()})['discordName']
        tSenderUsername = str(username)
        tRTaskIndex = int(tWords[1])-1

        print(f'S uname = {tSenderUsername} ')
        print(f'R uname = {tReceiverUsername}, s task index = {tRTaskIndex}')

        if task_exists(db=db, username=tReceiverUsername, index=tRTaskIndex):

            tRTaskOID = ObjectId(db.Roommate.find_one({"discordName": tReceiverUsername})['incompleteContainer'][tRTaskIndex])
            tRCont = ObjectId(db.Roommate.find_one({"discordName": tReceiverUsername})['incompleteContainer'])
            tSCont = ObjectId(db.Roommate.find_one({"discordName": tSenderUsername})['incompleteContainer'])

            print(f'R Task OID = {str(tRTaskOID)}')

            # add trade to pending
            db.Pending.insert_one({"action": "trade", "receiver" : tReceiverUsername, "receiverTask": tRTaskOID, "sender": tSenderUsername, "senderTask": tSTaskOID})

            # Chore-bot response
            tTask = db.Task.find_one({"_id" : tRTaskOID})
            tRTTitle = str(tTask['title'])
            tRName = str(db.Roommate.find_one({"discordName": tReceiverUsername})['roommateName'])
            tSName = str(db.Roommate.find_one({"discordName": tSenderUsername})['roommateName'])

            # steal: remove, add, and update
            tRCont.remove(tRTaskOID)
            tSCont.append(tRTaskOID)
            db.Roommate.update_one({"discordName" : str(tReceiverUsername)}, {"$set": {"incompleteContainer" : tRCont }})
            db.Roommate.update_one({"discordName" : str(tSenderUsername)}, {"$set": {"incompleteContainer" : tSCont }})

            return "@"+tReceiverUsername+" "+tRName+", Your shit just got SNAGGED by "+tSName+"!! \n Remeber, what matters most is who completes it first, you might still be able to steal it back ;)"
           

    #------------------------------ end of Forfeit tasks ------------------------------#


    #------------------------------ Test methods ------------------------------#
    if p_message == 'bleep bloop':
        return 'Not Implemented yet.'          
    if p_message == 'roll':
        return str(random.randint(1, 6))
    #------------------------------  end of Test methods ------------------------------#

    #------------------------------ Reset methods ------------------------------#
    if has_word(p_message, "reset") and (has_word(p_message, "month") or has_word(p_message, "year") or has_word(p_message, "week")): #p_message == 'reset':

        tWords = message.split(" ")
        print(f'tWords = {tWords}')

        #Check if its Upsetti OR if its a Sunday
        #rng seed? idk maybe based on time?? could rig it so whoever failed their tasks has a harder difficulty task?
        weekly_Reset(tWords[1])
    
    if p_message == 'schedule':
        return Laundry_Day_schedule()

    if p_message == '!help':
        return help_message()
    #------------------------------ end of Reset methods ------------------------------#


#------------------------------ Major Helper methods ------------------------------#
def help_message():
    return " The following are command options: (case insensitive)  \n - 'view my stats' \n - 'view group stats' \n - 'unmark chore' \n - 'mark chore' (these marks your chore as either incomplete or complete) \n - 'view my tasks' \n - 'view group tasks' (shows you everyone's tasks) \n - 'trade' (Allows you to view Incoming/outgoing trade request and initiate a trade your task with another member of the group) \n -  'steal' (allows you to Steal someone else's task to obtain more points) \n -  'forfeit' (Allows you to forfeit your task to a given member of the group)"     

def weekly_Reset(aType):
#    #Check Pseudocode
#    #current date
#    #tCurrentDate 
#    tCurrDay= datetime.datetime.now().day
#    tCurrMonth= datetime.datetime.now().month
#    tCurrMonth= datetime.datetime.now().year

#    #Monthly
#    if aType == "Month":
#     #reset tMonthDeadline to 1 month from the current date
#     tMonthDeadline = #the date 1 month from now

#    #Weekly
#    elif tWeekDeadline <= tCurrentDate):
#       #clear weekly chores from taken and available
#       #fill available
   
#       #clear roommate's containers (only completed?)
#       tRoommate.CompleteContainer = [] #or .clear()
   
   
#       for each priority p :#ascending order
#          #shuffle order of tAvailableWeek
#          random.shuffle(tAvailableWeek)
            
#          for each task in tAvailableWeek a :
#             if    tTaskList[a].DeadlineType == "Weekly" and tTaskList[a].Priorities contains p and !(tTakenWeek contains p):
#                #Assign to roommate of priority group
               
               
#                #Add to taken
#                tTakenWeek.insert(p)
         
#          # update available to remove whats been taken before next priority looP
#          #remove from tAvailableWeek
#          for each task in tAvailableWeek a :
#             if tTakenWeek contains a :
#                #remove a from tAvailableWeek (by its index)
#                tAvailableWeek.remove(a)
           
      
#       #reset tWeekDeadline to 1 week from the current date
#       tWeekDeadline = the date 1 week from now
     
#     #Update deadlines in DB

    return 'Not Implemented yet.' 

def Laundry_Day_reminder():
    #Check day of the week
    #always goes out at a specific time? automate it?
    return 'Not Implemented yet.' 

def Laundry_Day_schedule():
    return " The Laundry day schedule is as follows: (case insensitive)  \n - Johan and Ricky: Monday-Wednesday  \n - Alex and Bridget: Wednesday-Friday  \n - Bethany and Jamal: Saturday-Sunday"

#------------------------------ end of Major Helper methods ------------------------------#

#------------------------------ Minor Helper methods ------------------------------#

def has_digit(p_message):
    return any(c.isdigit() for c in p_message)

def user_exists(db, username):
    print(f'len = {len(db.Roommate.find_one({"discordName" : str(username)}))}')

    return len(db.Roommate.find_one({"discordName" : str(username)})) > 0

def user_exists_by_name(db, name):
    tStr = str(db.Roommate.find_one({"roommateName" : str(name.capitalize())})['discordName'])
    print(f'string found = {tStr}')

    return user_exists(db=db, username=tStr)

def switch_trade_tasks(db, username, TradeReq):
    tReceiverUsername = username
    tSenderUsername = TradeReq['sender']
    tSCont = db.Roommate.find({"discordName" : str(tSenderUsername)})['incompleteContainer']
    tRCont = db.Roommate.find({"discordName" : str(tReceiverUsername)})['incompleteContainer']
    tSTaskOID = TradeReq['650fa3645bcc238ce99260bf']
    tRTaskOID = TradeReq['650fa4d35bcc238ce99260c0']

    # switch Tasks
    tSCont.remove(tSTaskOID)
    tSCont.append(tRTaskOID)
    tRCont.remove(tRTaskOID)
    tRCont.append(tSTaskOID)

    # update
    db.Roommate.update_one({"discordName" : str(tReceiverUsername)}, {"$set": {"incompleteContainer" : tRCont }})
    db.Roommate.update_one({"discordName" : str(tSenderUsername)}, {"$set": {"incompleteContainer" : tSCont }})

    # delete the pending trade
    db.Pending.delete_one({"_id": ObjectId(TradeReq['_id'])})


    
def task_exists(db, username, index):
    print(f' user: {str(username)}, index = {index}\n incomplete container len =  = {len(db.Roommate.find_one({"discordName" : str(username)})["incompleteContainer"])} , complete container len =  {len(db.Roommate.find_one({"discordName" : str(username)})["completeContainer"])}\n')

    return len(db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer']) > index or len(db.Roommate.find_one({"discordName" : str(username)})['completeContainer']) > index

def has_word(p_message, tWord):
    return tWord in p_message

def get_trade_dict(db, username, index):
    tTradeDict = db.Pending.find({"receiver": username})

    for t, i in enumerate(tTradeDict):
        if index == i:
            #returns the correct pending trade
            return t

    return 0

def print_trade_options(db, username):
    tTradeDict = db.Pending.find({"receiver": username})
    tString = ""
    tCount = 1
    for t in tTradeDict:

        tRName = db.Roommate.find_one({"discordName" : t['receiver']})['roommateName']
        tSName = db.Roommate.find_one({"discordName" : t['sender']})['roommateName']
        tRTask = db.Task.find_one({"_id" : t['receiverTask']})['title']
        tSTask = db.Task.find_one({"_id" : t['senderTask']})['title']

        tString += tCount+") "+tRName+" gives you \n    "+tRTask+" \n      in exchange for \n   "+tSTask+"\n"

    return tString

def print_Indv_Tasks(db, username):
    ## Task IDs ##
    CompTaskIDs = db.Roommate.find_one({"discordName" : str(username)})['completeContainer']
    IncompTaskIDs = db.Roommate.find_one({"discordName" : str(username)})['incompleteContainer']
    CompTaskList = []
    IncompTaskList = []

    ## find each Task Object ##
    for c in CompTaskIDs:
        CompTaskList.append(db.Task.find_one({"_id" : ObjectId(c)}))

    for i in IncompTaskIDs:
        IncompTaskList.append(db.Task.find_one({"_id" : ObjectId(i)}))

    ## fill string ##
    tString = "The following are the chores you've currently been assigned: \n"
    tCount = 0

    for c in CompTaskList:
        tCount += 1
        tString += "☑ "+str(tCount)+") "+str(c['title'])+"\n"

    for i in IncompTaskList:
        tCount += 1
        tString += "□ "+str(tCount)+") "+str(i['title'])+"\n"

    ## Marking global variable
    # markingIP = True

    return tString

def print_Group_Tasks(db):
    ## Task IDs ##
    tRoommateList = db.Roommate.find()
    tMessage = "The following is everyone's progress with chores this week: \n"
    tCompString = ""
    tInCompString = ""
    tCCount = 0
    tICount = 0

    for r in tRoommateList:
        CompTaskIDs = r['completeContainer']
        IncompTaskIDs = r['incompleteContainer']
        CompTaskList = []
        IncompTaskList = []
        
        ## find each Task Object ##
        for c in CompTaskIDs:
            CompTaskList.append(db.Task.find_one({"_id" : ObjectId(c)}))

        for i in IncompTaskIDs:
            IncompTaskList.append(db.Task.find_one({"_id" : ObjectId(i)}))

        ## fill string ##
        tCString = ""
        for c in CompTaskList:
            tCCount += 1
            tCString += "☑ "+str(c['title'])+"\n"

        tCompString += tCString
        tIString = ""
        
        for i in IncompTaskList:
            tICount += 1
            tIString += "□ "+str(i['title'])+"\n"
   
        tInCompString += tIString


    tMessage += tCompString + tInCompString 

    tEndMsg = ""
    tSpecialMsg = ""
    if tCCount == 0 and tICount == 0:
        tEndMsg = "\n\n We are 0% of the way done"
    else:
        tProgress = round(tCCount/(tCCount+tICount)*100)
        if tProgress == 100:
            tSpecialMsg="! We did it!"
        elif tProgress >= 90:
            tSpecialMsg="- which one of y'all SLACKIN?? GO! JUST GO!! WE'RE SO CLOSE JUST FUCKING GOOO-"
        elif tProgress > 80:
            tSpecialMsg="! We're almost there!"
        elif tProgress > 60:
            tSpecialMsg="! Keep going!"
        elif tProgress > 50:
            tSpecialMsg="! We're Half way thee~re ooohhh OHHH, livin' on a pray'er"
        elif tProgress > 40:
            tSpecialMsg="! I swear if we arent passed this point by Thursday IMMA THROW SOME HANDS-"
        elif tProgress > 30:
            tSpecialMsg="! Great start! "
        elif tProgress <= 20:
            tSpecialMsg="! The hardest part is starting... "

        tEndMsg = "\n\n We are "+str(tProgress)+"% of the way done"+tSpecialMsg


    tMessage += tEndMsg



    ## Marking global variable
    # markingIP = True

    return tMessage

def print_Group_Assigned_IC_Tasks(db):
## Task IDs ##
    tRoommateList = db.Roommate.find()
    tMessage = "\n\n**The following is everyone's remaining chores for this week:**"
    tInCompString = ""

    for r in tRoommateList:
        tICount = 0
        IncompTaskIDs = r['incompleteContainer']
        IncompTaskList = []
        print(f'IncompTaskIDs length = {len(IncompTaskIDs)}')

        ## find each Task Object ##
        for i in IncompTaskIDs:
            IncompTaskList.append(db.Task.find_one({"_id" : ObjectId(i)}))

        ## fill string ##
        if len(IncompTaskList) == 0:
            tIString = ""
        else:
            tIString = "\n\tName: "+str(r['roommateName'])+"\n"

        for i in IncompTaskList:
            tICount += 1
            tIString += "\t\t□ "+str(tICount)+") "+str(i['title'])+"\n"
        
        tInCompString += str(tIString)

    tMessage += " \n"+tInCompString 

    return tMessage


#------------------------------ end of Minor Helper methods ------------------------------#


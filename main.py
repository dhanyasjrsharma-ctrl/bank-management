from pathlib import Path
import json
import random
import string


class Bank:
    database="database.json"
    data=[]

    try:
        if Path(database).exists():
            with open(database) as fs:
                data=json.loads(fs.read())
    except Exception as err:
        print(f"an error occured as {err} try again")

    @classmethod
    def __update(cls):
         with open(cls.database,'w') as fs:
              fs.write(json.dumps(cls.data))

    @staticmethod
    def __generate_acc():
        char=random.choices(string.ascii_uppercase,k=4)
        digits=random.choices(string.digits,k=8)
        acc=char+digits
        final="".join(acc) # .join is used to convert list into a string
        return final


    def create_account(self):
        # we'll create a dictionary for taking multiple info 
        info={
                "name": input("enter your name:"),
                "age": int(input("enter your age:")),
                "mail":input("enter your mail:"),
                "balance":0,
                "account no.": Bank.__generate_acc()
        }

# we have to check for pin alag se because we can only accept 4 digits wih no other thing in a pin 
        try:
            while True:
                pin=int(input("enter your 4 digit pin:"))
                if len(str(pin))!= 4:
                    print("your pin must be of 4 digits")
                else:
                    info["pin"]=pin
                    break
        except Exception as ValueError :
                print("you can only have numbers try again")

        try:
            while True:
            
                number=int(input("enter your 10 digit number:"))
                if len(str(number)) != 10:
                    print("your number must be of 10 digits")
                else:
                    info["number"]= number
                    break
        except Exception as ValueError :
            print("you can only have numbers try again")

        if info["age"] < 18:
            print("you are a minor")
            return
        else:
            Bank.data.append(info)
            Bank.__update()


             
    def deposit_money(self):
        acc_no=input("tell your account no:-")
        pin=int(input("tell your pin:-"))
        user=[i for i in Bank.data if i["pin"]==pin and i["account no."]==acc_no]
        # this is known as list comprehension where we extract user data from dummy data from a single lsit
        # pehle for loop then if condition bcz both should satisfy

        if user:
            money=int(input("how much money do you want to deposit:-"))
            if money > 100000 or money <= 0:
                print("you cannot deposit more than 100000 rs and less than 0 rs")
            else:
                user[0] ["balance"] += money
                print("money added successfully visit again")
                Bank.__update()
        else:
            print("invalid acc no or pin")



    def withdraw_money(self):
        acc_no=input("tell your acc no:-")
        pin=int(input("tell your pin:-"))
        user=[i for i in Bank.data if i ["pin"]==pin and i ["account no."]==acc_no]

        if user:
            money=int(input("how much money do you want to withdraw:-"))
            if money >= user[0] ["balance"] :
                print("you don't have sufficient balance")
            else:
                user[0]["balance"] -= money
                print("money debited successful")
                Bank.__update()
        else:
            print("invalid acc no or pin")



    def check_details(self):
        acc_no=input("tell your acc no:-")
        pin=int(input("tell your pin:-"))
        user=[i for i in Bank.data if i ["pin"]==pin and i ["account no."]==acc_no]

        if user:
            print("your details are: /n")
            for i in user[0]:
                if i != "pin":
                    print(f" {i} : {user[0][i]}")
        else:
            print("invalid acc no or pin")

    def update_details(self):
            acc_no=input("tell your acc no:-")
            pin=int(input("tell your pin:-"))
            user=[i for i in Bank.data if i ["pin"]==pin and i ["account no."]==acc_no]
            if user == False:
                print("invalid no. or pin")
            else:
                newdata={
                    "name": input("enter to skip or type your new name:"),
                    "mail":input("enter to skip or type your new mail:"),
                    "number":input("enter to skip or type your new number:"),
                    "pin":input("enter to skip or type your new pin:")
                }

                if newdata['name']=="":
                    newdata["name"]=user[0]["name"]

                if newdata['mail']=="":
                    newdata["mail"]=user[0]["mail"]

                if newdata['number']=="":
                    newdata["number"]= str(user[0]["number"])

                if newdata['pin']=="":
                    newdata["pin"]=str(user[0]["pin"])

                    newdata["pin"] = int(newdata["pin"])
                    newdata["number"] = int(newdata["number"])

            for i in user[0]:
                if i in newdata:
                    user[0][i] = newdata[i]
            bank.__update()

    def delete_details(self):
            acc_no=input("tell your acc no:-")
            pin=int(input("tell your pin:-"))
            user=[i for i in Bank.data if i ["pin"]==pin and i ["account no."]==acc_no]

            if user == False:
                print("invalid user or pin")
            else:
                print("are you sure press y/n")

                check=input("press(y)or (n)")
                if check == 'y' or check == "Y":
                    index = Bank.data.index(user)
                    Bank.data.pop(index)

                    Bank.__update()
                else:
                    print("okiiee")

bank=Bank()

print("press 1 for creating an account")
print("press 2 for depositing money")
print("press 3 for withdrawal")
print("print 4 for checking balance")
print("press 5 for updating some details")
print("press 6 for deactivating your account")
print("press   0 for exit")


check=int(input("tell your response :-"))

if check==1:
    bank.create_account()

if check ==2:
    bank.deposit_money()

if check ==3:
    bank.withdraw_money()

if check==4:
    bank.check_details()

if check==5:
    bank.update_details()

if check == 6:
    bank.deposit_details()


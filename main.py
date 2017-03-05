from cmd import Cmd
import sys, time, random, json

# vars
typing_speed = 100  #wpm
dataFile = "data.json"
started = False
data = {}
lTime = ''
numberString = [
    'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
    'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
    'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen', 'Twenty'
]


# methods
def slow_type(t):
    """prints things slowly to the screen"""
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        # continue  # todo remove this for prod release
        if random.random() > 0.8: continue
        time.sleep(random.random() * 10.0 / typing_speed)
    print ''


def runQuestions(chap):
    """ Runs through all the questions and steps of the adventure """
    global data
    #make new cmd class for here
    for i, q in enumerate(data[chap]):
        if i < data["stage"][1]: continue
        count = 0
        wasEmpty = False
        while True:
            num = numberString[i + 1] if i < 19 else str(i)
            if not wasEmpty: slow_type('Question ' + num + ': ' + q['q'])
            wasEmpty = False
            k = raw_input('?> ')
            if not q['conf']['caps']: k = k.lower()
            if k == "quit" or k == "exit":
                slow_type("Leaving the adventure interface...")
                return
            elif k == "save":
                saveData()
                return
            elif k == "hint":
                giveHint(q, count)
            elif k == q['a']:
                index = count if count < len(q['succ']) else len(q['succ']) - 1
                slow_type(q['succ'][index] + "\n")
                data['stage'][1] = i + 1
                break
            elif k == 'help':
                slow_type(
                    "Commands:  quit  hint  save  help (they all kinda just do what they say)\n"
                )
            elif k == '':
                wasEmpty = True
            else:
                slow_type(
                    "Incorrect. You can try again, but don't forget you might be able to get a hint by using the 'hint' command\n"
                )
            count += 1

    # when we've left the loop
    if data['stage'][1] > len(data[chap]) - 1:
        slow_type("You finished Chapter " + str(data['stage'][0] + 1) + '!')
        data['stage'][0] += 1
        data['stage'][1] = 0
        saveData()

    if data['stage'][0] > len(data['chapters']) - 1:
        slow_type("YOU'VE COMPLETED YOUR ADVENTURE! :D\n\tCONGRATULATIONS!")
        endGame()
    else:
        slow_type("Would you like to continue to the next chapter?")
        yn = raw_input("y/n> ")
        if yn == "y":
            runChapter()
        else:
            slow_type(
                "You chose not to continue.\nYour progress has been saved and you can continue at any time."
            )


def endGame():
    """No idea exactly what this will be yet, but this is run once the game is finished"""
    print "some super secret surprise link"  #todo


def giveHint(q, count):
    """ Provides hints to the player if they have some remaining """
    global data
    #todo allow only a certain number of hints every day and not within 2 minutes of the last one.
    cTime = time.time()
    if 'hint' not in q:
        slow_type("There's no hint for this question :(\n")
        return

    if data['hintConf']['current'] == 0:
        slow_type(
            "You have no more hints remaining! If you're really stuck you should turn the system off, take a break and come back tomorrow!\n"
        )
        return

    if count > len(q['hint']):
        slow_type(
            "There are no more hints for this question. The last hint you got was:\n"
            + q['hint'][len(q['hint']) - 1] + '\n')
        return

    slow_type("You have " + str(data['hintConf']['current']) +
              " hints remaining. Are you sure you want to use a hint now?")
    yn = raw_input("y/n> ")
    if yn == "y":
        index = count if count < len(q['hint']) else len(q['hint']) - 1
        data['hintConf']['current'] -= 1
        slow_type("You now have " + str(data['hintConf']['current']) +
                  " hints remaining.\nYour hint: " + q['hint'][index] + "\n")
    else:
        slow_type("No Hint points were spent.\n")


def runChapter():
    global data
    chap = data['chapters'][data['stage'][0]]
    chapRef = chap['ref']
    slow_type("\n\t" + chap['title'])
    if data['stage'][1] == 0:
        slow_type('-----------------------------------------')
        slow_type(chap['desc'])
    runQuestions(chapRef)


def loadData():
    """ http://stackoverflow.com/questions/4450144/easy-save-load-of-data-in-python """
    global data, started
    file = open(dataFile, 'r')
    data = json.load(file)
    file.close()
    started = data['started']
    if data['stage'] == [0, 0]:
        print 'we\'ve not started yet'
        started = False
    if data['hintConf']['type'] == 'sessionReset':
        data['hintConf']['current'] = data['hintConf']['start']


def saveData():
    global data, started
    data['started'] = started
    file = open(dataFile, 'w')
    json.dump(data, file)


# def connectToWifi(user, pw):
# slow_type("Starting connection attempt to "+user+" with "+pw)


# Class 'cause reasons
class mainPrompt(Cmd):
    def preloop(self):
        """Starts the adventure"""
        global started
        # todo add a note telling people where they're continuiong for
        slow_type(
            "[ To leave the program type 'quit' then unplug the device ]")
        slow_type("To continue your adventure type 'continue'!"
                  if started else "To begin your adventure type 'adventure'!")

    emptyCount = 0

    def emptyline(self):
        """This is so we don't just keep repeating commands. That would be silly'"""
        self.emptyCount += 1
        if self.emptyCount % 3 == 0:
            slow_type(
                "  Typing 'help' will give you a list of possible commands.")

    def do_quit(self, args):
        """Quits the program."""
        saveData()
        print "Quitting. :'("
        return True

    def do_exit(self, args):
        """Exits the program"""
        self.do_quit(args)

    # def do_networksetup(self, args):
    #     """uses bash to set up a new wifi connection on the raspberry pi"""
    #     print "this is the networksetup option"
    #     if len(args) != 3:
    #         slow_type("Please give me some details so I can connect to your wifi? ^_^\nWhat is your Wifi's name?")
    #         name = raw_input('wifi> ')
    #         slow_type("What is the password for the wifi?")
    #         password = raw_input('password> ')
    #         slow_type("Is this correct?\n\tWifi: "+name+"\tPassword: "+password)
    #         yn = raw_input('y/n> ')
    #         if yn == 'y': connectToWifi(name, password)
    #         else: slow_type("That's too bad, try running this argument again to get the inputs right")

    def do_continue(self, args):
        """Used to continue a current adventure"""
        global started
        if not started:
            slow_type("You have no adventure to continue yet :'(")
            return
        slow_type("Welcome back!")
        runChapter()

    def do_adventure(self, args):
        """Used to start your adventure. Impossible to use once an adventure is started."""
        global started
        if started:
            slow_type(
                "You can't start an another adventure! You can only continue your current adventure :P"
            )
            slow_type(
                "Would you like to continue with your current adventure? y/n?")
            while (True):
                r = raw_input('> y/n? ')
                if r == 'y':
                    self.do_continue(args)
                    return
                elif r == 'n':
                    return
                else:
                    slow_type("You need to pick either 'y' or 'n'")
        slow_type("Let's begin your adventure :D")
        started = True
        runChapter()


if __name__ == '__main__':
    # todo use cmdline args to create a data.json file with the necessary layout
    slow_type("Hello, and welcome to The Adventure Interface v3.2RC13")
    loadData()
    prompt = mainPrompt()
    prompt.prompt = '> '
    prompt.cmdloop()

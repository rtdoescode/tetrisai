class ConsoleHelper:

    colourdict = {

        "success"       :'\033[94m',
        "info"          :'\033[92m',
        "warn"          :'\033[93m',
        "fail"          :'\033[91m',

        "red"           :'\033[31m',
        "green"         :'\033[32m',
        "yellow"        :'\033[33m',
        "blue"          :'\033[34m',
        "purple"        :'\033[35m',
        "cyan"          :'\033[36m',
        "white"         :'\033[37m'}

    endchar = '\033[0m'

    @staticmethod
    def printHelper(colour, text):

        if colour in ConsoleHelper.colourdict:
            colour = ConsoleHelper.colourdict[colour]

        print(colour, text, ConsoleHelper.endchar)


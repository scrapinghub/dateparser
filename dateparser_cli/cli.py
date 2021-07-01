import sys

def entrance():
    args = sys.argv[1:]

    if args[0] == "download":
        download(args[1:])

def download(args):
    if args[0] == "fasttext":
        fasttext(args[1])

def fasttext(model=""):

    print(model)

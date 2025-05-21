from .parser import Parser
from .checker import Checker

parser = Parser()
checker = Checker()

def main():
    parser.check()

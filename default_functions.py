from default_types import *

def card(l:SET)->N:
    return len(l)

def echo(*v):
    print(*v)

def ask(t:[N,Z,R,C,S,B],ch:S):
    rep =''
    if t==S:
        rep=1
    while not t.recognize(rep):
        rep = input(ch)
    return t.from_str(rep)

def Re(c:C):
    return c.re

def Im(c:C):
    return c.im

F = ['Im', 'Re', 'ask', 'card', 'echo']
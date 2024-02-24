import default_types #import *
import sys,error

DEFAULT_FUNCTIONS = {"card","echo","ask","convert"}


def card(l):
    return len(l)

def echo(*v):
    print(*v)#,file=file)

def ask(t,ch):
    global ANS
    rep =''
    t=default_types.type_from_str(t)
    if t==default_types.S:
        rep=1
    while True:
        rep = input(ch)
        if(t.recognize(rep)):break
    return t.from_str(rep)

def Re(c):
    return c.re

def Im(c):
    return c.im

def convert(obj,typ):
    if type(typ)==str:
        typ = default_types.type_from_str(typ)
    if typ ==type(obj):return obj
    if typ == default_types.S:
        return default_types.S(str(obj))
    
    if type(typ)==default_types.Parts:
        assert type(obj)==default_types.SET or type(obj)==default_types.EmptySet
        if type(obj) == default_types.EmptySet:
            return default_types.SET(typ.typ)
        r = default_types.SET(typ.typ)
        for elt in obj:
            r.add(convert(elt,typ.typ))
        return r
    
    if type(typ)!=default_types.CrossSet:
        if type(obj) not in default_types.INCLUSIONS:raise error.ConvertionError
        if not typ in default_types.INCLUSIONS[type(obj)]:raise error.ConvertionError
        return typ(obj.value)
    
    assert type(obj)==default_types.Tuple 
    assert default_types.include(obj.type,typ)
    t=[]
    for i in range(len(typ.schema)):
        t.append(convert(obj[i],typ.schema[i]))
    return default_types.Tuple(tuple(t),typ)

def IN(v,t):
    t = default_types.TYPES[t]
    if type(v)==t:
        return default_types.B(True)
    if type(v) not in default_types.INCLUSIONS:return default_types.B(False)
    return default_types.B(t in default_types.INCLUSIONS(type(v)))


F = ['Im', 'Re', 'ask', 'card', 'echo','convert']

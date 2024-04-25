import default_types #import *
import sys,error

DEFAULT_FUNCTIONS = ['Im', 'Re', 'ask', 'card', 'echo','convert','dim','card','help']

def help(v):
    echo(v.__doc__)

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
    if typ == default_types.Parts(default_types.EmptySet) and type(obj)==default_types.EmptySet:
        return default_types.EmptySet()
    if typ ==type(obj):return obj
    if typ == default_types.S:
        return default_types.S(str(obj))
    
    if type(typ)==default_types.Parts:
        if not(type(obj)==default_types.SET or type(obj)==default_types.EmptySet):
            raise error.ConvertionError(obj,default_types.stringify(typ))
        if type(obj) == default_types.EmptySet:
            return default_types.SET(typ.typ)
        r = default_types.SET(typ.typ)
        for elt in obj:
            r.add(convert(elt,typ.typ))
        return r
    if type(typ)!=default_types.CrossSet:
        if type(obj) not in default_types.INCLUSIONS:
            print(obj,typ,type(obj))
            raise error.ConvertionError(obj,typ)
        if not typ in default_types.INCLUSIONS[type(obj)]:raise error.ConvertionError(obj,typ)
        return typ(obj.value)
    
    if type(obj)!=default_types.Tuple  or not default_types.include(obj.type,typ):
        print('ici2')
        raise error.ConvertionError(obj,default_types.stringify(typ))
    t=[]
    for i in range(len(typ.schema)):
        t.append(convert(obj[i],typ.schema[i]))
    return default_types.Tuple(tuple(t),typ)

def dim(elt):
    if not(type(elt)==default_types.CrossSet or type(elt)==default_types.Tuple):
        raise error.UnsupportedOperation('dim',default_types.stringify(type(elt)))
    if type(elt)==default_types.Tuple:
        return dim(elt.type)
    return default_types.N(len(elt.schema))

def card(elt):
    if type(elt)!=default_types.SET:
        raise error.UnsupportedOperation('card',default_types.stringify(type(elt)))
    return default_types.N(len(elt.deep_get()))

def IN(v,t):
    t = default_types.TYPES[t]
    if type(v)==t:
        return default_types.B(True)
    if type(v) not in default_types.INCLUSIONS:return default_types.B(False)
    return default_types.B(t in default_types.INCLUSIONS(type(v)))

import json,file
import Variable,default_types,Dictionnary,Applications,_parser_,Functions,default_functions

def load(path):
    data=file.get_json(path)

    VARIABLES = {}
    DICTIONNARY = {}
    FUNCTIONS = {}
    ALIAS = {}


    for k,v in data["Variables"].items():
        t,value,flag='','',True
        for car in v:
            if car ==';' and flag:
                flag=False
                continue
            if flag:
                t+=car
            else:
                value+=car

        t = default_types.type_from_str(t)
        VARIABLES[k] = Variable.Variable(t,k)
        if type(t)==default_types.Parts:
            v = default_types.SET(t.typ)
            value = default_types.SET.listify(value)
            for elt in value:
                elt = default_types.full_typize(elt)
                elt = default_functions.convert(elt,t.typ)
                v.add(elt)
            

            VARIABLES[k].set(v)
        elif type(t)==default_types.CrossSet:
            VARIABLES[k].set(default_types.Tuple.from_str(value,t))
        else:
            VARIABLES[k].set(t.from_str(value))

    for k,v in data['Dictionnaires'].items():
        t1,t2 = (default_types.type_from_str(v[i]) for i in (0,1))
        d = Dictionnary.Dictionnary(t1,t2,k)
        for k_,v_ in v[2].items():
            k_,v_ = default_types.full_typize(k_),default_types.full_typize(v_)

            d[k_]=v_

        DICTIONNARY[k]=d

    for k,v in data["Fonctions"].items():
        if v[0]=='#':
            v=v[1:-1]
            v=_parser_.parse(v)

            FUNCTIONS[v[0][0]] = Functions.Function(v[0][0],v[0][2],v[0][4])

            args = v[1][0][1:-1].split(';')
            FUNCTIONS[v[0][0]].set_args_name(*args)
            i=2
            if v[i] == ['@GLOBAL']:
                FUNCTIONS[v[0][0]].set_global()
                i+=1
            if v[i] == ['@RESTRICT'] :
                FUNCTIONS[v[0][0]].set_restricted()
                i+=1
            if v[i][0][0]==v[i][0][-1]=='"':
                FUNCTIONS[v[0][0]].set_doc(v[i][0][1:-1])
                i+=1
            FUNCTIONS[v[0][0]].set_code(v[i:])
        else:
            v = v.split('\n')
            ph=v[0].replace(' ','')
            ph = ph.split(':')[1].split('⟶')
            app = Applications.Applications(k,*ph)

            ph=v[1].split(" ⟼ ")#dangerous split
            args = ph[0].split(';')
            app.set_args_name(*args)
            expr = _parser_.parse(ph[1]+'.')[0]
            app.set_expr(expr)
            FUNCTIONS[k]=app

    ALIAS = data["Alias"]

    return VARIABLES, DICTIONNARY,FUNCTIONS,ALIAS

def load_some(path,thing):
    data=file.get_json(path)

    for k,v in data["Variables"].items():
        if k != thing : continue

        t,value,flag='','',True
        for car in v:
            if car ==';' and flag:
                flag=False
                continue
            if flag:
                t+=car
            else:
                value+=car

        t = default_types.type_from_str(t)
        r = Variable.Variable(t,k)
        if type(t)==default_types.Parts:
            v = default_types.SET(t.typ)
            value = default_types.SET.listify(value)
            for elt in value:
                elt = default_types.full_typize(elt)
                elt = default_functions.convert(elt,t.typ)
                v.add(elt)
            

            r.set(v)
        elif type(t)==default_types.CrossSet:
            r.set(default_types.Tuple.from_str(value,t))
        else:
            r.set(t.from_str(value))
        return 'VAR',r

    for k,v in data['Dictionnaires'].items():
        if k != thing : continue
        t1,t2 = (default_types.type_from_str(v[i]) for i in (0,1))
        d = Dictionnary.Dictionnary(t1,t2,k)
        for k_,v_ in v[2].items():
            k_,v_ = default_types.full_typize(k_),default_types.full_typize(v_)

            d[k_]=v_

        return 'DICT',d

    for k,v in data["Fonctions"].items():
        if k != thing : continue
        if v[0]=='#':
            v=v[1:-1]
            v=_parser_.parse(v)

            r = Functions.Function(v[0][0],v[0][2],v[0][4])
            

            args = v[1][0][1:-1].split(';')
            r.set_args_name(*args)
            i=2
            if v[i] == ['@GLOBAL']:
                r.set_global()
                i+=1
            if v[i] == ['@RESTRICT'] :
                r.set_restricted()
                i+=1
            if v[i][0][0]==v[i][0][-1]=='"':
                r.set_doc(v[i][0][1:-1])
                i+=1
            r.set_code(v[i:])
            return 'FUNC',r
        else:
            v = v.split('\n')
            ph=v[0].replace(' ','')
            ph = ph.split(':')[1].split('⟶')
            app = Applications.Applications(k,*ph)

            ph=v[1].split(" ⟼ ")#dangerous split
            args = ph[0].split(';')
            app.set_args_name(*args)
            expr = _parser_.parse(ph[1]+'.')[0]
            app.set_expr(expr)
            return 'FUNC',app

    if thing in data['Alias']:
        r= load_some(path,data['Alias'][thing])
        r[1].name = thing
        return r
    
    raise

if __name__=='__main__':
    pass
import Callable
import POO
import Variable
import _parser_
from default_functions import *


def typize(l:list):
    for i,elt in enumerate(l):
        if type(elt)==list:
            typize(elt)
        else:
            r=default_types.full_typize(elt)
            if type(r) != type(None):
                l[i]=r

def create_evaluating_list(expr:list):
    ll=[]
    depth=0
    l_=[]
    for elt in expr:
        ll += transform(elt)
    for thing in ll:           
        if thing == '(':
            eval('l_'+'[-1]'*depth+'.append([])')
            depth +=1
        elif thing ==')':
            depth -=1
        else:
            eval('l_'+'[-1]'*depth+'.append(thing)')
    return l_

def exec_param_type(elt, variables, dictionary, function, alias, objet, ex):
    if not (elt.count('⟨') == elt.count('⟩')==2):
        raise error.WrongSyntax()
    l = elt.split('⟨')
    l = [elt.replace('⟩','') for elt in l]

    t = objet[l[0]]
    if not t.right_parameter(l[1]):raise

    t = t.get_representant(default_types.type_from_str(l[1],objet),objet)

    l_args = []
    la = ['']
    SET, string = 0, False
    for elt in l[2]:
        if elt == '"':
            string = not string
        elif elt == '{' and not string:
            SET += 1
        elif elt == '}' and not string:
            SET -= 1

        if elt == ';' and not string and SET == 0:
            la.append('')
        else:
            la[-1] += elt
    for elt in la:
        l = _parser_.parse_a_sentence(elt)
        l = create_evaluating_list(l)
        typize(l)
        if l: l_args.append(evaluate(l, variables, dictionary, function, {}, objet, ex))
    return POO.Instance(t,variables,dictionary,alias,function,objet,*l_args)

def eval_exists(ph:list[str],variables,dictionary,function,alias,objet,ex):
    if len(ph) < 6: raise error.WrongSyntax()
    if ph[0]!='∃':raise error.WrongSyntax()
    if ph[2]!='∊':raise error.WrongSyntax()
    if ph[4]!='|':raise error.WrongSyntax()

    Ens = create_Ens(ph,variables,dictionary,function,alias,objet)

    for thing in Ens:
        variables[ph[1]].set(thing)

        res = evaluate(ph[5:],variables,dictionary,function,alias,objet,ex)
        if type(res)!=default_types.B:
            raise error.TypeError_(ph[5:],'',stringify(type(res)),stringify(default_types.B))

        if res.v:
            del variables[ph[1]]
            return [default_types.B(True)]
    del variables[ph[1]]
    return [default_types.B(False)]

def create_Ens(ph:list[str],variables,dictionary,function,alias,objet):
    Ens:default_types.Iterable = default_types.EmptySet()

    if ph[1] in variables or ph[1] in dictionary or ph[1] in alias or ph[1] in objet or ph[1] in function:
        raise error.AlreadyExistsError(ph[1])

    if ph[3] not in variables and ph[3] not in alias:
        try:
            assert type(ph[3])==default_types.S or type(ph[3])==default_types.SET
            Ens = ph[3]
            ph[3]='!new'
        except Exception as err:
            raise error.UnknownObject(ph[3])

    if ph[3] in alias:
        ph[3] = alias[ph[3]].ptr

    if ph[3]!='!new' and (variables[ph[3]].type == default_types.S or type(
            variables[ph[3]].type) == default_types.Parts):
        Ens = variables[ph[3]].get()
    elif ph[3]!='!new':
        raise error.IterationError(default_types.stringify(variables[ph[3]].type))

    if Ens is None:raise error.WrongSyntax()

    if type(Ens) == default_types.S:
        variables[ph[1]] = Variable.Variable(default_types.S, ph[1])
    else:
        Ens: default_types.AbstractSet
        variables[ph[1]] = Variable.Variable(Ens.type, ph[1])

    return Ens

def eval_forall(ph:list[str],variables,dictionary,function,alias,objet,ex):
    if len(ph) < 6: raise error.WrongSyntax()
    if ph[0]!='∀':raise error.WrongSyntax()
    if ph[2]!='∊':raise error.WrongSyntax()
    if ph[4]!=':':raise error.WrongSyntax()

    Ens = create_Ens(ph,variables,dictionary,function,alias,objet)

    for thing in Ens:
        variables[ph[1]].set(thing)

        res = evaluate(ph[5:],variables,dictionary,function,alias,objet,ex)
        if type(res)!=default_types.B:
            raise error.TypeError_(ph[5:],'',stringify(type(res)),stringify(default_types.B))

        if not res.v:
            del variables[ph[1]]
            return [default_types.B(False)]
    del variables[ph[1]]
    return [default_types.B(True)]

def evaluate(l:list,variables,dictionary,function,alias,objet,ex,k=0):#,stdout=sys.__stdout__):
    simpl(l)
    assert type(k)==int
    for i,elt in enumerate(l):
        if type(elt)==list:
            evaluate(elt,variables,dictionary,function,alias,objet,ex,k+1)
            if len(l[i])==1:l[i]=l[i][0]
        elif type(elt)==str and elt in variables:
            l[i] = variables[elt].get()
        elif type(elt)==str and elt in alias:
            l[i] = variables[alias[elt].ptr].get()
        elif type(elt)==str and elt in objet:
            l[i] = objet[elt]
        elif type(elt)==str and elt[0]=='{' and elt[-1]=='}':
            l[i]=evaluate_sets(elt,variables,dictionary,alias,function,objet,ex)
        elif type(elt)==str and elt[0]=='⟦' and elt[-1]=='⟧':
            l[i] = evaluate_int(elt,variables,dictionary,alias,function,objet,ex)
        elif type(elt)==str and elt == '∃':
            l[i:] = eval_exists(l[i:],variables, dictionary, function, alias, objet, ex)
        elif type(elt)==str and elt == '∀':
            l[i:] = eval_forall(l[i:],variables, dictionary, function, alias, objet, ex)
        elif type(elt) == str and (elt not in _parser_.op and elt !=';' and elt not in _parser_.t):
            if elt!='' and elt[0] == '·'and i!=0:
                l[i-1]=exec_method(l[i-1],elt[1:],variables,dictionary,alias,function,objet, ex)
                del l[i]
            elif first_occurs(elt,'$','·')=='·':
                l[i]=meth(elt,variables,dictionary,alias,function,objet,ex)
            else:
                if elt.count('⟨')==2:
                    l[i] = exec_param_type(elt,variables,dictionary,function,alias,objet,ex)
                else:
                    l[i] = exec_func_dict(elt,variables,dictionary,function,alias,objet,ex)#,stdout=stdout)
    for i,elt in enumerate(l):
        if type(elt) != str: continue
        if elt == '^':
            l[i-1] = l[i-1]**l[i+1]
            del l[i]
            del l[i]

    #execution * et / en m^ temps !! 
    
    i=0
    while i < len(l):
        elt=l[i]
        if type(elt)!=str:
            i+=1
            continue
        if elt == '×':
            l[i-1]=l[i-1]*l[i+1]
            del l[i]
            del l[i]
        elif elt == '÷':
            l[i-1]=l[i-1]/l[i+1]
            del l[i]
            del l[i]
        else:
            i+=1

    i=0
    while i < len(l):
        elt=l[i]
        if type(elt)!=str:
            i+=1
            continue
        if elt == '+':
            if i == 0:
                del l[i]
            else:
                try:
                    l[i-1]=l[i-1]+l[i+1]
                    del l[i]
                    del l[i]
                except AttributeError:
                    raise error.UnsupportedOperation('+',default_types.stringify(type(l[i-1])),default_types.stringify(type(l[i+1])))
        elif elt == '-':
            if i == 0 or type(l[i-1])==str:
                try:
                    l[i+1]=-l[i+1]
                    del l[i]
                except AttributeError:
                    raise error.UnsupportedOperation('-',default_types.stringify(type(l[i+1])))
            else:
                try:
                    l[i-1]=l[i-1]-l[i+1]
                    del l[i]
                    del l[i]
                except AttributeError:
                    raise error.UnsupportedOperation('-',default_types.stringify(type(l[i-1])),default_types.stringify(type(l[i+1])))
        else:
            i+=1


    traiter(l,'|',lambda b1,b2:b1.div(b2))
    traiter(l,'⩾',lambda b1,b2 : b1 >= b2)
    traiter(l,'>',lambda b1,b2 : b1 > b2)
    traiter(l,'⩽',lambda b1,b2 : b1 <= b2)
    traiter(l,'<',lambda b1,b2 : b1 < b2)
    traiter(l,'⋃',lambda b1,b2 :b1.union(b2))
    traiter(l,'⋂',lambda b1,b2 : b1.inter(b2))
    traiter(l,'∖',lambda b1,b2 : b1.setminus(b2))

    traiter(l,'∊',lambda b1,b2: IN(b1,b2))
    traiter(l,'⊆',lambda b1,b2: INCLUDE(b1,b2,objet))

    traiter(l,'=',lambda b1,b2 : default_types.B(b1 == b2) if type(b1==b2)==bool else b1==b2)
    traiter(l,'≠',lambda b1,b2 : b1 != b2)
    traiter(l,'∧',lambda b1,b2:b1 and b2)
    traiter(l,'∨',lambda b1,b2:b1 or b2)
    traiter(l,'⊕',lambda b1,b2:b1.xor(b2))

    for i,elt in enumerate(l):
        if type(elt) != str: continue
        if elt == '¬':
            try:
                l[i] = default_types.B(l[i+1].__not__())
                del l[i+1]
            except AttributeError:
                raise error.UnsupportedOperation("¬",default_types.stringify(type(l[i+1])))
    
    for i in range(len(l)-1,-1,-1):
        elt=l[i]
        if type(elt) != str:continue
        if elt == '⇒':
            try:
                l[i-1] = l[i-1].impl(l[i+1])
                del l[i]
                del l[i]
            except AttributeError:
                error.UnsupportedOperation('⇒',default_types.stringify(type(l[i-1])),default_types.stringify(type(l[i+1])))

    traiter(l,'⇔',lambda b1,b2:b1.equiv(b2))
    
    if k==0:
        if len(l)==1 and type(l[0])==list and ';' in l[0]:
            l_=[]
            for element in l[0]:
                if type(element) == str and element==';':continue
                l_.append(element)
            sc = [type(elt) for elt in l_]
            for i,elt in enumerate(sc):
                if elt==default_types.SET:
                    sc[i]= default_types.Parts(l_[i].type)
                elif "Instance" in str(elt):
                    sc[i] = l_[i].type
            l[0]=default_types.Tuple(l_,default_types.CrossSet(*sc))
    if k==0:
        return l[0] if len(l)==1 else 'err' 

def evaluate_int(elt,variables,dictionary,function,alias,objet,ex):
    l1 = _parser_.parse(elt[1:-1].split(';')[0]+'.')
    l2 = _parser_.parse(elt[1:-1].split(';')[1]+'.')
    l1,l2 = create_evaluating_list(l1),create_evaluating_list(l2)
    typize(l1)
    typize(l2)
    return default_types.ZIntervalle(evaluate(l1,variables,dictionary,function,alias,objet,ex),evaluate(l2,variables,dictionary,function,alias,objet,ex))

def traiter(l,car,fct):
    """cas opérateur associatif a gauche"""
    i=0
    while i < len(l):
        elt=l[i]
        if type(elt) != str:
            i+=1
            continue
        if elt == car:
            try:
                l[i-1] = fct(l[i-1],l[i+1])
                del l[i]
                del l[i]
            except AttributeError:
                raise error.UnsupportedOperation(car,default_types.stringify(type(l[i-1])),default_types.stringify(type(l[i+1])))
        else:
            i+=1

def transform(ch:str):
    #'(2+3;7)' -> ['(','2','+','3',';','7',')']
    l=['']
    S=0;s=False;chevron=0;dbrak = False
    for car in ch:
        if car =='{' and not s:
            if l[-1]!='':l.append('')
            S+=1
        if car == '⟦' and not dbrak:
            dbrak=True
        if car == '⟧' and dbrak:
            dbrak=False
        if car =='}' and not s : S-=1
        if car =='"':s=not s
        if car =='⟨':chevron+=1
        if car =='⟩':chevron-=1

        if car in _parser_.op or car in "();":
            if S !=0 or chevron or dbrak or s:
                l[-1]+=car
                continue
            if car ==';':
                if S!=0 or s:
                    l[-1]+=car
                    continue
            if l[-1]=='':
                l[-1]=car
            else:
                l.append(car)
            l.append('')
        else:
            l[-1]+=car
    if l[-1]=='':
        del l[-1]
    return l

def simpl(l:list):
    for i,elt in enumerate(l):
        if type(elt) != str:continue
        
        if elt =='×' and 0<i<len(l)-1:            
            if check_0(l[i-1]):
                del l[i]
                del l[i]
            elif check_0(l[i+1]):
                del l[i-1]
                del l[i-1]
        
        elif elt == '+'and 0<i<len(l)-1:            
            if check_0(l[i-1]):
                del l[i-1]
                del l[i-1]
            elif check_0(l[i+1]):
                del l[i]
                del l[i]
        
        elif elt == '∧' and 0<i<len(l)-1:            
            if type(l[i - 1]) == default_types.B and l[i - 1].v == False:
                del l[i]
                del l[i]
            elif type(l[i + 1])==default_types.B and l[i + 1].v == False:
                del l[i-1]
                del l[i-1]

        elif elt == '∨' and 0<i<len(l)-1:            
            if type(l[i - 1]) == default_types.B and l[i - 1].v == True:
                del l[i]
                del l[i]
            elif type(l[i + 1])==default_types.B and l[i + 1].v == True:
                del l[i-1]
                del l[i-1]
        
        elif elt  == '⇒':
            if type(l[i - 1]) == default_types.B and l[i - 1].v == False:
                del l[i]
                del l[i]
                l[i-1] = default_types.B(True)
            elif type(l[i + 1])==default_types.B and l[i + 1].v == True:
                del l[i-1]
                del l[i-1]

def evaluate_sets(ch,variables,dictionary,alias,functions,objet,ex):
    if '∊' in ch:
        return set_comprehension(ch,variables,dictionary,alias,functions,objet,ex)

    s=set()
    for elt in default_types.SET.listify(ch):
        l_elt = _parser_.parse_a_sentence(elt)
        eval_l = create_evaluating_list(l_elt)
        typize(eval_l)
        res = evaluate(eval_l,variables,dictionary,functions,alias,objet,ex)
        s.add(res)

    return convert_to_set(s)

def exec_func_dict(ch:str,variables,dictionary,function,alias,objet,ex):#,stdout):
    f,a='',''
    flag=True#complete func name
    if '$' in ch : 
        if '⟨' in ch:
            raise error.WrongSyntax()

        ch_ =""

        for car in ch:
            if car != '$':
                ch_ += car
            elif flag:
                ch_ += '('
                flag=False
            else:
                ch_ +=','
        if '('in ch_:
            ch_ += ')'
        else:
            ch_ += '()'

        p1 =True
        for car in ch_:
            if car =='(':p1=False
            if p1:f+=car
            else:a+=car

        if f in dictionary:
            l_=[]
            for elt in a[1:-1].split(','):
                if default_types.recognize_type(elt):
                    l_.append('"'+elt+'"')
                elif elt in variables:
                    l_.append(variables[elt].get()) 
                else:
                    _l_ = [elt]
                    typize(_l_)
                    l_.append(_l_[0])
            if not len(l_)==1:raise error.WrongSyntax()
            return dictionary[f][l_[0]]
        if not((f in function and type(function[f])!=Callable.Applications) or f in DEFAULT_FUNCTIONS):
            raise error.WrongSyntax()
        l_=[]

        if f in function:
            function[f].right_access(ex)
            for elt in a[1:-1].split(','):
                if elt in variables:
                    l_.append(elt) 
                elif elt=='':
                    continue
                else:
                    raise
            return ex.func_call(f,*l_)
        
        #DEFAULT_FUNCTION
        for elt in a[1:-1].split(','):
            if default_types.recognize_type(elt):
                l_.append('"'+elt+'"')
            elif elt in variables:
                l_.append(f"variables['{elt}'].get()") 
            elif elt in dictionary:
                l_.append(f"dictionary[elt]")
            elif elt in function:
                l_.append(f"function[elt]")
            elif elt in objet:
                l_.append(f"objet[elt]")
            elif elt in DEFAULT_FUNCTIONS:
                l_.append(elt)
            elif elt=='':
                continue
            else:
                raise
        
        a = '('+','.join(l_)+')'
        return eval(f+a)

    if not (ch.count('⟨') == ch.count('⟩')==ch.count('$')+1==1 and ch[-1]=='⟩'):
        raise error.WrongSyntax()
    f,a = ch[:-1].split('⟨')
    if not((f in function and type(function[f])==Callable.Applications) or f  in objet):
        raise error.WrongSyntax()
    f=function.get(f,f)
    l_args = []
    la=['']
    SET,string=0,False
    for elt in a:
        if elt =='"':
            string=not string
        elif elt=='{'and not string:
            SET +=1
        elif elt=='}' and not string:
            SET-=1
        
        if elt ==';' and not string and SET==0:
            la.append('')
        else:
            la[-1]+=elt

    for elt in la:
        l=_parser_.parse_a_sentence(elt)
        l=create_evaluating_list(l)
        typize(l)
        if l:l_args.append(evaluate(l,variables,dictionary,function,{},objet,ex))
    if f in objet:
        for elt in _parser_.t:
            if elt in l_args:
                return ch
        return POO.Instance(objet[f],variables,dictionary,alias,function,objet,*l_args)
    return f(*l_args)

def exec_method(obj:default_types.Types|POO.Object,ch:str,variables,dictionnaries,alias,functions,objet,ex,static=False):
    l = ch.split('$')
    if l[-1]=='':l.pop()
    f=l[0]
    a=[]
    for elt in l[1:]:
        if elt in variables :
            a.append(variables[elt].get())
        elif elt[0]=="⟦":
            l = elt[1:-1].split(";")
            assert len(l)==2
            binf = ex.eval_expr(l[0])
            bsup = ex.eval_expr(l[1])
            a.append(default_types.ZIntervalle(binf,bsup))
        else:raise

    if not static: return obj.call(f,*a)
    return obj.static_call(f,variables,dictionnaries,alias,functions,objet,*a)

def meth(elt,variables,dictionnaries,alias,functions,objet,ex):
    #Refaire !
    l=elt.split('·')
    static=False
    if l[0] == 'me':
        l[0]=variables[l[0]]
    elif l[0] in variables:
        l[0]=variables[l[0]].get()
    elif l[0] in dictionnaries:
        l[0]=dictionnaries[l[0]]
    elif l[0] in alias:
        l[0] = alias[l[0]].ptr
        l[0]=variables[l[0]].get()
    elif l[0]in objet:
        l[0] = objet[l[0]]
        static=True
    else:
        raise
    if len(l)!=2:
        raise error.WrongSyntax()
    return exec_method(l[0],l[1],variables,dictionnaries,alias,functions,objet,ex,static)

def first_occurs(ch,car1,car2):
    for elt in ch:
        if elt ==car1:return car1
        elif elt == car2:return car2
    return False

def check_0(thing):
    return (type(thing)in default_types.NUMERAL and type(thing) != default_types.C and thing.value == 0) or (type(thing)in default_types.NUMERAL and type(thing) == default_types.C and thing.re == thing==0)

def define_set_forall(l, variables, dictionary, alias, functions, objet, ex):

    l_ = [[]]
    for elt in l:
        if elt == ';':
            l_.append([])
        else:
            l_[-1].append(elt)
    l=l_

    if len(l) != 2:
        raise error.WrongSyntax()
    if len(l[1])!=3 or l[1][1] != '∊':
        raise error.WrongSyntax()

    if l[1][0] in variables or l[1][0] in dictionary or l[1][0] in alias or l[1][0] in objet or l[1][0] in functions:
        raise error.WrongSyntax()

    Ens = evaluate([l[1][2]], variables, dictionary, alias, functions, objet, ex)

    if isinstance(Ens,default_types.AbstractSet):
        variables[l[1][0]] = Variable.Variable(Ens.type,l[1][0])
    elif isinstance(Ens,default_types.Iterable):
        variables[l[1][0]] = Variable.Variable(type(Ens), l[1][0])
    else:
        raise error.IterationError(type(Ens))

    s = set()
    for elt in Ens:
        l_ = create_evaluating_list(l[0])
        typize(l_)

        variables[l[1][0]].set(elt)

        res = evaluate(l_, variables, dictionary, alias, functions, objet, ex)
        s.add(res)

    del variables[l[1][0]]
    return convert_to_set(s)

def define_set_suchthat(l, variables, dictionary, alias, functions, objet, ex):
    if '│' not in l:
        raise error.WrongSyntax()

    if l[0] in variables or l[0] in dictionary or l[0] in alias or l[0] in objet or l[0] in functions:
        raise error.WrongSyntax()

    l_ = [[]]
    for elt in l:
        if elt == '│':
            l_.append([])
        else:
            l_[-1].append(elt)

    l=l_
    if len(l) != 2:
        raise error.WrongSyntax()

    if len(l[0])!=3 or l[0][1] != '∊':
        raise error.WrongSyntax()

    Ens = evaluate([l[0][2]],variables,dictionary,alias,functions,objet,ex)


    if isinstance(Ens,default_types.AbstractSet):
        variables[l[0][0]] = Variable.Variable(Ens.type,l[0][0])
    else:
        return default_types.EmptySet()

    s=set()
    for elt in Ens:
        l_ = create_evaluating_list(l[1])
        typize(l_)

        variables[l[0][0]].set(elt)

        res= evaluate(l_,variables,dictionary,alias,functions,objet,ex)
        if type(res) != default_types.B:
            raise error.TypeError#change here : generic type error
        res:default_types.B
        if res.v:
            s.add(elt)

    del variables[l[0][0]]
    return convert_to_set(s)


def set_comprehension(ch,variables,dictionary,alias,functions,objet,ex):
    #│

    if ch == '' or ch[0]!='{' or ch[-1]!='}':
        raise error.WrongSyntax()

    l = _parser_.parse(ch[1:-1] + '.', objet)[0]

    if '│' in l:
        return define_set_suchthat(l,variables,dictionary,alias,functions,objet,ex)
    else:
        return define_set_forall(l,variables,dictionary,alias,functions,objet,ex)

def convert_to_set(s):
    t = {type(elt) for elt in s}
    for typ in default_types.NUMERAL:
        if len(t) == 1: break
        if typ in t:
            t = {elt if elt != typ else default_types.INCLUSIONS[typ][0] for elt in t}

    if len(t) != 1:
        raise error.WrongSyntax()

    t = list(t)
    if t[0] == default_types.Tuple:
        t[0] = list(s)[0].type

    s = {convert(elt, t[0]) for elt in s}
    S = default_types.SET(t[0])
    for elt in s:
        S.add(elt)
    return S
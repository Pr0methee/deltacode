import default_types,_parser_,Applications,error
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

def evaluate(l:list,variables,dictionary,function,alias,ex,k=0):#,stdout=sys.__stdout__):
    simpl(l)
    assert type(k)==int
    for i,elt in enumerate(l):
        if type(elt)==list:
            evaluate(elt,variables,dictionary,function,alias,ex,k+1)
            if len(l[i])==1:l[i]=l[i][0]
        elif type(elt)==str and elt in variables:
            l[i] = variables[elt].get()
        elif type(elt)==str and elt in alias:
            l[i] = variables[alias[elt]].get()
        elif type(elt)==str and elt[0]=='{' and elt[-1]=='}':
            l[i]=evaluate_sets(elt,variables,dictionary,alias,function,ex)
        elif type(elt) == str and elt not in _parser_.op:
            if '·' in elt:l[i]=meth(elt,variables,dictionary,alias,ex)
            else:l[i] = exec_func_dict(elt,variables,dictionary,function,ex)#,stdout=stdout)
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
            if i == 0:
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
    #print(l,'is going to apply \setminus')
    traiter(l,'∖',lambda b1,b2 : b1.setminus(b2))
    #print('after :',l)

    traiter(l,'=',lambda b1,b2 : b1 == b2)
    traiter(l,'≠',lambda b1,b2 : b1 != b2)
    #traiter(l,'∊',lambda b1,b2 : IN(b1,b2))
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

            l[0]=default_types.Tuple(l_,default_types.CrossSet(*sc))
    if k==0:
        return l[0] if len(l)==1 else 'err' 

def traiter(l,car,fct):
    "cas opérateur associatif a gauche"
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
            if S !=0 or chevron or dbrak:
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
            if (type(l[i-1])in default_types.NUMERAL and type(l[i-1]) != default_types.C and l[i-1].value == 0) or (type(l[i-1])in default_types.NUMERAL and type(l[i-1]) == default_types.C and l[i-1].re == l[i-1]==0):
                del l[i]
                del l[i]
            elif (type(l[i+1])in default_types.NUMERAL and type(l[i+1]) != default_types.C and l[i+1].value == 0) or (type(l[i-1])in default_types.NUMERAL and type(l[i+1]) == default_types.C and l[i+1].re == l[i+1]==0):
                del l[i-1]
                del l[i-1]
        
        elif elt == '+'and 0<i<len(l)-1:            
            if (type(l[i-1])in default_types.NUMERAL and type(l[i-1]) != default_types.C and l[i-1].value == 0) or (type(l[i-1])in default_types.NUMERAL and type(l[i-1]) == default_types.C and l[i-1].re == l[i-1]==0):
                del l[i-1]
                del l[i-1]
            elif (type(l[i+1])in default_types.NUMERAL and type(l[i+1]) != default_types.C and l[i+1].value == 0) or (type(l[i-1])in default_types.NUMERAL and type(l[i+1]) == default_types.C and l[i+1].re == l[i+1]==0):
                del l[i]
                del l[i]
        
        elif elt == '∧' and 0<i<len(l)-1:            
            if (type(l[i-1]) == default_types.B and l[i-1].v == False):
                del l[i]
                del l[i]
            elif (type(l[i+1])==default_types.B and l[i+1].v == False) :
                del l[i-1]
                del l[i-1]

        elif elt == '∨' and 0<i<len(l)-1:            
            if (type(l[i-1]) == default_types.B and l[i-1].v == True):
                del l[i]
                del l[i]
            elif (type(l[i+1])==default_types.B and l[i+1].v == True) :
                del l[i-1]
                del l[i-1]
        
        elif elt  == '⇒':
            if (type(l[i-1]) == default_types.B and l[i-1].v == False):
                del l[i]
                del l[i]
                l[i-1] = default_types.B(True)
            elif (type(l[i+1])==default_types.B and l[i+1].v == True) :
                del l[i-1]
                del l[i-1]

def evaluate_sets(ch,variables,dictionary,alias,functions,ex):
    s=set()
    for elt in default_types.SET.listify(ch):
        l_elt = _parser_.parse_a_sentence(elt)
        eval_l = create_evaluating_list(l_elt)
        typize(eval_l)
        res = evaluate(eval_l,variables,dictionary,functions,alias,ex)
        s.add(res)

    t = {type(elt) for elt in s}
    for typ in default_types.NUMERAL:
        if len(t)==1:break
        if typ in t:
            t = {elt if elt != typ else default_types.INCLUSIONS[typ][0] for elt in t}
    
    if len(t)!=1:
        raise error.WrongSyntax()

    t=list(t)
    if t[0]==default_types.Tuple:
        t[0]=list(s)[0].type   
    
    s={convert(elt,t[0])for elt in s}
    S = default_types.SET(t[0])
    for elt in s:
        S.add(elt)
    return S

def exec_func_dict(ch:str,variables,dictionary,function,ex):#,stdout):
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
        if not((f in function and type(function[f])!=Applications.Applications) or f in DEFAULT_FUNCTIONS):
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
            
        for elt in a[1:-1].split(','):
            if default_types.recognize_type(elt):
                l_.append('"'+elt+'"')
            elif elt in variables:
                l_.append(f"variables['{elt}'].get()") 
            elif elt in dictionary:
                l_.append(f"dictionary[elt]")
            elif elt in function:
                l_.append(f"function[elt]")
            elif elt=='':
                continue
            else:
                raise
        
        a = '('+','.join(l_)+')'
        return eval(f+a)

    if not (ch.count('⟨') == ch.count('⟩')==ch.count('$')+1==1 and ch[-1]=='⟩'):
        raise error.WrongSyntax()
    f,a = ch[:-1].split('⟨')
    if not(f in function and type(function[f])==Applications.Applications):
        raise error.WrongSyntax()
    f=function[f]
    l_args = []
    for elt in a.split(';'):
        l=_parser_.parse_a_sentence(elt)
        l=create_evaluating_list(l)
        typize(l)
        if l !=[]:l_args.append(evaluate(l,variables,dictionary,function,{},ex))
    return f(*l_args)

def exec_method(obj:default_types.Types,ch:str,variables,ex):
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

    return obj.call(f,*a)

def meth(elt,variables,dictionnaries,alias,ex):
    l=elt.split('·')
    if len(l)!=2:
        raise error.WrongSyntax()
    if l[0] in variables:
        l[0]=variables[l[0]].get()
    elif l[0] in dictionnaries:
        l[0]=dictionnaries[l[0]]
    elif l[0] in alias:
        l[0] = alias[l[0]]
        l[0]=variables[l[0]].get()
    else:raise
    return exec_method(l[0],l[1],variables,ex)

if __name__ == '__main__':
    l=create_evaluating_list(['10'])
    print(l)
    typize(l)
    print(l)

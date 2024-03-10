import default_types,_parser_,Functions
from default_functions import *

def typize(l:list):
    for i,elt in enumerate(l):
        if type(elt)==list:
            typize(elt)
        else:
            r=default_types.attribute_type(elt)
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

def evaluate(l:list,variables,dictionary,function,alias,k=0):#,stdout=sys.__stdout__):
    simpl(l)
    assert type(k)==int
    for i,elt in enumerate(l):
        if type(elt)==list:
            evaluate(elt,variables,dictionary,alias,function,k+1)
            if len(l[i])==1:l[i]=l[i][0]
        elif type(elt)==str and elt in variables:
            l[i] = variables[elt][1]
        elif type(elt)==str and elt in alias:
            l[i] = variables[alias[elt]][1]
        elif type(elt)==str and elt[0]=='{' and elt[-1]=='}':
            l[i]=evaluate_sets(elt,variables,dictionary,alias,function)
        elif type(elt) == str and elt not in _parser_.kw:
            l[i] = exec_func_dict(elt,variables,dictionary,function)#,stdout=stdout)

    for i,elt in enumerate(l):
        if type(elt) != str: continue
        if elt == '^':
            l[i-1] = l[i-1]**l[i+1]
            del l[i]
            del l[i]

    #execution * et / en m^ temps !! 
    for i,elt in enumerate(l):
        if type(elt) != str: continue
        if elt == '×':
            l[i-1] = l[i-1]*l[i+1]
            del l[i]
            del l[i]
        elif elt == '÷':
            l[i-1] = l[i-1]/l[i+1]
            del l[i]
            del l[i]

    for i,elt in enumerate(l):
        if type(elt) != str: continue
        if elt == '+':
            if i==0:
                del l[i]
            else:
                l[i-1] = l[i-1]+l[i+1]
                del l[i]
                del l[i]
        elif elt == '-':
            if i==0:
                del l[i]
                l[i]=-l[i]
            else:
                l[i-1] = l[i-1]-l[i+1]
                del l[i]
                del l[i]

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
            l[i] = default_types.B(l[i+1].__not__())
            del l[i+1]
    
    for i in range(len(l)-1,-1,-1):
        elt=l[i]
        if type(elt) != str:continue
        if elt == '⇒':
            l[i-1] = l[i-1].impl(l[i+1])
            del l[i]
            del l[i]

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
    for i, elt in enumerate(l):
        if type(elt) != str:continue
        if elt == car:
            l[i-1] = fct(l[i-1],l[i+1])
            del l[i]
            del l[i]

def transform(ch:str):
    #'(2+3;7)' -> ['(','2','+','3',';','7',')']
    l=['']
    S=0;s=False;chevron=0
    for car in ch:
        if car =='{' and not s:
            if l[-1]!='':l.append('')
            S+=1
        if car =='}' and not s : S-=1
        if car =='"':s=not s
        if car =='⟨':chevron+=1
        if car =='⟩':chevron-=1

        if car in '∃∊+-×÷∧∨¬⇔⇒;()':
            if S !=0:
                l[-1]+=car
                continue
            if car ==';':
                if S!=0 or s:
                    l[-1]+=car
                    continue
            if chevron !=0:
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

def evaluate_sets(ch,variables,dictionary,alias,functions):
    s=set()
    for elt in default_types.SET.listify(ch):
        l_elt = _parser_.parse_a_sentence(elt)
        eval_l = create_evaluating_list(l_elt)
        typize(eval_l)
        res = evaluate(eval_l,variables,dictionary,functions,alias)
        s.add(res)

    t = {type(elt) for elt in s}
    for typ in default_types.NUMERAL:
        if len(t)==1:break
        if typ in t:
            t = {elt if elt != typ else default_types.INCLUSIONS[typ][0] for elt in t}
    
    assert len(t)==1

    t=list(t)
    if t[0]==default_types.Tuple:
        t[0]=list(s)[0].type   
    
    s={convert(elt,t[0])for elt in s}
    S = default_types.SET(t[0])
    for elt in s:
        S.add(elt)
    return S

def exec_func_dict(ch:str,variables,dictionary,function):#,stdout):
    f,a='',''
    flag=True#complete func name
    if '$' in ch : 
        assert '⟨' not in ch

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
                    l_.append(variables[elt][1]) 
                else:
                    _l_ = [elt]
                    typize(_l_)
                    l_.append(_l_[0])
            assert len(l_)==1
            return dictionary[f][1][l_[0]]
        assert (f in function and type(function[f])!=Functions.Applications) or f in DEFAULT_FUNCTIONS
        l_=[]

        for elt in a[1:-1].split(','):
            if default_types.recognize_type(elt):
                l_.append('"'+elt+'"')
            elif elt in variables:
                l_.append(f"variables['{elt}'][1]") 
            elif elt=='':
                continue
            else:
                raise
        
        a = '('+','.join(l_)+')'
        if f in function:
            f='function["'+f+'"]'
        return eval(f+a)

    assert ch.count('⟨') == ch.count('⟩')==ch.count('$')+1==1 and ch[-1]=='⟩'
    f,a = ch[:-1].split('⟨')
    a=a.replace(';',',')
    assert f in function and type(function[f])==Functions.Applications
    f="function['"+f+"']"
    l_args = []
    for elt in a.split(','):
        l=_parser_.parse_a_sentence(elt)
        l=create_evaluating_list(l)
        typize(l)
        if l !=[]:l_args.append(evaluate(l,variables,dictionary,function,{}))
    a = ','.join(f"l_args[{i}]" for  i in range(len(l_args)))
    return eval(f+'('+a+')')

if __name__ == '__main__':
    (create_evaluating_list(['"a"']))
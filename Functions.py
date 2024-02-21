from default_types import recognize_type, type_from_str, attribute_type
import default_types,_parser_
from default_functions import convert

class Function:
    def __init__(self,e1,e2):
        assert recognize_type(e1) and recognize_type(e2)
        self.t = (type_from_str(e1),type_from_str(e2))
        self.code=['']
    
    def set(self,code):
        #code should be under the form [arg,expr]
        self.code=code
    
    def __call__(self,*args):
        pass

class FunctionExecutor:
    def __init__(self):
        pass
    
    def set_args(self,n,t):
        self.var=[n,t]
    
    def set_return_type(self,t):
        self.rtype=t
    
    def set_expr(self,expr):
        self.expr=expr
    
    def evaluate(self,v):
        try:
            r = convert(v,self.var[1])
            if len(self.var)==2:self.var.append(r)
            else:self.var[1]=r
        except:
            raise

    
    def eval_expr(self,l:list[str]):
        l_=[]
        for i,elt in enumerate(l):
            res=attribute_type(elt)
            if type(res) != type(None):
                l_.append(res)
            else:
                l_.append(elt)


        if len(l_) == 1 and type(l_[0]) != str:
            return l_[0]
        
        if len(l)==1 and l[0][0]=='{' and l[0][-1]=='}':
            try:   
                res=evaluate_sets(l[0],self.VARIABLES,self.DICTIONARY)#,self.FUNCTIONS)
                return res
            except Exception as err:
                print(err)
                return 'err'
        else:
            l_=create_evaluating_list(l)
            typize(l_)
            try:
                res=evaluate(l_,self.VARIABLES,self.DICTIONARY)#,stdout=StdRedirector(self.echo))
                return res
            except ZeroDivisionError:
                return '0err'
            #except Exception as err:
            #    print(err)

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


def typize(l:list):
    for i,elt in enumerate(l):
        if type(elt)==list:
            typize(elt)
        else:
            r=default_types.attribute_type(elt)
            if type(r) != type(None):
                l[i]=r

def evaluate(l:list,variables,dictionary,k=0):#,stdout=sys.__stdout__):
    simpl(l)
    assert type(k)==int
    for i,elt in enumerate(l):
        #print(elt)
        if type(elt)==list:
            evaluate(elt,variables,k+1)
            if len(l[i])==1:l[i]=l[i][0]
        elif type(elt)==str and elt in variables:
            l[i] = variables[elt][1]
        elif type(elt)==str and elt[0]=='{' and elt[-1]=='}':
            l[i]=evaluate_sets(elt,variables,dictionary)
    #print(l)
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
    S=0;s=False
    for car in ch:
        if car =='{' and not s:
            if l[-1]!='':l.append('')
            S+=1
        if car =='}' and not s : S-=1
        if car =='"':s=not s

        if car in '∃∊+-×÷∧∨¬⇔⇒;()':
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

def evaluate_sets(ch,variables,dictionary):
    s=set()
    for elt in default_types.SET.listify(ch):
        l_elt = _parser_.parse_a_sentence(elt)
        eval_l = create_evaluating_list(l_elt)
        typize(eval_l)
        res = evaluate(eval_l,variables,dictionary)
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

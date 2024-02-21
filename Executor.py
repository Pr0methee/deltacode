import tkinter.scrolledtext as scrolledtext
import _parser_, default_types
from default_functions import *
from tkinter import *
import error

class StdRedirector:
    def __init__(self, text_widget:scrolledtext.ScrolledText):
        self.text_widget = text_widget

    def write(self, message):#enlever le disabled
        self.text_widget.config(state='normal')
        self.text_widget.insert(END,message)
        self.text_widget.see(END)
        self.text_widget.config(state='disabled')
        

    def go(self,*args):
        self.ok=True

    def readline(self,*args):
        end =self.text_widget.index(str(self.last_line())+'.end')
        self.ok =False
        self.text_widget.config(state='normal')
        self.text_widget.bind('<Return>',self.go)
        while not self.ok:
            self.text_widget.master.update()
        self.text_widget.update()
        self.text_widget.update_idletasks()
        self.text_widget.config(state='disabled')
        return self.text_widget.get(end,'end-1c')
    
    def last_line(self):
        l=self.text_widget.index('end').split('.')[0]
        l=int(l)-1
        return l



class Executor:
    def __init__(self,echo:scrolledtext.ScrolledText):
        self.VARIABLES = {}
        self.ALIAS = {}
        self.FUNCTIONS = {}
        self.DICTIONARY = {}
        self.ASSERTS = []
        self.BOUCLE=False
        self.echo=echo
        self.ECHO=True
    
    def create_variable(self,name,typ,way='∊'):
        if name in self.VARIABLES:
            raise error.AlreadyExistsError(name)
            self.raise_error("AlreadyExistsError",f"Variable {name} already exists, We can't create it again.")
            return
        
        if not(default_types.recognize_type(typ)):
            self.raise_error("TypeError", f"{typ} can't be understood as a type.")
            return
        if not valid_name(name):
            self.raise_error('UnvalidNameError', f"Unvalid name for a variable {name}")
            return

        if way =='∊':
            self.VARIABLES[name]=[default_types.type_from_str(typ),None]
        else:
            self.VARIABLES[name]=[default_types.Parts(default_types.type_from_str(typ)),None]
        self.echo_dec(name,typ,way)

    def affect(self,name,expr:list[str]):
        if name not in self.VARIABLES and name not in self.ALIAS:
            self.raise_error("NameError",f"Unable to affect value to {name}, it does not exist.")
            return
        
        if name in self.ALIAS:
            name=self.ALIAS[name]

        value = self.eval_expr(expr.copy())
        if type(value)==str :
            if value == 'err':
                self.raise_error('EvaluatingError','')
                return
            elif value == '0err':
                self.raise_error('ZeroDivisionError',f'Trying to divide by zero while evaluating {"".join(expr)}')
                return
        try:
            value = convert(value,self.VARIABLES[name][0])
        except Exception as err:
            if type(self.VARIABLES[name][0])==default_types.CrossSet or type(self.VARIABLES[name][0]) == default_types.Parts:
                reqtyp=self.VARIABLES[name][0]
            else:
                reqtyp = default_types.TYPES_[self.VARIABLES[name][0]]

            if type(value) == default_types.Tuple:
                gettyp = value.type
            elif type(value)==default_types.SET:
                gettyp = value.type
            else:
                gettyp=default_types.TYPES_[type(value)]
                
            self.raise_error("TypeError",f"Can't affect {''.join(expr)} to <{name}>, it has the type {gettyp} while it's expected to be a {reqtyp} object")
            return

        self.echo_affect(name,value)
        self.VARIABLES[name][1]=value
    
    def suppr_var(self,var):
        if var not in self.VARIABLES:
            self.raise_error("UnknownVariable",f"Unable to destroy variable {var}, it does not exist.")
            return
        
        del self.VARIABLES[var]
        self.echo_del(var)

    def create_alias(self,name,ref):
        if name in self.VARIABLES or name in self.ALIAS:
            raise error.AlreadyExistsError(name)
        if ref not in self.VARIABLES and ref not in self.ALIAS:
            raise error.UnknownObject(ref)
        
        if ref in self.ALIAS:
            self.ALIAS[name] = self.ALIAS[ref]
        else:
            self.ALIAS[name]=ref

    def execute(self,txt:str,flag=True):#,echoflag=True):
        self.text=txt
        self.parsed = _parser_.parse(txt)

        defstdout = sys.stdout
        defstdin = sys.stdin

        sys.stdout = StdRedirector(self.echo)
        sys.stdin = StdRedirector(self.echo)

        #Ctrl+C : break self.echo.bind("")

        self.STOP =False
        self.l=1
        if flag:self.echo_inf("==COMMENCEMENT D'EXECUTION==")
        self.echo.bind_all('<Control-c>',self.raise_end)
        for ph in self.parsed:
            try:
                h =self.exec(ph)
            except Exception as err:
                self.STOP=True
                if 'name' in dir(err):
                    if err==error.Halt and self.BOUCLE:
                        self.BOUCLE=False
                        return
                    self.raise_error(err.name(),str(err))
                else:
                    raise err
            if h == error.Halt:
                if self.BOUCLE:
                    self.BOUCLE=False
                    return
                else:
                    err=error.Halt()
                    self.raise_error(err.name(),str(err))
            if self.STOP:break
            self.l+=1
            self.echo.update()
        #self.ECHO=True
        
        sys.stdout=defstdout
        sys.stdin=defstdin

        if flag:
            print('Variables :\n',self.VARIABLES,'\nDictionnaire :\n',self.DICTIONARY,'\nBOUCLE :',self.BOUCLE)
            self.echo_inf("==FIN D'EXECUTION==")
        
        self.echo.unbind_all('<Control-c>')
        return self.STOP

    def raise_end(self,evt):
        #raise error.EndError()
        #raise error.Halt
        self.STOP=True
        self.raise_error("Keyboard Interupt",'')

    def exec(self,ph):
        if ph[0] == '∃':
            if not (( ph[2] == '∊' or ph[2]=='⊆' )and len(ph)==4):
                raise error.WrongSyntax()
            #assert( ph[2] == '∊' or ph[2]=='⊆' )and len(ph)==4
            self.create_variable(ph[1],ph[3],ph[2])
        elif len(ph)>=2 and  ph[1] == '≜':
            if len(ph) != 3:raise error.WrongSyntax()
            self.create_alias(ph[0],ph[2])
        elif ph[0] == '∄':
            if  len(ph)!=2 :raise error.WrongSyntax()
            self.suppr_var(ph[1])

        elif len(ph) >=2 and ph[1]=='≔':
            if '$' in ph[0]:
                self.dict_affect(ph)
            else:
                self.affect(ph[0],ph[2:])
        elif '@' == ph[0][0]:
            if len(ph) != 1 : raise error.WrongSyntax()
            order = ph[0][1:]
            if order == 'hide':
                self.ECHO=False
            elif order == 'show':
                self.ECHO = True
            elif order == 'HALT':
                return error.Halt
            elif len(order.split(' ')) ==2 and order.split(' ')[0]=='use':
                m = ModuleExecutor(order.split(' ')[1],self.echo)
                r = m.exec()
                for k,v in r[0].items():
                    if k in self.VARIABLES:
                        raise error.OverWritingWarning(k)
                    elif k in self.ALIAS:
                        del self.ALIAS[k]
                        raise error.OverWritingWarning(k)
                    elif k in self.DICTIONARY:
                        del self.DICTIONARY[k]
                        raise error.OverWritingWarning(k)
                    self.VARIABLES[k]=v

                for k,v in r[1].items():
                    if k in self.VARIABLES:
                        del self.VARIABLES[k]
                        raise error.OverWritingWarning(k)
                    elif k in self.ALIAS:
                        del self.ALIAS[k]
                        raise error.OverWritingWarning(k)
                    elif k in self.DICTIONARY:
                        #del self.DICTIONARY[k]
                        raise error.OverWritingWarning(k)
                    self.DICTIONARY[k]=v

                for k,v in r[2].items():
                    if k in self.VARIABLES:
                        del self.VARIABLES[k]
                        raise error.OverWritingWarning(k)
                    elif k in self.ALIAS:
                        #del self.ALIAS[k]
                        raise error.OverWritingWarning(k)
                    elif k in self.DICTIONARY:
                        del self.DICTIONARY[k]
                        raise error.OverWritingWarning(k)
                    self.ALIAS[k]=v
            else:
                raise error.UnknownObject(ph[0])
        elif '□' == ph[0]:
            if ph[1:] not in self.ASSERTS:self.ASSERTS.append(ph[1:])
        elif '¬' == ph[0] and ph[1]=='□':
            if ph[2:] in self.ASSERTS:self.ASSERTS.remove(ph[2:])
        elif ph[0]=='∀':
            self.for_all_ex(ph)
        elif '⇴' in ph:
            self.dict_ex(ph)
        elif '➣' == ph[0]:
            self.if_ex(ph)
        else:
            self.eval_expr(ph)
        
        for tests in self.ASSERTS:
            res = self.eval_expr(tests)
            print(res)
            if type(res) != default_types.B and type(res) != type(None):
                raise TypeError
            if type(res)==default_types.B and res.equiv(default_types.B(True)).v ==False:
                #self.raise_error("AssertionError",f"The assertion '{''.join(tests)}' has failled. ")
                raise error.WrongAssertion(tests)

    def raise_error(self,err,mes):
        self.STOP =True
        self.echo.config(state='normal')
        self.echo.insert('end',err + ' has occured at line n°'+str(self.l)+'\n'+mes+'\n','err')
        self.echo.config(state='disabled')

    def echo_dec(self,name,typ,way):
        if not self.ECHO:return
        self.echo.config(state='normal')
        self.echo.insert('end',f"Variable {name} created with type {typ if way =='∊' else chr(8472)+'('+str(typ)+')' }\n",'dec')
        self.echo.config(state='disabled')

    def echo_del(self,name):
        if not self.ECHO:return
        self.echo.config(state='normal')
        self.echo.insert('end',f"Variable {name} has been destroyed successfully\n",'dec')
        self.echo.config(state='disabled')
    
    def echo_affect(self,name,value):
        if not self.ECHO:return
        self.echo.config(state='normal')
        self.echo.insert('end',f"Variable {name} has recieved the value : {value }\n",'dec')
        self.echo.config(state='disabled')

    def echo_inf(self,inf):
        #if not self.ECHO:return
        self.echo.config(state='normal')
        self.echo.insert('end',inf+'\n','inf')
        self.echo.config(state='disabled')

    def eval_expr(self,l:list[str]):
        
        l_=[]
        for i,elt in enumerate(l):
            res=default_types.attribute_type(elt)
            if type(res) != type(None):
                l_.append(res)
            else:
                l_.append(elt)


        if len(l_) == 1 and type(l_[0]) != str:
            return l_[0]
        
        if len(l)==1 and l[0][0]=='{' and l[0][-1]=='}':
            try:   
                res=evaluate_sets(l[0],self.VARIABLES,self.DICTIONARY,self.ALIAS)#,self.FUNCTIONS)
                return res
            except Exception as err:
                print(err)
                return 'err'
        else:
            l_=create_evaluating_list(l)
            typize(l_)
            try:
                res=evaluate(l_,self.VARIABLES,self.DICTIONARY,self.ALIAS)#,stdout=StdRedirector(self.echo))
                return res
            except ZeroDivisionError:
                return '0err'
            #except Exception as err:
            #    print(err)
    
    def for_all_ex(self,code):
        assert len(code)==6 and code[2]=='∊' and code[4]==':'
        #print(stringify(self.VARIABLES[code[3]][0]),default_types.S)
        if not default_types.ZIntervalle.recognize(code[3]) and code[3] != 'ℕ' and not (code[3] in self.VARIABLES and (type(self.VARIABLES[code[3]][0]) in (default_types.Parts,) or self.VARIABLES[code[3]][0]==default_types.S)):raise
        
        if code[3] == 'ℕ':
            Ens=default_types.Niterator()
        elif code[3] in self.VARIABLES:
            Ens=self.VARIABLES[code[3]][1]
        else:
            Ens = default_types.ZIntervalle.from_str(code[3])
        
        if code[1] in self.VARIABLES:raise

        if code[3] == 'ℕ':
            self.VARIABLES[code[1]] = [default_types.N,None]
        elif type(Ens)== default_types.ZIntervalle:
            if (Ens.binf >=default_types.N(0)).v :
                self.VARIABLES[code[1]] = [default_types.N,None]
            else:
                self.VARIABLES[code[1]] = [default_types.Z,None]
        elif type(Ens) == default_types.S:
            self.VARIABLES[code[1]] = [default_types.S,None]
        else:
            #Ens:SET
            self.VARIABLES[code[1]] = [Ens.type,None]
        
        assert len(code[5])>2 and code[5][0]=='\\' and code[5][-1]=='/'
        run_code= code[5][1:-1]
        #run_code = _parser_.parse(run_code)
        self.BOUCLE=True
        for i in Ens:
            assert self.BOUCLE
            self.VARIABLES[code[1]][1]=i

            try:
                res = self.execute(run_code,flag=False)#,echoflag=self.ECHO)
            except error.Halt:
                res=True
            if res == None or not self.BOUCLE:return 
            if res :
                self.STOP=True
                self.BOUCLE=False
                return
        
    
    def if_ex(self,code):
        expr=[]
        assert code[0]=='➣'
        i=1
        ex=False
        while i <len(code):
            elt = code[i]

            if ex:
                ex=False
                res =self.eval_expr(expr)
                if type(res) != default_types.B:raise
                if res.v :
                    #execute
                    assert elt[0]=='\\' and elt[-1]=='/'
                    run_code = elt[1:-1]
                    res = self.execute(run_code,flag=False)#,echoflag=self.ECHO)
                    if res == error.Halt:
                        #return error.Halt
                        raise error.Halt
                    if res :
                        self.STOP=True
                    return
            elif elt == '⇝':
                ex=True
            elif elt == '➣':
                expr=[]
            else:
                expr.append(elt)

            i+=1

    def dict_ex(self,code):
        """Créer un dictionaire"""
        name = code[0]
        assert code[1]==':'
        t1 = code[2]
        assert code[3]=='⇴'
        t2 =code[4]
        assert code[5:]==[]
        assert name not in self.VARIABLES and name not in self.DICTIONARY and name not in self.FUNCTIONS
        assert default_types.recognize_type(t1)and default_types.recognize_type(t2)
        t1,t2 = default_types.type_from_str(t1),default_types.type_from_str(t2)
        self.DICTIONARY[name]=[(t1,t2),{}]

    def dict_affect(self,code):
        assert code[1] == '≔'
        obj = code[0]
        assert obj.count('$')==1
        obj = obj.split('$')
        if obj[0] not in self.DICTIONARY:
            self.raise_error("NameError",f"Unable to affect value to {obj[0]}, it does not exist.")
            return 
        
        k = default_types.attribute_type(obj[1])
        k =convert(k,self.DICTIONARY[obj[0]][0][0])
        v = self.eval_expr(code[2:])
        v = convert(v,self.DICTIONARY[obj[0]][0][1])

        self.DICTIONARY[obj[0]][1][k]=v
    
    def create_function(self,code):
        assert len(code)== 5
        assert code[0] not in self.VARIABLES and code[0] not in self.FUNCTIONS
        assert code[1]==':' and code[3]== '⟶'
        assert default_types.recognize_type(code[2]) and default_types.recognize_type(code[4])

        self.FUNCTIONS[code[0]] = default_types.Function(self,code[2],code[4])


class ModuleExecutor:
    def __init__(self,path,echo) -> None:
        self.path=path+'.e'
        self.echo=echo
    
    def exec(self):
        with open(self.path,'rb') as f:
            ex=Executor(self.echo)
            ex.execute(f.read().decode('utf-8'),False)
        return (ex.VARIABLES,ex.DICTIONARY,ex.ALIAS)


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

def valid_name(ch:str):
    if ch =='' or ' ' in ch:
        return False
    if ch[0].isnumeric():return False
    return all(car in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch)

def typize(l:list):
    for i,elt in enumerate(l):
        if type(elt)==list:
            typize(elt)
        else:
            r=default_types.attribute_type(elt)
            if type(r) != type(None):
                l[i]=r

def evaluate(l:list,variables,dictionary,alias,k=0):#,stdout=sys.__stdout__):
    simpl(l)
    assert type(k)==int
    for i,elt in enumerate(l):
        #print(elt)
        if type(elt)==list:
            evaluate(elt,variables,dictionary,alias,k+1)
            if len(l[i])==1:l[i]=l[i][0]
        elif type(elt)==str and elt in variables:
            l[i] = variables[elt][1]
        elif type(elt)==str and elt in alias:
            l[i] = variables[alias[elt]][1]
        elif type(elt)==str and elt[0]=='{' and elt[-1]=='}':
            l[i]=evaluate_sets(elt,variables,dictionary)
        elif type(elt) == str and elt not in "∃∊+-×÷∧∨⊕¬⇔⇒⊆|^⟦⟧≔⩾=⩽≠<>;":
            l[i] = exec_func_dict(elt,variables,dictionary)#,stdout=stdout)
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

def evaluate_sets(ch,variables,dictionary,alias):
    s=set()
    for elt in default_types.SET.listify(ch):
        l_elt = _parser_.parse_a_sentence(elt)
        eval_l = create_evaluating_list(l_elt)
        typize(eval_l)
        res = evaluate(eval_l,variables,dictionary,alias)
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

def exec_func_dict(ch:str,variables,dictionary):#,stdout):

    ch_ =""
    f=True

    for car in ch:
        if car != '$':
            ch_ += car
        elif f:
            ch_ += '('
            f=False
        else:
            ch_ +=','
    if '('in ch_:
        ch_ += ')'
    else:
        ch_ += '()'

    p1 =True
    f,a='',''
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
    
    l_=[]
    #print(a)
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
    return eval(f+a)

#ajouter des opérateurs
#refaire des verifs puis faire les fonctions.
#enregistrer et ouvrir
#structures conditionnelles.
if __name__=='__main__':print(transform('(1;{"1";"2"})'))
import tkinter.scrolledtext as scrolledtext
import _parser_, default_types, evaluations,Functions
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
            self.raise_error('InvalidNameError', f"Invalid name for a variable {name}")
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
            try:
                if h == error.Halt:
                    if self.BOUCLE:
                        self.BOUCLE=False
                        return
                    else:
                        err=error.Halt()
                        self.raise_error(err.name(),str(err))
            except:pass
            if self.STOP:break
            self.l+=1
            self.echo.update()
        #self.ECHO=True
        
        sys.stdout=defstdout
        sys.stdin=defstdin

        if flag:
            print('Variables :\n',self.VARIABLES,'\nDictionnaire :\n',self.DICTIONARY,'\Fonctions :\n',self.FUNCTIONS,'\nAlias :\n',self.ALIAS,'\nBOUCLE :',self.BOUCLE)
            self.echo_inf("==FIN D'EXECUTION==")
        
        self.echo.unbind_all('<Control-c>')
        return self.STOP

    def raise_end(self,evt):
        #raise error.EndError()
        #raise error.Halt
        self.STOP=True
        self.raise_error("Keyboard Interupt",'')

    def exec(self,ph):
        #match ph:
        #    case ['∃',name, ('∊' | '⊆') as way,typ]:
        #        self.create_variable(name,typ,way)
        
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
        elif len(ph) == 5 and ph[1]==':' and ph[3]=='⟶':
            assert default_types.recognize_type(ph[2])
            assert default_types.recognize_type(ph[4])
            assert ph[0] not in self.VARIABLES
            assert ph[0] not in self.DICTIONARY
            assert ph[0] not in self.ALIAS
            assert ph[0] not in self.FUNCTIONS
            self.FUNCTIONS[ph[0]]=Functions.Applications(ph[0],ph[2],ph[4])
        elif len(ph) >= 5 and ph[1]==':' and ph[3] == '⟼':
            if ph[0] not in self.FUNCTIONS:raise
            f:Functions.Applications = self.FUNCTIONS[ph[0]]
            f.set_args_name(*ph[2].split(';'))
            f.set_expr(ph[4:])
        else:
            self.eval_expr(ph)
        
        for tests in self.ASSERTS:
            res = self.eval_expr(tests)
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
                res=evaluations.evaluate_sets(l[0],self.VARIABLES,self.DICTIONARY,self.ALIAS,self.FUNCTIONS)#,self.FUNCTIONS)
                return res
            except Exception as err:
                print(err)
                return 'err'
        else:
            l_=evaluations.create_evaluating_list(l)
            evaluations.typize(l_)
            try:
                res=evaluations.evaluate(l_,self.VARIABLES,self.DICTIONARY,self.FUNCTIONS,self.ALIAS)#,stdout=StdRedirector(self.echo))
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




def valid_name(ch:str):
    if ch =='' or ' ' in ch:
        return False
    if ch[0].isnumeric():return False
    return all(car in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch)



#refaire des verifs puis faire les fonctions.
from tkinter.scrolledtext import ScrolledText #as scrolledtext.Scrolledtext
import _parser_, default_types, evaluations,Applications,error,time,Functions, Dictionnary,Variable
from default_functions import convert
import sys,copy,os,json,load,compilator,file
from tkinter import END

class StdRedirector:
    def __init__(self, text_widget:ScrolledText):
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
    def __init__(self,echo:ScrolledText):
        if not os.path.exists("dcache"):
            os.mkdir("dcache")
        self.VARIABLES = {}
        self.ALIAS = {}
        self.FUNCTIONS = {}
        self.DICTIONARY = {}
        self.ASSERTS = []
        self.BOUCLE=False
        self.echo=echo
        self.ECHO=True
        self.saveable = True
    
    def create_variable(self,name,typ,way='∊'):
        if name in self.VARIABLES or name in self.FUNCTIONS or name in  self.ALIAS or name in self.DICTIONARY:
            raise error.AlreadyExistsError(name)
        
        if not(default_types.recognize_type(typ)):
            raise error.TypeError(typ)

        if way =='∊':
            self.VARIABLES[name]=Variable.Variable(default_types.type_from_str(typ),name)#[default_types.type_from_str(typ),None]
        else:
            self.VARIABLES[name]=Variable.Variable(default_types.Parts(default_types.type_from_str(typ)),name)
        self.echo_dec(name,typ,way)

    def affect(self,name,expr:list[str]):
        if name not in self.VARIABLES and name not in self.ALIAS:
            raise error.NameError(name)
        
        if name in self.ALIAS:
            name=self.ALIAS[name]

        value = self.eval_expr(expr.copy())
        if type(value)==str :
            if value == 'err':
                raise error.EvaluationError(expr)
            elif value == '0err':
                raise error.DividingByZero()
        try:
            value = convert(value,self.VARIABLES[name].type)
        except Exception as err:
            if type(self.VARIABLES[name].type)==default_types.CrossSet or type(self.VARIABLES[name].type) == default_types.Parts:
                reqtyp=self.VARIABLES[name].type
            else:
                reqtyp = default_types.TYPES_[self.VARIABLES[name].type]

            if type(value) == default_types.Tuple:
                gettyp = value.type
            elif type(value)==default_types.SET:
                gettyp = value.type
            else:
                gettyp=default_types.TYPES_[type(value)]
            
            raise error.TypeError_(expr,name,gettyp,reqtyp)

        self.echo_affect(name,value)
        self.VARIABLES[name].set(value)
    
    def suppr_var(self,var,flag=True):
        if var not in self.VARIABLES:
            raise error.UnknownObject(var)
        
        del self.VARIABLES[var]
        if flag :self.echo_del(var)

    def create_alias(self,name,ref):
        if name in self.VARIABLES or name in self.ALIAS:
            raise error.AlreadyExistsError(name)
        if ref not in self.VARIABLES and ref not in self.ALIAS:
            raise error.UnknownObject(ref)
        
        if ref in self.ALIAS:
            self.ALIAS[name] = self.ALIAS[ref]
        else:
            self.ALIAS[name]=ref

    def execute(self,txt:str,flag=True,name=''):#,echoflag=True):,
        self.text=txt
        self.parsed = _parser_.parse(txt)

        if self.echo != None:
            defstdout = sys.stdout
            defstdin = sys.stdin

            sys.stdout = StdRedirector(self.echo)
            sys.stdin = StdRedirector(self.echo)

        #Ctrl+C : break self.echo.bind("")

        self.STOP =False
        self.l=1
        if flag:self.echo_inf("==COMMENCEMENT D'EXECUTION==")
        t=time.time()
        self.echo.bind_all('<Control-c>',self.raise_end)
        for i,ph in enumerate(self.parsed):
            try:
                h =self.exec(ph)
            except Exception as err:
                print('err',err,str(err)=="This sentence is syntaxly incorrect.")
                self.STOP=True
                if 'name' in dir(err):
                    if err==error.Halt and self.BOUCLE:
                        self.BOUCLE=False
                        self.STOP=False
                        return
                    if err == error.WrongSyntax and str(err)=="This sentence is syntaxly incorrect.":
                        err=error.WrongSyntax(ph)
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
                        raise err
                if h == error.EOI:
                    return error.EOI

            except NameError:
                h=None
            if h != None:
                return h
            if self.STOP:break
            self.l+=1
            self.echo.update()
        #self.ECHO=True
        
        if self.echo != None:
            sys.stdout=defstdout
            sys.stdin=defstdin

        if flag:
            if not self.STOP and name.replace(' ','') != '' and self.saveable:
                data = {
                    'Variables' : {k:v.__repr__() for k,v in self.VARIABLES.items()},
                    'Dictionnaires' : {k:v.representation() for k,v in self.DICTIONARY.items()},
                    'Fonctions' : {k:v.__repr__() for k,v in self.FUNCTIONS.items()},
                    'Alias' : {k:v for k,v in self.ALIAS.items()}
                }
                with open(name+'.json','w') as f:
                    json.dump(data,f)
                file.save_json(name,name+'.json')
            print('Variables :\n',self.VARIABLES,'\nDictionnaire :\n',self.DICTIONARY,'\nFonctions :\n',self.FUNCTIONS,'\nAlias :\n',self.ALIAS,'\nBOUCLE :',self.BOUCLE)
            self.echo_inf("==FIN D'EXECUTION=="+str(time.time()-t))
        
        self.echo.unbind_all('<Control-c>')
        return self.STOP

    def raise_end(self,evt):
        #raise error.EndError()
        #raise error.Halt
        self.STOP=True
        self.raise_error("Keyboard Interupt",'')

    def exec(self,ph):
        match ph:
            case ['∃',name, ('∊' | '⊆') as way,typ]:
               self.create_variable(name,typ,way)
            case [v1, '≜', v2]:
               self.create_alias(v1,v2)
            case ['∄',var]:
               self.suppr_var(var)
            case [thing,'≔',*r]:
                if '$' in thing:
                   self.dict_affect(ph)
                else:
                   self.affect(thing,r)
            case [thing] if thing != '' and thing[0]=='@':
                match thing[1:].split(' '):
                    case ['HIDE']: self.ECHO = False
                    case ['SHOW']: self.ECHO=True
                    case ['HALT']: return error.Halt
                    case ['CONTINUE']: return error.EOI
                    case ['WAIT']: time.sleep(3e-3)
                    case ['BELL']: self.echo.bell()
                    case [('USE*'|'USE') as w,name]:
                        if '*' in w:
                            if not os.path.exists(name+'.df'):raise error.ModuleError(name)
                            r = load.load(name)
                        else:
                            m = ModuleExecutor(name,self.echo)
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
                            elif k in self.FUNCTIONS:
                                del self.FUNCTIONS[k]
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
                            elif k in self.FUNCTIONS:
                                del self.FUNCTIONS[k]
                                raise error.OverWritingWarning(k)
                            self.DICTIONARY[k]=v

                        for k,v in r[2].items():
                            if k in self.VARIABLES:
                                del self.VARIABLES[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.ALIAS:
                                del self.ALIAS[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.DICTIONARY:
                                del self.DICTIONARY[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.FUNCTIONS:
                                raise error.OverWritingWarning(k)
                            self.FUNCTIONS[k]=v

                        for k,v in r[3].items():
                            if k in self.VARIABLES:
                                del self.VARIABLES[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.ALIAS:
                                #del self.ALIAS[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.DICTIONARY:
                                del self.DICTIONARY[k]
                                raise error.OverWritingWarning(k)
                            elif k in self.FUNCTIONS:
                                del self.FUNCTIONS[k]
                                raise error.OverWritingWarning(k)
                            self.ALIAS[k]=v
                    case ['USE', expr,'FROM',path]:
                        searched = expr.split(',')
                        for elt in searched:
                            r= load.load_some(path,elt)
                            if r[0] =='VAR':
                                self.VARIABLES[r[1].name]=r[1]
                            elif r[0] == 'DICT':
                                self.DICTIONARY[r[1].name]=r[1]
                            else:
                                self.FUNCTIONS[r[1].name]=r[1]
                    
                    case _:raise error.UnknownObject(ph[0])
            case ['□',*expr]:
                if expr not in self.ASSERTS:self.ASSERTS.append(expr)
            case ['¬','□',*expr]:
                if expr in self.ASSERTS:
                    self.ASSERTS.remove(expr)
            case ['∀',*code]:self.for_all_ex(ph)
            case [nom,':',typ1,'⇴',typ2]:
                self.dict_ex(nom,typ1,typ2)#refaire
            case ['➣',*code]:
                r=self.if_ex(ph)
                if r == error.EOI:return r
            case [nom,':',t1,'⟶',t2]:
                if not default_types.recognize_type(t1):
                    raise error.TypeError(t1)
                if not default_types.recognize_type(t2):
                    raise error.TypeError(t2)
                if nom in self.VARIABLES or nom in self.DICTIONARY or nom in self.ALIAS or nom in self.FUNCTIONS:
                    raise error.AlreadyExistsError(name)
                self.FUNCTIONS[nom]=Applications.Applications(nom,t1,t2)
            case [nom,':',vars,'⟼',*return_]:
                if nom not in self.FUNCTIONS:raise
                f:Applications.Applications = self.FUNCTIONS[nom]
                f.set_args_name(*vars.split(';'))
                f.set_expr(return_)
            case [thing] if len(thing) >2 and thing[0]==thing[-1]=='#':
                self.create_function(thing)
            case _:
                if any([elt in _parser_.kw for elt in ph]):
                    raise error.WrongSyntax()
                self.eval_expr(ph)
        for tests in self.ASSERTS:
            res = self.eval_expr(tests)
            if type(res) != default_types.B and type(res) != type(None):
                raise error.WrongAssertion(res)
            if type(res)==default_types.B and res.equiv(default_types.B(True)).v ==False:
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
        if any('ask' in obj for obj in l):
            self.saveable=False
        ph_=[]
        for i,elt in enumerate(l):
            if i==0:
                ph_.append(elt)
            elif elt[0]=='$':
                ph_[-1]+=elt
            elif elt[0] in _parser_.t or elt[0] in _parser_.indic and ph_[-1][-1]=='$':
                ph_[-1]+=elt
            else:
                ph_.append(elt)
        l=ph_
        l_=[]
        for i,elt in enumerate(l):
            res=default_types.full_typize(elt)
            if type(res) != type(None):
                l_.append(res)
            else:
                l_.append(elt)


        if len(l_) == 1 and type(l_[0]) != str:
            return l_[0]

        if len(l)==1 and l[0][0]=='{' and l[0][-1]=='}':
            try:   
                res=evaluations.evaluate_sets(l[0],self.VARIABLES,self.DICTIONARY,self.ALIAS,self.FUNCTIONS,self)#,self.FUNCTIONS)
                return res
            except Exception as err:
                return 'err'
        else:
            l_=evaluations.create_evaluating_list(l)
            evaluations.typize(l_)
            try:
                res=evaluations.evaluate(l_,self.VARIABLES,self.DICTIONARY,self.FUNCTIONS,self.ALIAS,self)#,stdout=StdRedirector(self.echo))
                return res
            except ZeroDivisionError:
                return '0err'
    
    def for_all_ex(self,code):
        if not (len(code)==6 and code[2]=='∊' and code[4]==':'):raise error.WrongSyntax()
        #Refaire !
        Ens=code[3]
        if Ens == 'ℕ':
            self.saveable=False
            Ens=default_types.Niterator()
        elif Ens in self.VARIABLES:
            if self.VARIABLES[Ens].type == default_types.S or type(self.VARIABLES[Ens].type) == default_types.Parts:
                Ens = self.VARIABLES[Ens].get()
            else:
                raise error.IterationError(default_types.stringify(self.VARIABLES[Ens].type))
        elif len(Ens)>=5 and Ens[0]=='⟦' and Ens[-1]== '⟧':
            Ens = Ens[1:-1].split(';')
            if len(Ens) != 2:
                raise error.WrongSyntax(*code) 
            b1,b2 = self.eval_expr([Ens[0]]),self.eval_expr([Ens[1]])
            b1,b2 = convert(b1,default_types.Z),convert(b2,default_types.Z)
            Ens = default_types.ZIntervalle(b1,b2)
        else:
            raise error.WrongSyntax(*code) 
        
        if code[1] in self.VARIABLES:raise

        if code[3] == 'ℕ':
            self.VARIABLES[code[1]] = Variable.Variable(default_types.N,code[1])
        elif type(Ens)== default_types.ZIntervalle:
            if (Ens.binf >=default_types.N(0)).v :
                self.VARIABLES[code[1]] = Variable.Variable(default_types.N,code[1])
            else:
                self.VARIABLES[code[1]] = Variable.Variable(default_types.Z,code[1])
        elif type(Ens) == default_types.S:
            self.VARIABLES[code[1]] = Variable.Variable(default_types.S,code[1])
        else:
            Ens:default_types.SET
            self.VARIABLES[code[1]] = Variable.Variable(Ens.type,code[1])
        
        if  not(len(code[5])>2 and code[5][0]=='\\' and code[5][-1]=='/'):raise error.WrongSyntax()
        run_code= code[5][1:-1]
        #run_code = _parser_.parse(run_code)
        self.BOUCLE=True
        for i in Ens:
            assert self.BOUCLE
            self.VARIABLES[code[1]].set(i)

            try:
                res = self.execute(run_code,flag=False)
            except error.Halt:
                res=True
            except error.EOI:continue
            if res ==error.EOI:
                continue
            if res == None or not self.BOUCLE:
                break
            if res :
                self.STOP=True
                self.BOUCLE=False
                break
        self.suppr_var(code[1],False)
            
    def if_ex(self,code):
        expr=[]
        if code[0]!='➣':raise error.WrongSyntax()
        i=1
        ex=False
        while i <len(code):
            elt = code[i]

            if ex:
                ex=False
                res =self.eval_expr(expr)
                if type(res) != default_types.B:raise
                if res.v :
                    if not (elt[0]=='\\' and elt[-1]=='/'):raise error.WrongSyntax()
                    run_code = elt[1:-1]
                    res = self.execute(run_code,flag=False)
                    if res == error.Halt:
                        raise error.Halt
                    if res == error.EOI:
                        return error.EOI
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

    def dict_ex(self,nom,t1,t2):
        """Créer un dictionaire"""

        if nom in self.VARIABLES or nom in self.DICTIONARY or nom in self.FUNCTIONS :
            raise error.AlreadyExistsError(nom)
        if not (default_types.recognize_type(t1)):raise error.TypeError(t1)
        if not (default_types.recognize_type(t2)):raise error.TypeError(t2)
        t1,t2 = default_types.type_from_str(t1),default_types.type_from_str(t2)
        self.DICTIONARY[nom]=Dictionnary.Dictionnary(t1,t2,nom)

    def dict_affect(self,code):
        if code[1] != '≔': raise error.WrongSyntax()
        obj = code[0]
        if obj.count('$')!=1 : raise error.WrongSyntax()
        obj = obj.split('$')
        if obj[0] not in self.DICTIONARY:
            raise error.NameError(obj[0])
        
        k = self.eval_expr([obj[1]])
        v = self.eval_expr(code[2:])
        

        self.DICTIONARY[obj[0]][k]=v
    
    def create_function(self,code):
        code=code[1:-1]
        code=_parser_.parse(code)
        if  len(code)<=2:raise error.WrongSyntax()
        if  len(code[0])!=5: raise error.WrongSyntax()
        if code[0][0] in self.VARIABLES or code[0][0] in self.FUNCTIONS or code[0][0]  in self.ALIAS or code[0][0] in self.DICTIONARY: raise error.AlreadyExistsError(code[0][0])
        if code[0][1]!=':' or code[0][3] != '⟶':raise error.WrongSyntax()
        if not default_types.recognize_type(code[0][2]) : raise error.TypeError(code[0][2])
        if not default_types.recognize_type(code[0][4]) : raise error.TypeError(code[0][4])

        self.FUNCTIONS[code[0][0]] = Functions.Function(code[0][0],code[0][2],code[0][4])
        if not (len(code[1]) == 1 and code[1][0][0] == '⟨' and code[1][0][-1] == '⟩'):
            raise error.WrongSyntax()
        args = code[1][0][1:-1].split(';')
        self.FUNCTIONS[code[0][0]].set_args_name(*args)
        i=2
        if code[i] == ['@GLOBAL']:
            self.FUNCTIONS[code[0][0]].set_global()
            i+=1
        if code[i] == ['@RESTRICT'] :
            self.FUNCTIONS[code[0][0]].set_restricted()
            i+=1
        if code[i][0][0]==code[i][0][-1]=='"':
            self.FUNCTIONS[code[0][0]].set_doc(code[i][0][1:-1])
            i+=1
        if code[i:]==[]: raise error.WrongSyntax()
        self.FUNCTIONS[code[0][0]].set_code(code[i:])

    def func_call(self,f,*args):
        if f not in self.FUNCTIONS: raise error.TypeError(f,typ=2)##
        #faire des copies
        cvar,cfct,calias,cdict = {},{},{},{}
        for k,v in self.VARIABLES.items():
            cvar[copy.copy(k)]=copy.copy(v)
        for k,v in self.FUNCTIONS.items():
            cfct[copy.copy(k)]=copy.copy(v)
        for k,v in self.ALIAS.items():
            calias[copy.copy(k)]=copy.copy(v)
        for k,v in self.DICTIONARY.items():
            cdict[copy.copy(k)]=copy.copy(v) 

        self.FUNCTIONS[f].set_global_obj(cvar,cfct,calias,cdict)
        r=self.FUNCTIONS[f](self.echo,*[self.VARIABLES[elt].get() for elt in args])
        if self.FUNCTIONS[f].gl_bal:
            for k,v in self.FUNCTIONS[f].VAR.items():
                if k in self.FUNCTIONS[f].arg_names:continue
                if k[:7]=='GLOBAL·':
                    self.VARIABLES[k[7:]].set(v.get())
                else:
                    self.VARIABLES[k].set(v.get())
            self.FUNCTIONS=self.FUNCTIONS[f].FUNC
            self.ALIAS=self.FUNCTIONS[f].ALIAS
            self.DICTIONARY=self.FUNCTIONS[f].DICT
        return r

class ModuleExecutor:
    def __init__(self,path,echo) -> None:

        if not os.path.exists(path+'.df'):raise

        self.text = file.get_text(path,path)
        self.text=compilator.compile(self.text)

        self.echo=echo
    
    def exec(self):
        ex=Executor(self.echo)
        ex.execute(self.text,False)
        return (ex.VARIABLES,ex.DICTIONARY,ex.FUNCTIONS,ex.ALIAS)


class FuncExecutor:
    def __init__(self,code,echo,var,func,dic,alias):
        self.VARIABLES = var
        self.ALIAS = alias
        self.FUNCTIONS = func
        self.DICTIONARY = dic
        self.ASSERTS = []
        self.BOUCLE=False
        self.echo=echo
        self.ECHO=True
        self.code=code
        self.returned, self.return_obj=False,default_types.EmptySet()
    
    def create_variable(self,name,typ,way='∊'):
        if name in self.VARIABLES or name in self.FUNCTIONS or name in  self.ALIAS or name in self.DICTIONARY:
            raise error.AlreadyExistsError(name)
        
        if not(default_types.recognize_type(typ)):
            raise error.TypeError(typ)

        if way =='∊':
            self.VARIABLES[name]=Variable.Variable(default_types.type_from_str(typ),name)#[default_types.type_from_str(typ),None]
        else:
            self.VARIABLES[name]=Variable.Variable(default_types.Parts(default_types.type_from_str(typ)),name)
        self.echo_dec(name,typ,way)

    def affect(self,name,expr:list[str]):
        if name not in self.VARIABLES and name not in self.ALIAS:
            raise error.NameError(name)
        
        if name in self.ALIAS:
            name=self.ALIAS[name]

        value = self.eval_expr(expr.copy())
        if type(value)==str :
            if value == 'err':
                raise error.EvaluationError(expr)
            elif value == '0err':
                raise error.DividingByZero()
        try:
            value = convert(value,self.VARIABLES[name].type)
        except Exception as err:
            if type(self.VARIABLES[name].type)==default_types.CrossSet or type(self.VARIABLES[name].type) == default_types.Parts:
                reqtyp=self.VARIABLES[name].type
            else:
                reqtyp = default_types.TYPES_[self.VARIABLES[name].type]

            if type(value) == default_types.Tuple:
                gettyp = value.type
            elif type(value)==default_types.SET:
                gettyp = value.type
            else:
                gettyp=default_types.TYPES_[type(value)]
            
            raise error.TypeError_(expr,name,gettyp,reqtyp)

        self.echo_affect(name,value)
        self.VARIABLES[name].set(value)
    
    def create_alias(self,name,ref):
        if name in self.VARIABLES or name in self.ALIAS:
            raise error.AlreadyExistsError(name)
        if ref not in self.VARIABLES and ref not in self.ALIAS:
            raise error.UnknownObject(ref)
        
        if ref in self.ALIAS:
            self.ALIAS[name] = self.ALIAS[ref]
        else:
            self.ALIAS[name]=ref

    def execute(self,code=''):#,echoflag=True):,

        if self.echo != None:
            defstdout = sys.stdout
            defstdin = sys.stdin

            sys.stdout = StdRedirector(self.echo)
            sys.stdin = StdRedirector(self.echo)

        #Ctrl+C : break self.echo.bind("")
        if code=='':code=self.code

        self.STOP =False
        self.l=1
        t=time.time()
        self.echo.bind_all('<Control-c>',self.raise_end)
        for i,ph in enumerate(code):
            try:
                h =self.exec(ph)
            except Exception as err:
                raise err
                
                self.STOP=True
                if 'name' in dir(err):
                    if err==error.Halt and self.BOUCLE:
                        self.BOUCLE=False
                        self.STOP=False
                        return
                    if err == error.WrongSyntax and str(err)=="This sentence is syntaxly incorrect.":
                        err=error.WrongSyntax(ph)
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
                        raise err
                if h == error.EOI:
                    return error.EOI

            except NameError:
                h=None
            if h != None:
                return h
            if self.STOP or self.returned:break
            self.l+=1
            self.echo.update()
        #self.ECHO=True
        if self.echo != None:
            sys.stdout=defstdout
            sys.stdin=defstdin

        self.echo.unbind_all('<Control-c>')
        return self.return_obj

    def raise_end(self,evt):
        #raise error.EndError()
        #raise error.Halt
        self.STOP=True
        self.raise_error("Keyboard Interupt",'')

    def exec(self,ph):
        match ph:
            case ['∃',name, ('∊' | '⊆') as way,typ]:
               self.create_variable(name,typ,way)
            case [v1, '≜', v2]:
               self.create_alias(v1,v2)
            case [thing,'≔',*r]:
                if '$' in thing:
                   self.dict_affect(ph)
                else:
                   self.affect(thing,r)
            case [thing] if thing != '' and thing[0]=='@':
                match thing[1:].split(' '):
                    case ['HIDE']: self.ECHO = False
                    case ['SHOW']: self.ECHO=True
                    case ['HALT']: return error.Halt
                    case ['CONTINUE']: return error.EOI
                    case ['WAIT']: time.sleep(3e-3)
                    case ['BELL']: self.echo.bell()
                    case _:raise error.UnknownObject(ph[0])
            case ['□',*expr]:
                if expr not in self.ASSERTS:self.ASSERTS.append(expr)
            case ['¬','□',*expr]:
                if expr in self.ASSERTS:
                    self.ASSERTS.remove(expr)
            case ['∀',*code]:self.for_all_ex(ph)
            case [nom,':',typ1,'⇴',typ2]:
                self.dict_ex(nom,typ1,typ2)#refaire
            case ['➣',*code]:
                r=self.if_ex(ph)
                if r == error.EOI:return r
            case ['⟼',*expr]:
                self.returned=True
                if expr != []:
                    r=self.eval_expr(expr)
                    self.return_obj=r
            case[]:pass
            case _:
                
                if any([elt in _parser_.kw for elt in ph]):
                    raise error.WrongSyntax()
                self.eval_expr(ph)
        
        for tests in self.ASSERTS:
            res = self.eval_expr(tests)
            if type(res) != default_types.B and type(res) != type(None):
                raise error.WrongAssertion(res)
            if type(res)==default_types.B and res.equiv(default_types.B(True)).v ==False:
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
            res=default_types.full_typize(elt)
            if type(res) != type(None):
                l_.append(res)
            else:
                l_.append(elt)


        if len(l_) == 1 and type(l_[0]) != str:
            return l_[0]

        if len(l)==1 and l[0][0]=='{' and l[0][-1]=='}':
            try:   
                res=evaluations.evaluate_sets(l[0],self.VARIABLES,self.DICTIONARY,self.ALIAS,self.FUNCTIONS,self)#,self.FUNCTIONS)
                return res
            except Exception as err:
                return 'err'
        else:
            l_=evaluations.create_evaluating_list(l)
            evaluations.typize(l_)
            try:
                res=evaluations.evaluate(l_,self.VARIABLES,self.DICTIONARY,self.FUNCTIONS,self.ALIAS,self)#,stdout=StdRedirector(self.echo))
                return res
            except ZeroDivisionError:
                return '0err'
    
    def for_all_ex(self,code):
        if not (len(code)==6 and code[2]=='∊' and code[4]==':'):raise error.WrongSyntax()
        #Refaire !
        Ens=code[3]
        if Ens == 'ℕ':
            Ens=default_types.Niterator()
        elif Ens in self.VARIABLES:
            if self.VARIABLES[Ens].type == default_types.S or type(self.VARIABLES[Ens].type) == default_types.Parts:
                Ens = self.VARIABLES[Ens].get()
            else:
                raise error.IterationError(default_types.stringify(self.VARIABLES[Ens].type))
        elif len(Ens)>=5 and Ens[0]=='⟦' and Ens[-1]== '⟧':
            Ens = Ens[1:-1].split(';')
            if len(Ens) != 2:
                raise error.WrongSyntax(*code) 
            b1,b2 = self.eval_expr([Ens[0]]),self.eval_expr([Ens[1]])
            b1,b2 = convert(b1,default_types.Z),convert(b2,default_types.Z)
            Ens = default_types.ZIntervalle(b1,b2)
        else:
            raise error.WrongSyntax(*code) 
        
        if code[1] in self.VARIABLES:raise

        if code[3] == 'ℕ':
            self.VARIABLES[code[1]] = Variable.Variable(default_types.N,code[1])
        elif type(Ens)== default_types.ZIntervalle:
            if (Ens.binf >=default_types.N(0)).v :
                self.VARIABLES[code[1]] = Variable.Variable(default_types.N,code[1])
            else:
                self.VARIABLES[code[1]] = Variable.Variable(default_types.Z,code[1])
        elif type(Ens) == default_types.S:
            self.VARIABLES[code[1]] = Variable.Variable(default_types.S,code[1])
        else:
            Ens:default_types.SET
            self.VARIABLES[code[1]] = Variable.Variable(Ens.type,code[1])
        
        if  not(len(code[5])>2 and code[5][0]=='\\' and code[5][-1]=='/'):raise error.WrongSyntax()
        run_code= code[5][1:-1]
        #run_code = _parser_.parse(run_code)
        self.BOUCLE=True
        for i in Ens:
            assert self.BOUCLE
            self.VARIABLES[code[1]].set(i)

            try:
                res = self.execute(run_code,flag=False)
            except error.Halt:
                res=True
            except error.EOI:continue
            if res ==error.EOI:
                continue
            if res == None or not self.BOUCLE:
                break
            if res :
                self.STOP=True
                self.BOUCLE=False
                break
        self.suppr_var(code[1],False)
            
    def if_ex(self,code):
        expr=[]
        if code[0]!='➣':raise error.WrongSyntax()
        i=1
        ex=False
        while i <len(code):
            elt = code[i]

            if ex:
                ex=False
                res =self.eval_expr(expr)
                if type(res) != default_types.B:raise
                if res.v :
                    if not (elt[0]=='\\' and elt[-1]=='/'):raise error.WrongSyntax()
                    run_code = elt[1:-1]
                    res = self.execute(run_code,flag=False)
                    if res == error.Halt:
                        raise error.Halt
                    if res == error.EOI:
                        return error.EOI
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

    def dict_ex(self,nom,t1,t2):
        """Créer un dictionaire"""

        if nom in self.VARIABLES or nom in self.DICTIONARY or nom in self.FUNCTIONS :
            raise error.AlreadyExistsError(nom)
        if not (default_types.recognize_type(t1)):raise error.TypeError(t1)
        if not (default_types.recognize_type(t2)):raise error.TypeError(t2)
        t1,t2 = default_types.type_from_str(t1),default_types.type_from_str(t2)
        self.DICTIONARY[nom]=Dictionnary.Dictionnary(t1,t2,nom)

    def dict_affect(self,code):
        if code[1] != '≔': raise error.WrongSyntax()
        obj = code[0]
        if obj.count('$')!=1 : raise error.WrongSyntax()
        obj = obj.split('$')
        if obj[0] not in self.DICTIONARY:
            raise error.NameError(obj[0])
        k = self.eval_expr([obj[1]])
        k =convert(k,self.DICTIONARY[obj[0]]._in)
        v = self.eval_expr(code[2:])
        v = convert(v,self.DICTIONARY[obj[0]].out)
        

        self.DICTIONARY[obj[0]][k]=v

    def func_call(self,f,*args):
        if f not in self.FUNCTIONS: raise error.TypeError(f,typ=2)##
        #faire des copies
        cvar,cfct,calias,cdict = {},{},{},{}
        for k,v in self.VARIABLES.items():
            cvar[copy.copy(k)]=copy.copy(v)
        for k,v in self.FUNCTIONS.items():
            cfct[copy.copy(k)]=copy.copy(v)
        for k,v in self.ALIAS.items():
            calias[copy.copy(k)]=copy.copy(v)
        for k,v in self.DICTIONARY.items():
            cdict[copy.copy(k)]=copy.copy(v) 

        self.FUNCTIONS[f].set_global_obj(cvar,cfct,calias,cdict)
        r=self.FUNCTIONS[f](self.echo,*[self.VARIABLES[elt].get() for elt in args])
        if self.FUNCTIONS[f].gl_bal:
            for k,v in self.FUNCTIONS[f].VAR.items():
                if k in self.FUNCTIONS[f].arg_names:continue
                if k[:7]=='GLOBAL·':
                    self.VARIABLES[k[7:]].set(v.get())
                else:
                    self.VARIABLES[k].set(v.get())
            self.FUNCTIONS=self.FUNCTIONS[f].FUNC
            self.ALIAS=self.FUNCTIONS[f].ALIAS
            self.DICTIONARY=self.FUNCTIONS[f].DICT
        return r

#refaire des verifs puis faire les fonctions.

if __name__ == '__main__':
    pass
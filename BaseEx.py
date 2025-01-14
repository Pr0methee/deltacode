import copy,error,default_types,evaluations,Variable,time,sys,_parser_,Dictionnary,tools,os,POO,Callable
from abc import abstractmethod

import exceptions
from default_functions import convert,DEFAULT_FUNCTIONS,stringify

class BaseEx:
    def __init__(self,vars,fcts,dicts,aliases,objs,echo):
        self.VARIABLES = vars
        self.FUNCTIONS = fcts
        self.ALIAS = aliases
        self.OBJECTS = objs
        self.DICTIONARY = dicts
        self.echo = echo
        self.ASSERTS = []
        self.BOUCLE=False
        self.STOP=False
        self.saveable=True

        self.l=0

    @abstractmethod
    def execute(self,*args):pass

    def eval_expr(self,l):
        l_ = []
        for i, elt in enumerate(l):
            res = default_types.full_typize(elt)
            if type(res) != type(None):
                l_.append(res)
            else:
                l_.append(elt)

        if len(l_) == 1 and type(l_[0]) != str:
            return l_[0]

        if len(l) == 1 and l[0][0] == '{' and l[0][-1] == '}':
            res = evaluations.evaluate_sets(l[0], self.VARIABLES, self.DICTIONARY, self.ALIAS, self.FUNCTIONS,self.OBJECTS, self)  # ,self.FUNCTIONS)
            return res
        else:
            l_ = evaluations.create_evaluating_list(l)
            evaluations.typize(l_)
            try:
                res = evaluations.evaluate(l_, self.VARIABLES, self.DICTIONARY, self.FUNCTIONS, self.ALIAS,self.OBJECTS, self)  # ,stdout=tools.StdRedirector(self.echo))
                return res
            except ZeroDivisionError:
                raise error.DividingByZero()

    def func_call(self,f,*args):
        if f not in self.FUNCTIONS: raise error.TypeError(f,typ=2)##
        #faire des copies
        cvar,cfct,calias,cdict,cobj = {},{},{},{},{}
        for k,v in self.VARIABLES.items():
            cvar[copy.copy(k)]=copy.copy(v)
        for k,v in self.FUNCTIONS.items():
            cfct[copy.copy(k)]=copy.copy(v)
        for k,v in self.ALIAS.items():
            calias[copy.copy(k)]=copy.copy(v)
        for k,v in self.DICTIONARY.items():
            cdict[copy.copy(k)]=copy.copy(v)
        for k,v in self.OBJECTS.items():
            cobj[copy.copy(k)]=copy.copy(v)

        self.FUNCTIONS[f].set_global_obj(cvar,cfct,calias,cdict,cobj)
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
            self.OBJECTS=self.FUNCTIONS[f].OBJ
        return r

    def test(self, name, expr):
        if name not in self.VARIABLES and name not in self.ALIAS:
            raise error.NameError(name)

        if name in self.ALIAS:
            name = self.ALIAS[name]

        value = self.eval_expr(expr.copy())
        if type(value) == str:
            if value == 'err':
                raise error.EvaluationError(expr)
            elif value == '0err':
                raise error.DividingByZero()
        return value, name

    def check_asserts(self):
        for tests in self.ASSERTS:
            res = self.eval_expr(tests)
            if type(res) != default_types.B and type(res) != type(None):
                raise error.WrongAssertion(tests)
            if type(res)==default_types.B and res.equiv(default_types.B(True)).v ==False:
                raise error.WrongAssertion(tests)

    def for_all_ex(self,code,f=False):
        if not (len(code) == 6 and code[2] == '∊' and code[4] == ':'): raise error.WrongSyntax()
        # Refaire !
        Ens_str = code[3]
        Ens:default_types.Iterable
        if Ens_str == 'ℕ':
            self.saveable = False
            Ens = default_types.Niterator()
        elif Ens_str in self.VARIABLES:
            if self.VARIABLES[Ens_str].type == default_types.S or type(
                    self.VARIABLES[Ens_str].type) == default_types.Parts:
                Ens = self.VARIABLES[Ens_str].get()
            else:
                raise error.IterationError(default_types.stringify(self.VARIABLES[Ens_str].type))
        elif len(Ens_str) >= 5 and Ens_str[0] == '⟦' and Ens_str[-1] == '⟧':
            Ens_str = Ens_str[1:-1].split(';')
            if len(Ens_str) != 2:
                raise error.WrongSyntax(*code)
            b1, b2 = self.eval_expr([Ens_str[0]]), self.eval_expr([Ens_str[1]])
            b1, b2 = convert(b1, default_types.Z), convert(b2, default_types.Z)
            Ens = default_types.ZIntervalle(b1, b2)
        else:
            raise error.WrongSyntax(*code)

        if code[1] in self.VARIABLES or code[1] in self.FUNCTIONS or code[1] in self.ALIAS or code[
            1] in self.DICTIONARY or code[1] in DEFAULT_FUNCTIONS:
            raise error.AlreadyExistsError(code[1])

        if code[3] == 'ℕ':
            self.VARIABLES[code[1]] = Variable.Variable(default_types.N, code[1])
        elif type(Ens) == default_types.ZIntervalle:
            Ens:default_types.ZIntervalle
            if Ens.binf >= default_types.N(0):
                self.VARIABLES[code[1]] = Variable.Variable(default_types.N, code[1])
            else:
                self.VARIABLES[code[1]] = Variable.Variable(default_types.Z, code[1])
        elif type(Ens) == default_types.S:
            self.VARIABLES[code[1]] = Variable.Variable(default_types.S, code[1])
        else:
            Ens: default_types.SET
            self.VARIABLES[code[1]] = Variable.Variable(Ens.type, code[1])
        self.VARIABLES[code[1]].set_glob(False)
        if not (len(code[5]) > 2 and code[5][0] == '\\' and code[5][-1] == '/'): raise error.WrongSyntax()
        run_code = code[5][1:-1]

        ex = LoopExecutor(run_code,self.echo,self.VARIABLES,self.FUNCTIONS,self.DICTIONARY,self.ALIAS,self.OBJECTS,f)

        r = ex.execute(Ens,code[1])
        self.suppr_var(code[1], False)
        return r

    @abstractmethod
    def suppr_var(self,*args):pass

    @abstractmethod
    def exec(self,*args):pass

    def dict_affect(self, code):
        if code[1] != '≔': raise error.WrongSyntax()
        obj = code[0]
        if obj.count('$') != 1: raise error.WrongSyntax()
        obj = obj.split('$')
        if obj[0] not in self.DICTIONARY:
            raise error.NameError(obj[0])

        k = self.eval_expr([obj[1]])
        v = self.eval_expr(code[2:])

        self.DICTIONARY[obj[0]][k] = v

    def echo_dec(self, name, typ, way):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES[name].__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(
            f"{kind} {name} created with type {typ if way == '∊' else chr(8472) + '(' + str(typ) + ')'}\n")

    def common_sentence_operation(self,ph):
        if self.STOP:return
        h = None
        try:
            if type(ph) != list:raise
            h = self.exec(ph)
        except error.Halt as err:
            if self.BOUCLE:
                self.BOUCLE = False
                self.STOP = False
                return
            raise err

        if h == error.Halt:
            if self.BOUCLE:
                self.BOUCLE = False
                return
            else:
                err = error.Halt()
                raise err

        if h == error.EOI:
            return error.EOI
        if h is not None:
            return h

    @abstractmethod
    def raise_error(self, *args):pass

    @abstractmethod
    def echo_affect(self,*args):pass

    def affect(self, name, expr: list[str]):
        value, name = self.test(name, expr)
        try:
            self.VARIABLES[name].set(value)
            self.echo_affect(name, value)
        except error.ConvertionError as _:

            if type(self.VARIABLES[name].type) == default_types.CrossSet or type(
                    self.VARIABLES[name].type) == default_types.Parts:
                reqtyp = self.VARIABLES[name].type
            else:
                reqtyp = default_types.TYPES_.get(self.VARIABLES[name].type, self.VARIABLES[name].type)

            if type(value) == default_types.Tuple:
                gettyp = value.type
            elif type(value) == default_types.SET:
                gettyp = value.type
            else:
                gettyp = default_types.TYPES_[type(value)]

            raise error.TypeError_(expr, name, gettyp, reqtyp)

    def dict_ex(self, nom, t1, t2,meth,flag=True):
        """Créer un dictionaire"""

        if nom in self.VARIABLES or nom in self.FUNCTIONS or nom in self.ALIAS or nom in self.DICTIONARY or nom in DEFAULT_FUNCTIONS:
            raise error.AlreadyExistsError(nom)
        if not (default_types.recognize_type(t1, self.OBJECTS)): raise error.TypeError(t1)
        if not (default_types.recognize_type(t2, self.OBJECTS)): raise error.TypeError(t2)
        t1, t2 = default_types.type_from_str(t1, self.OBJECTS), default_types.type_from_str(t2, self.OBJECTS)
        self.DICTIONARY[nom] = Dictionnary.Dictionnary(t1, t2, nom, meth)
        self.DICTIONARY[nom].set_glob(flag)

class FuncExecutor(BaseEx):
    def __init__(self, code, echo, var, func, dic, alias, obj, name, is_meth=False, father=''):
        super().__init__({k:v for k,v in var.items() if k!='me' and v.glob}, func, {k:v for k,v in dic.items() if v.glob}, {k:v for k,v in alias.items() if v.glob}, obj, echo)
        self.code = code

        self.name = name
        self.father = father
        self.method = is_meth
        self.returned, self.return_obj = False, default_types.EmptySet()
        self.flag=False

    def set_args(self,args):
        for k,v in args.items():
            self.VARIABLES[k]=v

    def create_variable(self, name, typ, way='∊'):
        for elt in (self.VARIABLES, self.FUNCTIONS, self.ALIAS, self.DICTIONARY):
            if name in elt:
                elt["GLOBAL·" + name] = elt[name]
                del elt[name]
        if name in DEFAULT_FUNCTIONS:
            raise error.AlreadyExistsError(name)
        if 'set_of' in typ:
            typ = self.eval_expr([typ])
        if not (default_types.recognize_type(typ, self.OBJECTS)):
            raise error.TypeError(typ)

        if way == '∊':
            self.VARIABLES[name] = Variable.create_var(default_types.type_from_str(typ, self.OBJECTS), name,
                                                       self.method)  # [default_types.type_from_str(typ),None]
        else:
            self.VARIABLES[name] = Variable.create_var(
                default_types.Parts(default_types.type_from_str(typ, self.OBJECTS)), name)
        self.VARIABLES[name].set_glob(False)
        self.echo_dec(name, typ, way)

    def create_alias(self, name, ref):
        if name in self.VARIABLES or name in self.FUNCTIONS or name in self.ALIAS or name in self.DICTIONARY or name in DEFAULT_FUNCTIONS:
            raise error.AlreadyExistsError(name)
        if ref not in self.VARIABLES and ref not in self.ALIAS:
            raise error.UnknownObject(ref)
        al = Variable.Alias(name, ref if ref not in self.ALIAS else self.ALIAS[ref].name)
        al.set_glob(False)
        self.ALIAS[name] = al

    def execute(self, code='',flag=True):  # ,echoflag=True):,
        defstdout = sys.stdout
        defstdin = sys.stdin

        if self.echo is not None:
            sys.stdout = tools.StdRedirector(self.echo)
            sys.stdin = tools.StdRedirector(self.echo)

        # Ctrl+C : break self.echo.bind("")
        if code == '': code = self.code
        if type(code)==str:code = _parser_.parse(code,self.OBJECTS)

        if self.echo is not None and self.echo.active: self.echo.declare(
            f"Inside {'method' if self.method else 'function'} {self.name} {'of ' + self.father if self.father != '' else ''}\n")

        self.l = 1
        if self.echo is not None: self.echo.bind_all('<Control-c>', self.raise_end)
        for i, ph in enumerate(code):
            try:
                r = self.common_sentence_operation(ph)
            except (error.Error,error.InFunctionError,exceptions.RunTimeException) as err:
                if not self.flag:raise error.InFunctionError(err,''.join(ph),self.name)
                raise err
            if flag and (self.STOP or self.returned): break
            if not flag and r is not None:return r
            self.l += 1
            if self.echo is not None: self.echo.update()
        if self.echo is not None:
            sys.stdout = defstdout
            sys.stdin = defstdin

        if self.echo is not None: self.echo.unbind_all('<Control-c>')
        if self.echo is not None and self.echo.active: self.echo.declare(
            f"Outside {'method' if self.method else 'function'} {self.name} {'of ' + self.father if self.father != '' else ''}\n")
        return self.return_obj

    def raise_end(self, _):
        self.STOP = True
        self.raise_error("Keyboard Interupt", '')

    def exec(self, ph):
        match ph:
            case ['∃', name, ('∊' | '⊆') as way, typ]:
                self.create_variable(name, typ, way)
            case [v1, '≜', v2]:
                self.create_alias(v1, v2)
            case [thing, '≔', *r]:
                if '$' in thing:
                    self.dict_affect(ph)
                else:
                    self.affect(thing, r)
            case [thing] if thing != '' and thing[0] == '@':
                match thing[1:].split(' '):
                    case ['HIDE']:
                        self.echo.active = False
                    case ['SHOW']:
                        self.echo.active = True
                    case ['HALT']:
                        return error.Halt
                    case ['CONTINUE']:
                        return error.EOI
                    case ['WAIT']:
                        time.sleep(3e-3)
                    case ['BELL'] if self.echo is not None:
                        self.echo.bell()
                    case ['RAISE', *excep]:
                        raise exceptions.get_exception(' '.join(excep))
                    case _:
                        raise error.UnknownObject(thing)
            case ['□', *expr]:
                if expr not in self.ASSERTS: self.ASSERTS.append(expr)
            case ['¬', '□', *expr]:
                if expr in self.ASSERTS:
                    self.ASSERTS.remove(expr)
            case ['∀', *_]:
                r = self.for_all_ex(ph,True)
                if r is not None:
                    self.returned = True
                    self.return_obj = r
            case [nom, ':', typ1, '⇴', typ2]:
                self.dict_ex(nom, typ1, typ2,self.method,False)  # refaire
            case ['➣', *_]:
                r = self.if_ex(ph)
                if r == error.EOI: return r
                if r == error.Halt: return r
            case ['⟼', *expr]:
                self.returned = True
                if expr:
                    r = self.eval_expr(expr)
                    self.return_obj = r
            case []:
                pass
            case _:

                if any([elt in _parser_.kw for elt in ph]):
                    raise error.WrongSyntax()
                self.eval_expr(ph)

        self.check_asserts()

    def raise_error(self, err, mes):
        self.STOP = True
        if self.echo is not None: self.echo.raise_error(err + ' has occured at line n°' + str(self.l) + '\n' + mes + '\n')

    def echo_del(self, name):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES.get(name, Variable.Alias).__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has been destroyed successfully\n")

    def echo_affect(self, name, value):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES[name].__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has recieved the value : {value}\n")

    def echo_inf(self, inf):
        if self.echo is None or not self.echo.active: return
        if self.echo is not None: self.echo.informe_main(inf + '\n')

    def if_ex(self, code):
        expr = []
        if code[0] != '➣': raise error.WrongSyntax()
        i = 1
        ex = False
        while i < len(code):
            elt = code[i]

            if ex:
                ex = False
                res = self.eval_expr(expr)
                if type(res) != default_types.B: raise
                if res.v:
                    if not (elt[0] == '\\' and elt[-1] == '/'): raise error.WrongSyntax()
                    run_code = elt[1:-1]
                    try:res = self.execute(_parser_.parse(run_code))
                    except error.InFunctionError as err:
                        self.flag=True
                        raise err
                    if res == error.Halt:
                        return error.Halt
                    if res == error.EOI:
                        return error.EOI
                    if res:
                        self.STOP = True
                    return
            elif elt == '⇝':
                ex = True
            elif elt == '➣':
                expr = []
            else:
                expr.append(elt)

            i += 1

    def suppr_var(self, var, flag=True):
        if var in self.VARIABLES:
            del self.VARIABLES[var]
        elif var in self.ALIAS:
            del self.ALIAS[var]
        else:
            raise error.UnknownObject(var)

        if flag: self.echo_del(var)

class Executor(BaseEx):
    def __init__(self, echo):
        super().__init__({}, {}, {}, {}, {}, echo)
        if not os.path.exists("dcache"):
            os.mkdir("dcache")
        self.STATUS = {"__NAME__": '__main__', "__DOC__": ''}
        self.saveable = True
        self.l = 1

        self.text=''
        self.parsed=[]

    def create_variable(self, name, typ, way='∊'):
        if name in self.VARIABLES or name in self.FUNCTIONS or name in self.ALIAS or name in self.DICTIONARY or name in DEFAULT_FUNCTIONS or name in self.OBJECTS:
            raise error.AlreadyExistsError(name)
        if len(typ) == 1:
            typ = typ[0]
        if 'set_of' in typ:
            typ = default_types.stringify(self.eval_expr([typ]))
        if not (default_types.recognize_type(typ, self.OBJECTS)):
            raise error.TypeError(typ)
        typ = default_types.type_from_str(typ, self.OBJECTS)

        if way == '∊':
            self.VARIABLES[name] = Variable.create_var(typ, name)
        else:
            self.VARIABLES[name] = Variable.create_var(default_types.Parts(typ), name)

        self.echo_dec(name, stringify(typ), way)

    def affect(self, name, expr: list[str]):
        if name in self.STATUS:
            self.set_status(name, expr)
            return

        super().affect(name,expr)

    def set_status(self, name, expr):
        if name == '__NAME__': raise  ####
        value = self.eval_expr(expr.copy())
        if type(value) == str:
            if value == 'err':
                raise error.EvaluationError(expr)
            elif value == '0err':
                raise error.DividingByZero()
        if type(value) != default_types.S:
            raise error.TypeError_(expr, name, stringify(type(value)), stringify(default_types.S))

        self.STATUS[name] = value.value

    def suppr_var(self, var, flag=True):
        if var in self.VARIABLES:
            del self.VARIABLES[var]
        elif var in self.ALIAS:
            del self.ALIAS[var]
        else:
            raise error.UnknownObject(var)

        if flag: self.echo_del(var)

    def create_alias(self, name, ref):
        if name in self.VARIABLES or name in self.FUNCTIONS or name in self.ALIAS or name in self.DICTIONARY or name in DEFAULT_FUNCTIONS or name in self.OBJECTS:
            raise error.AlreadyExistsError(name)
        if ref not in self.VARIABLES and ref not in self.ALIAS:
            raise error.UnknownObject(ref)

        al = Variable.Alias(name, ref if ref not in self.ALIAS else self.ALIAS[ref].name)
        al.set_glob(False)

    def execute(self, txt: str, flag=True, name=''):
        self.text = txt
        self.parsed = _parser_.parse(txt,self.OBJECTS)

        defstdout = sys.stdout
        defstdin = sys.stdin

        if self.echo is not None:
            sys.stdout = tools.StdRedirector(self.echo)
            sys.stdin = tools.StdRedirector(self.echo)

        # Ctrl+C : break self.echo.bind("")

        self.STOP = False
        if flag: self.echo_inf("==COMMENCEMENT D'EXECUTION==")
        t = time.time()
        if self.echo is not None: self.echo.bind_all('<Control-c>', self.raise_end)
        for i, ph in enumerate(self.parsed):
            self.l = i+1
            if self.OBJECTS != {}: _parser_.recognize_cross_set(ph, self.OBJECTS)
            try:
                self.common_sentence_operation(ph)
            except (error.Error, exceptions.RunTimeException,error.InFunctionError)as err:
                self.raise_error(err.name(),str(err),ph)
            if self.STOP: break

            if self.echo is not None: self.echo.update()

        if self.echo is not None:
            sys.stdout = defstdout
            sys.stdin = defstdin

        if flag:
            print('Variables :\n', self.VARIABLES, '\nDictionnaire :\n', self.DICTIONARY, '\nFonctions :\n',
                  self.FUNCTIONS, '\nAlias :\n', self.ALIAS, '\nObjets : \n', self.OBJECTS, '\nBOUCLE :', self.BOUCLE,
                  '\nStatus : \n ', self.STATUS)
            self.echo_inf("==FIN D'EXECUTION==" + str(time.time() - t))

        if self.echo is not None: self.echo.unbind_all('<Control-c>')
        return self.STOP

    def raise_end(self, *_):
        self.STOP = True
        self.raise_error("Keyboard Interupt", '','')

    def exec(self, ph):
        match ph:
            case ['∃', name, '⊃', 'Ω']:
                if '⟨' in name:
                    l = name.split('⟨')
                    l[1] = l[1].replace('⟩', '')
                    E = l[1]
                    assert E in ('𝕋', "𝕂")
                    name = l[0]
                    if name in self.VARIABLES or name in self.FUNCTIONS or name in self.ALIAS or name in self.DICTIONARY or name in DEFAULT_FUNCTIONS or name in self.OBJECTS:
                        raise error.AlreadyExistsError(name)
                    self.OBJECTS[name] = POO.ParametrizedObject(name, self.echo, E)
                else:
                    if name in self.VARIABLES or name in self.FUNCTIONS or name in self.ALIAS or name in self.DICTIONARY or name in DEFAULT_FUNCTIONS or name in self.OBJECTS:
                        raise error.AlreadyExistsError(name)
                    self.OBJECTS[name] = POO.Object(name, self.echo)
            case ['∃', name, ('∊' | '⊆') as way, *typ]:
                self.create_variable(name, typ, way)
            case [v1, '≜', v2]:
                self.create_alias(v1, v2)
            case ['∄', var]:
                self.suppr_var(var)
            case [thing, '≔', *r]:
                if '$' in thing:
                    self.dict_affect(ph)
                else:
                    self.affect(thing, r)
            case [thing] if thing != '' and thing[0] == '@':
                match thing[1:].split(' '):
                    case ['HIDE']:
                        self.echo.active = False
                    case ['SHOW']:
                        self.echo.active = True
                    case ['HALT']:
                        return error.Halt
                    case ['CONTINUE']:
                        return error.EOI
                    case ['WAIT']:
                        time.sleep(3e-3)
                    case ['BELL'] if self.echo is not None:
                        self.echo.bell()
                    case ['RAISE', *ph]:
                        raise exceptions.get_exception(' '.join(ph))
                    case _:
                        raise error.UnknownObject(ph[0])
            case ['□', *expr]:
                if expr not in self.ASSERTS: self.ASSERTS.append(expr)
            case ['¬', '□', *expr]:
                if expr in self.ASSERTS:
                    self.ASSERTS.remove(expr)
            case ['∀', *_]:
                self.for_all_ex(ph)
            case [nom, ':', typ1, '⇴', typ2]:
                self.dict_ex(nom, typ1, typ2,False)  # refaire
            case ['➣', *_]:
                r = self.if_ex(ph)
                if r == error.EOI: return r
            case [nom, ':', t1, '⟶', t2]:
                if not default_types.recognize_type(t1, self.OBJECTS):
                    raise error.TypeError(t1)
                if not default_types.recognize_type(t2, self.OBJECTS):
                    raise error.TypeError(t2)
                if nom in self.VARIABLES or nom in self.FUNCTIONS or nom in self.ALIAS or nom in self.DICTIONARY or nom in DEFAULT_FUNCTIONS or nom in self.OBJECTS:
                    raise error.AlreadyExistsError(nom)
                self.FUNCTIONS[nom] = Callable.Applications(nom, t1, t2, self.OBJECTS)
            case [nom, ':', vars, '⟼', *return_]:
                if nom not in self.FUNCTIONS: raise
                f: Callable.Applications = self.FUNCTIONS[nom]
                f.set_args_name(*vars.split(';'))
                f.set_expr(return_)
            case [thing] if len(thing) > 2 and thing[0] == thing[-1] == '#':
                self.create_func_meth(thing)
            case _:
                if any([elt in _parser_.kw for elt in ph]):
                    raise error.WrongSyntax()
                self.eval_expr(ph)
        self.check_asserts()

    def raise_error(self, err, mes,ph):
        self.STOP = True
        if self.echo is not None:
            self.echo.raise_error(err + ' has occured at line n°' + str(self.l)+" :\n "+''.join(ph) + '\n' + mes + '\n')

    def echo_del(self, name):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES.get(name, Variable.Alias).__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has been destroyed successfully\n")

    def echo_affect(self, name, value):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES[name].__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has recieved the value : {value}\n")

    def echo_inf(self, inf):
        if self.echo is None or not self.echo.active: return
        if self.echo is not None: self.echo.informe_main(inf + '\n')

    def eval_expr(self, l: list[str]):
        if any('ask' in obj for obj in l):
            self.saveable = False

        ph_ = []
        for i, elt in enumerate(l):
            if i == 0:
                ph_.append(elt)
            elif elt[0] == '$':
                ph_[-1] += elt
            elif elt[0] in _parser_.t or elt[0] in _parser_.indic and ph_[-1][-1] == '$':
                ph_[-1] += elt
            else:
                ph_.append(elt)
        l = ph_
        return super().eval_expr(l)

    def if_ex(self, code):
        expr = []
        if code[0] != '➣': raise error.WrongSyntax()
        i = 1
        ex = False
        while i < len(code):
            elt = code[i]

            if ex:
                ex = False
                res = self.eval_expr(expr)

                if type(res) != default_types.B: raise
                if res.v:
                    if not (elt[0] == '\\' and elt[-1] == '/'): raise error.WrongSyntax()
                    run_code = elt[1:-1]
                    res = self.execute(run_code, flag=False)
                    if res == error.Halt:
                        raise error.Halt
                    if res == error.EOI:
                        return error.EOI
                    if res:
                        self.STOP = True
                    return
            elif elt == '⇝':
                ex = True
            elif elt == '➣':
                expr = []
            else:
                expr.append(elt)

            i += 1

    def create_func_meth(self, code):
        code_ = code[1:-1]
        code_ = _parser_.parse(code_, self.OBJECTS)
        if len(code_) <= 2: raise error.WrongSyntax()
        if len(code_[0]) != 5: raise error.WrongSyntax()
        if '·' in code_[0][0]:
            self.create_method(code)
        else:
            self.create_function(code)

    def create_method(self, code):
        code_ = code[1:-1]
        code_ = _parser_.parse(code_)
        if len(code_) <= 2: raise error.WrongSyntax()
        if len(code_[0]) != 5: raise error.WrongSyntax()
        nom = code_[0][0]
        nom = nom.split('·')
        if nom[0] not in self.OBJECTS:
            raise error.NameError(nom[0], 2)
        obj = self.OBJECTS[nom[0]]

        if nom[1]=='check':
            if type(obj) != POO.ParametrizedObject:
                raise error.AttributeError('check',obj.name)
            obj.add_check(code,self.OBJECTS)
        else:
            obj.add_method(code, self.OBJECTS)

    def create_function(self, code):
        code = code[1:-1]
        code = _parser_.parse(code)
        if len(code) <= 2: raise error.WrongSyntax()
        if len(code[0]) != 5: raise error.WrongSyntax()
        if code[0][0] in self.VARIABLES or code[0][0] in self.FUNCTIONS or code[0][0] in self.ALIAS or code[0][
            0] in self.DICTIONARY or code[0][0] in DEFAULT_FUNCTIONS: raise error.AlreadyExistsError(code[0][0])
        if code[0][1] != ':' or code[0][3] != '⟶': raise error.WrongSyntax()
        if not default_types.recognize_type(code[0][2], self.OBJECTS): raise error.TypeError(code[0][2])
        if not default_types.recognize_type(code[0][4], self.OBJECTS): raise error.TypeError(code[0][4])

        self.FUNCTIONS[code[0][0]] = Callable.Function(code[0][0],
                                                        default_types.type_from_str(code[0][2], self.OBJECTS),
                                                        default_types.type_from_str(code[0][4], self.OBJECTS))
        if not (len(code[1]) == 1 and code[1][0][0] == '⟨' and code[1][0][-1] == '⟩'):
            raise error.WrongSyntax()
        args = code[1][0][1:-1].split(';')
        self.FUNCTIONS[code[0][0]].set_args_name(*args)
        i = 2
        if code[i] == ['@GLOBAL']:
            self.FUNCTIONS[code[0][0]].set_global()
            i += 1
        if code[i] == ['@RESTRICT']:
            self.FUNCTIONS[code[0][0]].set_restricted()
            i += 1
        if code[i][0][0] == code[i][0][-1] == '"':
            self.FUNCTIONS[code[0][0]].set_doc(code[i][0][1:-1])
            i += 1
        if not code[i:]: raise error.WrongSyntax()
        self.FUNCTIONS[code[0][0]].set_code(code[i:])

class LoopExecutor(BaseEx):
    def echo_affect(self, name, value):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES[name].__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has recieved the value : {value}\n")

    def execute(self, Ens,var_name):
        for elt in Ens:
            try:
                self.VARIABLES[var_name].set(elt)
                r = self.sub_ex(self.code)
                self.echo.update()
                if r is not None:
                    self.echo.update()
                    return r
            except error.EOI:
                pass
            except error.Halt:
                return

    def sub_ex(self,code):
        for ph in code:
            r = self.exec(ph)
            if r is not None:
                self.echo.update()
                return r

    def echo_del(self, name):
        if self.echo is None or not self.echo.active: return
        kind = self.VARIABLES.get(name, Variable.Alias).__name__
        if kind == 'Attribute': kind = '\t' + kind
        self.echo.declare(f"{kind} {name} has been destroyed successfully\n")

    def suppr_var(self, var, flag=True):
        if var in self.VARIABLES:
            del self.VARIABLES[var]
        elif var in self.ALIAS:
            del self.ALIAS[var]
        else:
            raise error.UnknownObject(var)

        if flag: self.echo_del(var)

    def exec(self, ph):
        match ph:
            case ['∃', _, '⊃', 'Ω']:
                raise error.CreationError('object')
            case ['∃', _, ('∊' | '⊆'), *_]:
                raise error.CreationError('variable')
            case [_, '≜', _]:
                raise error.CreationError('alias')
            case ['∄', var]:
                self.suppr_var(var)
            case [thing, '≔', *r]:
                if '$' in thing:
                    self.dict_affect(ph)
                else:
                    self.affect(thing, r)
            case [thing] if thing != '' and thing[0] == '@':
                match thing[1:].split(' '):
                    case ['HIDE']:
                        self.echo.active = False
                    case ['SHOW']:
                        self.echo.active = True
                    case ['HALT']:
                        raise error.Halt
                    case ['CONTINUE']:
                        raise error.EOI
                    case ['WAIT']:
                        time.sleep(3e-3)
                    case ['BELL'] if self.echo is not None:
                        self.echo.bell()
                    case ['RAISE', *ph]:
                        raise exceptions.get_exception(' '.join(ph))
                    case _:
                        raise error.UnknownObject(ph[0])
            case ['□', *expr]:
                if expr not in self.ASSERTS: self.ASSERTS.append(expr)
            case ['¬', '□', *expr]:
                if expr in self.ASSERTS:
                    self.ASSERTS.remove(expr)
            case ['∀', *_]:
                r = self.for_all_ex(ph)
                if r is not None:
                    return r
            case [_, ':', _, '⇴', _]:
                raise error.CreationError('dictionnary')
            case ['➣', *_]:
                r = self.if_ex(ph)
                if r is not None:
                    return r
            case [_, ':', _, '⟶', _]:
                raise error.CreationError('application')
            case [thing] if len(thing) > 2 and thing[0] == thing[-1] == '#':
                raise error.CreationError('function')
            case ['⟼', *expr] if self.is_func:
                if expr:
                    return self.eval_expr(expr)
                else:
                    return default_types.EmptySet()
            case _:
                if any([elt in _parser_.kw for elt in ph]):
                    raise error.WrongSyntax()
                self.eval_expr(ph)
        self.check_asserts()

    def raise_error(self, *args):
        pass

    def __init__(self, code, echo, var, func, dic, alias, obj,f):
        super().__init__(var, func, dic, alias, obj, echo)
        self.code = _parser_.parse(code,obj)
        self.is_func = f

    def if_ex(self, code):
        expr = []
        if code[0] != '➣': raise error.WrongSyntax()
        i = 1
        ex = False
        while i < len(code):
            elt = code[i]

            if ex:
                ex = False
                res = self.eval_expr(expr)

                if type(res) != default_types.B: raise
                if res.v:
                    if not (elt[0] == '\\' and elt[-1] == '/'): raise error.WrongSyntax()
                    run_code = elt[1:-1]
                    r = self.sub_ex(_parser_.parse(run_code))
                    return r
            elif elt == '⇝':
                ex = True
            elif elt == '➣':
                expr = []
            else:
                expr.append(elt)

            i += 1


import default_functions,default_types, Executor,error,Variable

class Function:
    def __init__(self,name,t_in,t_out):
        self.name=name
        assert default_types.recognize_type(t_in) and default_types.recognize_type(t_out)
        self.types = (default_types.type_from_str(t_in),default_types.type_from_str(t_out))
        self.gl_bal=False
        self.restricted = False
        self.arg_names=()
        self.__doc__=''
        self.VAR,self.FUNC,self.ALIAS,self.DICT={},{},{},{}
        valid_name(name)
    
    def set_doc(self,ch:str):
        self.__doc__=ch

    def set_args_name(self,*noms:str):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
           if noms!=('∅',) and noms != ('',):
                raise error.UnexpectedArgument(given=len(noms),req=1,wanted='∅')
           self.arg_names=()
        for elt in noms:
            if type(elt)!=str:raise error.InvalidName(elt)
        if (type(self.types[0])!=default_types.CrossSet and len(noms)!=1):
            raise error.UnexpectedArgument(given=len(noms),req=1)
        elif type(self.types[0])==default_types.CrossSet and (default_functions.dim(self.types[0])!= default_types.N(len(noms))):
            raise error.UnexpectedArgument(given=len(noms),req=default_functions.dim(self.types[0]).value)
        self.arg_names = noms

    def set_global(self):
        self.gl_bal=True
    
    def set_restricted(self):
        self.restricted=True

    def right_access(self,ex):
        if type(ex) == Executor.Executor and self.restricted:
            raise error.DeniedAccessError(self.name)

    def set_code(self,code):
        self.code=code #liste deja parsee
        
        r = "#\n"
        r+=self.name + ' : '+default_types.stringify(self.types[0]) + ' ⟶ '+default_types.stringify(self.types[1]) + '.\n'
        r +='⟨'+';'.join(self.arg_names)+'⟩.\n'
        l=[]
        for elt in self.code:
            l.append(' '.join(elt)+'.')
        r += '\n'.join(l)
        r+='\n#'
        if self.__doc__=='':self.__doc__=r
        self.__repr = r

    def set_global_obj(self,var,func,alias,dic):
        self.VAR,self.FUNC,self.ALIAS,self.DICT={},{},{},{}
        for k in [(var,self.VAR),(func,self.FUNC),(alias,self.ALIAS),(dic,self.DICT)]:
            for elt in k[0]:
                if elt in self.arg_names:
                    k[1]["GLOBAL·"+elt]=k[0][elt]
                else:
                    k[1][elt]=k[0][elt]
        
        

    def __call__(self,echo,*vals):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            if vals!=():
                raise error.UnexpectedArgument(given=len(vals),req=0)
        elif type(self.types[0])!=default_types.CrossSet:
            if len(vals)!=1:
                raise error.UnexpectedArgument(given=len(vals),req=1)
            var= Variable.Variable(self.types[0],self.arg_names[0])
            var.set(vals[0])
            self.VAR[self.arg_names[0]]=var
        else:
            if len(vals)!=default_functions.dim(self.types[0]):
                raise error.UnexpectedArgument(given=len(vals),req=default_functions.dim(self.types[0]).value)
            for i in range(len(self.arg_names)):
                var= Variable.Variable(self.types[0][i],self.arg_names[i])
                var.set(vals[i])
                self.VAR[self.arg_names[i]]=var

        ex = Executor.FuncExecutor(self.code,echo,self.VAR,self.FUNC,self.ALIAS,self.DICT)#il faut le coder !
        res=ex.execute()
        if self.types[1]==default_types.Parts(default_types.EmptySet):
            if type(res) == default_types.EmptySet:
                return res
            raise 
        return default_functions.convert(res,self.types[1])

    def __str__(self) -> str:
        return self.__doc__
    
    def __repr__(self) -> str:
        return self.__repr

def valid_name(ch:str):
    if ch =='' or ' ' in ch:
        raise error.InvalidName(ch)
    if ch[0] not in 'abcdefghijklmnopqrstuvwxyz':
        raise error.InvalidName(ch)
    if any(car not in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch):
        raise error.InvalidName(ch)

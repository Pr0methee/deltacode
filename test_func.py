import default_types,evaluations,_parser_,default_functions,error,Executor

class Function:
    def __init__(self,name,t_in,t_out,echo):
        self.name=name
        assert default_types.recognize_type(t_in) and default_types.recognize_type(t_out)
        self.types = (default_types.type_from_str(t_in),default_types.type_from_str(t_out))
        self.gl_bal=False
        self.arg_names=()
        self.echo=echo
    
    def set_args_name(self,*noms:str):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
           assert noms==('∅',)
           self.arg_names=()
        assert all(type(elt)==str for elt in noms)
        assert (type(self.types[0])!=default_types.CrossSet and len(noms)==1) or (default_functions.dim(self.types[0]) == default_types.N(len(noms)))
        self.arg_names = noms

    def set_global(self):
        self.gl_bal=True

    def set_code(self,code):
        self.code=code #liste deja parsee

    def set_global_obj(self,var,func,alias,dic):
        self.VAR,self.FUNC,self.ALIAS,self.DICT={},{},{},{}
        for k in [(var,self.VAR),(func,self.FUNC),(alias,self.ALIAS),(dic,self.DICT)]:
            for elt in k[0]:
                if elt in self.arg_names:
                    k[1]["GLOBAL·"+elt]=k[0][elt]
                else:
                    k[1][elt]=k[0][elt]
        
        

    def __call__(self,*vals):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            assert vals==()
        elif type(self.types[0])!=default_types.CrossSet:
            assert default_types.include(type(vals[0]),self.types[0])
            self.VAR[self.arg_names[0]]=[self.types[0],vals[0]]
        else:
            for i in range(len(self.arg_names)):
                assert default_types.include(type(vals[i]),self.types[0][i])
                self.VAR[self.arg_names[i]]=[self.types[0][i],vals[i]]

        ex = Executor.FuncExecutor(self.code,self.echo,self.VAR,self.FUNC,self.ALIAS,self.DICT)#il faut le coder !
        res=ex.execute()
        return default_functions.convert(res,self.types[1])

    def __str__(self) -> str:
        r = "#\n"
        r+=self.name + ' : '+default_types.stringify(self.types[0]) + ' ⟶ '+default_types.stringify(self.types[1]) + '.\n'
        r +='⟨'+';'.join(self.arg_names)+'⟩.\n'
        l=[]
        for elt in self.code:
            l.append(' '.join(elt)+'.')
        r += '\n'.join(l)
        r+='\n#'
        return r
    
    def __repr__(self) -> str:
        return self.__str__()

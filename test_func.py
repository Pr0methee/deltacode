import default_types,evaluations,_parser_,default_functions,error

class Function:
    def __init__(self,name,t_in,t_out):
        self.name=name
        assert default_types.recognize_type(t_entree) and default_types.recognize_type(t_sortie)
        self.types = (default_types.type_from_str(t_entree),default_types.type_from_str(t_sortie))
        self.global=False
        self.arg_names=()
    
    def set_args_name(self,*noms:str):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
           assert noms==('∅',)
           self.arg_names=()
        assert all(type(elt)==str for elt in noms)
        assert default_functions.dim(self.types[0]) == default_types.N(len(noms))
        self.arg_names = noms

    def set_global(self):
        self.global=True

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
        
        

    def __call_(self,*vals):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            assert vals==()
            ARGS={}
        elif type(self.types[0])!=default_types.CrossSet:
            assert default_types.include(type(vals[0]),self.types[0])
            ARGS = {
                self.arg_names[0]:[self.types[0],vals[0]]
            }
        else:
            ARGS = {}
            for i in range(len(self.arg_names)):
                assert default_types.include(type(vals[i]),self.types[0][i])
                ARGS[self.arg_names[i]]=[self.types[0][i],vals[i]]

        res = executor.FuncExec(self.code,self.VAR,self.FUNC,self.ALIAS,self.DICT)#il faut le coder !
        return default_functions.convert(res,self.types[1])

import default_types,evaluations,_parser_,default_functions,error


class Applications:
    def __init__(self,nom:str,t_entree,t_sortie) -> None:
        self.name =nom
        assert default_types.recognize_type(t_entree) and default_types.recognize_type(t_sortie)
        self.types = (default_types.type_from_str(t_entree),default_types.type_from_str(t_sortie))

    def set_args_name(self,*noms:str):
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            if noms!=('∅',):
                raise error.UnexpectedArgument(given=len(noms),req=1,wanted='∅')
            self.arg_names=()
        for elt in noms:
            if type(elt)!=str:raise error.InvalidName(elt)
        if (type(self.types[0])!=default_types.CrossSet and len(noms)!=1):
            raise error.UnexpectedArgument(given=len(noms),req=1)
        if (default_functions.dim(self.types[0])!= default_types.N(len(noms))):
            raise error.UnexpectedArgument(given=len(noms),req=default_functions.dim(self.types[0]).value)
        self.arg_names = noms
    
    def set_expr(self,expr):
        if type(expr)!=list:expr=[expr]
        self.expr =expr
    
    def __call__(self,*vals):
        print(len(vals))
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            if vals!=():
                raise error.UnexpectedArgument(given=len(vals),req=0)
            ARGS={}
        elif type(self.types[0])!=default_types.CrossSet:
            if len(vals)!=1:
                raise error.UnexpectedArgument(given=len(vals),req=1)
            ARGS = {
                self.arg_names[0]:[self.types[0],default_functions.convert(self.types[0],vals[0])]
            }
        else:
            ARGS = {}
            if len(vals)!=default_functions.dim(self.types[0]):
                raise error.UnexpectedArgument(given=len(noms),req=default_functions.dim(self.types[0]).value) 
            for i in range(len(self.arg_names)):
                ARGS[self.arg_names[i]]=[self.types[0][i],default_functions.convert(self.types[0][i],vals[i])]
        FUNC = {self.name:self}
        if self.expr[0] == "➣":
            l = split(self.expr)
            for case in l:
                cond,expr=cut(case)
                r = evaluations.create_evaluating_list(cond)
                evaluations.typize(r)
                r = evaluations.evaluate(r,ARGS,{},FUNC,{},None)
                if type(r) != default_types.B:
                    raise error.TypeError()
                if r.v:
                    
                    l=evaluations.create_evaluating_list(expr)
                    evaluations.typize(l)
                    r = evaluations.evaluate(l,ARGS,{},FUNC,{},None)#liste parsee, transformee en evaluating list, typee
                    return default_functions.convert(r,self.types[1])
            raise
        else:
            l=evaluations.create_evaluating_list(self.expr)
            evaluations.typize(l)
            r = evaluations.evaluate(l,ARGS,{},FUNC,{},None)#liste parsee, transformee en evaluating list, typee
        return default_functions.convert(r,self.types[1])
    
    def __str__(self) -> str:
        r= self.name+' : '+default_types.stringify(self.types[0])+' ⟶  '+default_types.stringify(self.types[1])
        try:
            r+='\n'+';'.join(self.arg_names) + ' ⟼  '+''.join(self.expr)
        except:pass
        return r
    def __repr__(self) -> str:
        return self.__str__()


def split(ch):
    l=[[]]
    for car in ch:
        if car == '➣' and l[-1] != []:
            l.append([])
        l[-1].append(car)
    return l

def cut(ch):
    cond=[]
    expr = []
    c=True
    for car in ch:
        if car ==':':
            c=False
        if car =='➣' or car ==':':
            continue
        if c:
            cond.append(car)
        else:
            expr.append(car)
    return cond,expr

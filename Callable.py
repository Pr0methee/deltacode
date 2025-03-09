import copy

import default_functions,default_types, error,BaseEx,evaluations

class Callable:
    def __init__(self,name,t_in,t_out):
        self.name = name
        self.types = (t_in, t_out)
        self.arg_names=()
        valid_name(name)

    def __call__(self, *vals)->dict:
        ARGS = {}
        if self.types[0] == default_types.Parts(default_types.EmptySet):
            if vals != ():
                raise error.UnexpectedArgument(given=len(vals), req=0)
        elif type(self.types[0]) != default_types.CrossSet:
            if len(vals) != 1:
                raise error.UnexpectedArgument(given=len(vals), req=1)
            ARGS = {self.arg_names[0]: FixedVariable(self.types[0], self.arg_names[0], vals[0])}
        else:
            if (len(vals) == 1) and type(vals[0]) == default_types.Tuple:
                vals = default_functions.convert(vals[0], self.types[0])
            else:
                if len(vals) != default_functions.dim(self.types[0]).value:
                    raise error.UnexpectedArgument(given=len(vals), req=default_functions.dim(self.types[0]).value)

            for i, n in enumerate(self.arg_names):
                ARGS[n] = FixedVariable(self.types[0][i], self.arg_names[i], vals[i])
        return ARGS

    def set_args_name(self, *noms: str):

        if self.types[0] == default_types.Parts(default_types.EmptySet):
            if noms != ('∅',):
                raise error.UnexpectedArgument(given=len(noms), req=1, wanted='∅')
            self.arg_names = ()
        for elt in noms:
            if type(elt) != str: raise error.InvalidName(elt)

        if type(self.types[0]) != default_types.CrossSet and len(noms) != 1:
            raise error.UnexpectedArgument(given=len(noms), req=1)
        elif type(self.types[0]) == default_types.CrossSet and (
                default_functions.dim(self.types[0]) != default_types.N(len(noms))):
            raise error.UnexpectedArgument(given=len(noms), req=default_functions.dim(self.types[0]).value)
        self.arg_names = noms

class Function(Callable):
    def __init__(self, name, t_in, t_out, method=False):
        super().__init__(name,t_in,t_out)
        self.gl_bal = False
        self.restricted = False
        self.__doc__ = ''
        self.VAR, self.FUNC, self.ALIAS, self.DICT, self.OBJ = {}, {}, {}, {}, {}
        self.is_meth = method
        self.static=False
        self.__repr=''
        self.code=[]

    def set_doc(self, ch: str):
        self.__doc__ = ch

    def set_global(self):
        self.gl_bal = True

    def set_restricted(self):
        self.restricted = True

    def right_access(self, ex):
        if type(ex) == BaseEx.Executor and self.restricted:
            raise error.DeniedAccessError(self.name)

    def set_code(self, code):
        self.code = code  # liste deja parsee

        r = "#\n"
        r += self.name + ' : ' + default_types.stringify(self.types[0]) + ' ⟶ ' + default_types.stringify(
            self.types[1]) + '.\n'
        r += '⟨' + ';'.join(self.arg_names) + '⟩.\n'
        l = []
        for elt in self.code:
            l.append(' '.join(elt) + '.')
            if l[-1].replace(' ', '') == '.':
                l.pop()
        r += '\n'.join(l)
        r += '\n#'
        if self.__doc__ == '':
            self.__doc__ = r
        else:
            self.__doc__ = self.name + ' : ' + default_types.stringify(self.types[0]) + ' ⟶ ' + default_types.stringify(
                self.types[1]) + '.\n' + self.__doc__
        self.__repr = r

    def set_global_obj(self, var, func, alias, dic, obj):
        var = copy.deepcopy(var)
        func = copy.deepcopy(func)
        alias = copy.deepcopy(alias)
        dic = copy.deepcopy(dic)
        obj = copy.deepcopy(obj)

        self.VAR, self.FUNC, self.ALIAS, self.DICT, self.OBJ = {}, {}, {}, {}, {}
        for k in [(var, self.VAR), (func, self.FUNC), (alias, self.ALIAS), (dic, self.DICT), (obj, self.OBJ)]:
            for elt in k[0]:
                if elt in self.arg_names:
                    k[1]["GLOBAL·" + elt] = k[0][elt]
                else:
                    k[1][elt] = k[0][elt]

    def __call__(self, echo, *vals, father=''):
        ARGS= super().__call__(*vals)

        ex = BaseEx.FuncExecutor(self.code, echo, self.VAR, self.FUNC, self.DICT, self.ALIAS, self.OBJ, self.name,
                                 self.is_meth, father)  # il faut le coder !
        ex.set_args(ARGS)
        res = ex.execute()
        self.VAR=ex.VARIABLES
        self.DICT=ex.DICTIONARY
        self.ALIAS=ex.ALIAS
        if self.types[1] == default_types.Parts(default_types.EmptySet):
            if type(res) == default_types.EmptySet:
                return res
            raise
        return default_functions.convert(res, self.types[1])

    def __str__(self) -> str:
        return self.__doc__

    def __repr__(self) -> str:
        return self.__repr


class FixedVariable:
    __name__ = 'Variable'

    def __init__(self, typ, nom, value):
        self.type = typ
        self.name = nom
        self.value = value
        self.glob = False
        self.__doc__ = self.type.__doc__

    def get(self):
        if self.value is None:
            raise error.TooEarlyToAccessError(self.name)
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return default_functions.stringify(self.type) + ';' + self.value.__repr__()


class Applications(Callable):
    def __init__(self, nom: str, t_entree, t_sortie, obj=None) -> None:
        if obj is None:obj={}
        super().__init__(nom,default_types.type_from_str(t_entree, obj), default_types.type_from_str(t_sortie, obj))
        self.expr=[]

    def set_expr(self, expr):
        if type(expr) != list: expr = [expr]
        self.expr = expr
        self.__doc__ = self.__str__()

    def __call__(self, *vals):
        ARGS=super().__call__(*vals)

        FUNC = {self.name: self}
        if self.expr[0] == "➣":
            l = split(self.expr)
            for case in l:
                cond, expr = cut(case)
                r = evaluations.create_evaluating_list(cond)
                evaluations.typize(r)
                r = evaluations.evaluate(r, ARGS, {}, FUNC, {}, {}, {})
                if type(r) != default_types.B:
                    raise error.TypeError_(cond,'',default_types.stringify(type(r)),default_types.stringify(default_types.B),0)
                if r.v:
                    l = evaluations.create_evaluating_list(expr)
                    evaluations.typize(l)
                    r = evaluations.evaluate(l, ARGS, {}, FUNC, {}, {},
                                             {})  # liste parsee, transformee en evaluating list, typee
                    return default_functions.convert(r, self.types[1])
            raise
        else:
            l = evaluations.create_evaluating_list(self.expr)
            evaluations.typize(l)
            r = evaluations.evaluate(l, ARGS, {}, FUNC, {}, {},
                                     {})  # liste parsee, transformee en evaluating list, typee
        return default_functions.convert(r, self.types[1])

    def __str__(self) -> str:
        r = self.name + ' : ' + default_types.stringify(self.types[0]) + ' ⟶  ' + default_types.stringify(self.types[1])
        try:
            r += '\n' + ' ' * len(self.name + ' : ') + ';'.join(self.arg_names) + ' ⟼  ' + ' '.join(self.expr)
        except Exception as err:
            pass
        return r

    def __repr__(self) -> str:
        r = self.name + ' : ' + default_types.stringify(self.types[0]) + ' ⟶  ' + default_types.stringify(self.types[1])
        try:
            r += '\n' + ';'.join(self.arg_names) + ' ⟼  ' + ' '.join(self.expr)
        except:
            pass
        return r


def split(ch):
    l = [[]]
    for car in ch:
        if car == '➣' and l[-1] != []:
            l.append([])
        l[-1].append(car)
    return l


def cut(ch):
    cond = []
    expr = []
    c = True
    for car in ch:
        if car == ':':
            c = False
        if car == '➣' or car == ':':
            continue
        if c:
            cond.append(car)
        else:
            expr.append(car)
    return cond, expr


def valid_name(ch: str):
    if ch in default_functions.DEFAULT_FUNCTIONS:
        raise error.InvalidName(ch)
    if ch == '' or ' ' in ch:
        raise error.InvalidName(ch)
    if ch[0] not in 'abcdefghijklmnopqrstuvwxyz':
        raise error.InvalidName(ch)
    if any(car not in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for car in ch):
        raise error.InvalidName(ch)

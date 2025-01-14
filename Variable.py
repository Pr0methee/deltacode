from default_types import stringify
import error,default_functions,POO

class Alias:
    __name__='Alias'
    def __init__(self,nom,ptr):
        self.nom=nom
        self.ptr=ptr
        self.glob=True

    def set_glob(self,glob):
        self.glob=glob

    

class Variable:
    __name__='Variable'
    def __init__(self,typ,nom):
        self.type=typ
        self.name=nom
        self.value = None
        self.glob=True
        self.__doc__=self.type.__doc__
        valid_name_var(nom)

    def set_glob(self,glob):
        self.glob=glob

    def get(self):
        if self.value is None:
            raise error.TooEarlyToAccessError(self.name)
        return self.value
    
    def set(self,v):
        if type(self.type) == POO.Object:
            assert type(v)==POO.Instance and v.type==self.type
        else:
            v = default_functions.convert(v,self.type)
        self.value = v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return stringify(self.type)+';'+self.value.__repr__()

class Constant:
    __name__ = 'Constante'
    def __init__(self,typ,nom):
        self.type=typ
        self.name=nom
        self.value = None
        self.__doc__=self.type.__doc__
        self.glob=True
        valid_name_const(nom)

    def set_glob(self,glob):
        self.glob=glob

    def get(self):
        if self.value is None:
            raise error.TooEarlyToAccessError(self.name)
        return self.value
    
    def set(self,v):
        if self.value is not None:
            raise error.RedefiningError
        if type(self.type) == POO.Object:
            assert type(v)==POO.Instance and v.type==self.type
        else:
            v = default_functions.convert(v,self.type)
        self.value = v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return stringify(self.type)+';'+self.value.__repr__()

class Attribute(Variable):
    __name__='Attribute'
    def __init__(self, typ, nom):
        self.type=typ
        self.name=nom
        self.value = None
        self.__doc__=self.type.__doc__
        valid_name_attr(nom)
        self.glob=False

    def set_glob(self,*args):
        self.glob=False

def create_var(typ,nom,meth=False):
    if meth:
        if not nom.startswith('me·'):raise error.InvalidName(nom)
        return Attribute(typ,nom)
    if nom=='':
        raise error.InvalidName(nom)
    if nom[0] in 'abcdefghijklmnopqrstuvwxyz':
        return Variable(typ,nom)
    elif nom[0] in 'abcdefghijklmnopqrstuvwxyz'.upper():
        return Constant(typ,nom)
    else:
        raise error.InvalidName(nom)

def valid_name_var(ch:str):
    if ch =='' or ' ' in ch:
        raise error.InvalidName(ch)
    if ch[0] not in 'abcdefghijklmnopqrstuvwxyz':
        raise error.InvalidName(ch)
    if any(car not in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch):
        raise error.InvalidName(ch)

def valid_name_attr(ch:str):
    if not ch.startswith('me·'):
        raise error.InvalidName(ch)
    valid_name_var(ch[3:])
    
def valid_name_const(ch:str):
    if ch =='' or ' ' in ch:
        raise error.InvalidName(ch)
    if any(car not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_' for car in ch):
        raise error.InvalidName(ch)
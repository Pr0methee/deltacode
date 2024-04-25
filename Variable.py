from default_types import stringify
import error,default_functions

class Variable:
    def __init__(self,typ,nom):
        self.type=typ
        self.name=nom
        self.value = None
        self.__doc__=self.type.__doc__
        valid_name(nom)
    
    def get(self):
        if self.value is None:
            raise error.TooEarlyToAccessError(self.name)
        return self.value
    
    def set(self,v):
        v = default_functions.convert(v,self.type)
        self.value = v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return stringify(self.type)+';'+self.value.__repr__()

def valid_name(ch:str):
    if ch =='' or ' ' in ch:
        raise error.InvalidName(ch)
    if ch[0] not in 'abcdefghijklmnopqrstuvwxyz':
        if any(car  not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for car in ch):
            raise error.InvalidName(ch)
    if any(car not in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch):
        raise error.InvalidName(ch)

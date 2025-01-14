import default_functions,error
import default_types
stringify = default_types.stringify
Types= default_types.Types

class Dictionnary(Types):
    def __init__(self,t1,t2,name,meth=False):
        super().__init__()
        self._in=t1
        self.out = t2
        self.d = {}
        self.__doc__ = f"""Dictionnary :{name}\n{stringify(t1)} ⇴ {stringify(t2)}\nKeys : Values \n"""
        valid_name(name,meth)
        self.name=name
        self.glob=True

    def set_glob(self,s:bool):
        self.glob=s

    def __getitem__(self,k):
        k = default_functions.convert(k,self._in)
        if k in self.d:
            return self.d[k]
        raise error.InvalidKeyError(k)

    def __setitem__(self,k,v):
        k = default_functions.convert(k,self._in)
        v = default_functions.convert(v,self.out)
        self.d[k]=v
        self.__doc__ += f"{k.__repr__()} : {v.__repr__()}\n"
    
    def Keys(self):
        r=default_types.SET(self._in)
        for k in self.d.keys():
            r.add(k)
        return r
    
    def Values(self):
        r=default_types.SET(self.out)
        for v in self.d.values():
            r.add(v)
        return r

    def __str__(self) -> str:
        return self.__doc__
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def representation(self):
        return stringify(self._in),stringify(self.out),{k.__repr__():v.__repr__() for k,v in self.d.items()}
    
def valid_name(ch:str,meth:bool):
    if meth:
        if ch.startswith('me·'):
            valid_name(ch[3:],False)
            return

    if ch in default_functions.DEFAULT_FUNCTIONS:
        raise error.InvalidName(ch)
    if ch =='' or ' ' in ch:
        raise error.InvalidName(ch)
    if ch[0] not in 'abcdefghijklmnopqrstuvwxyz':
        raise error.InvalidName(ch)
    if any(car not in '1234567890AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn_\'₀₁₂₃₄₅₆₇₈₉' for  car in ch):
        raise error.InvalidName(ch)

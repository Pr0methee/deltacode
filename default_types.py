import math

class N:
    def __init__(self,v):
        assert type(v)==int and v>=0
        self.value=v

    def __int__(self):
        return self.value
    
    def recognize(ch):
        return all([car in '0123456789' for car in ch]) and ch != ''
    
    @classmethod
    def from_str(cls,ch):
        assert N.recognize(ch)
        return cls(int(ch))
    
    def __str__(self) -> str:
        return 'N'+str(self.value)

    def __add__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) == N:
            return N(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) == N:
            return N(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __sub__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) == N and obj.value<= self.value:
            return N(self.value-obj.value)
        elif type(obj) == N:
            return Z(self.value)-obj
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z) and self.value%obj.value==0:
            return type(obj)(int(self.value/obj.value))
        elif type(obj) in (N,Z):
            return R(self.value)/obj
        else:
            return type(obj)(self.value)/obj
    
    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return False
        if type(__value)==C:
            return self.value==__value.re and __value.im==0
        else:
            return self.value==__value.value
    
    def __ne__(self, __value: object) -> bool:
        return not self==__value
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value > obj.value
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value >= obj.value
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value < obj.value
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value <= obj.value
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__() -> str:
        return 'N'





class Z:
    def __init__(self,v):
        assert type(v)==int 
        self.value=v

    def __int__(self):
        return self.value
    
    def recognize(ch):
        return all([car in '-0123456789' for car in ch]) and ch!=''
    
    @classmethod
    def from_str(cls,ch):
        assert Z.recognize(ch)
        return cls(int(ch))
    
    def __str__(self) -> str:
        return 'Z'+str(self.value)

    def __add__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z):
            return Z(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z):
            return Z(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __sub__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z):
            return Z(self.value-obj.value)
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z) and self.value%obj.value==0:
            return Z(int(self.value/obj.value))
        elif type(obj) in (N,Z):
            return R(self.value)/obj
        else:
            return type(obj)(self.value)/obj

    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return False
        if type(__value)==C:
            return self.value==__value.re and __value.im==0
        else:
            return self.value==__value.value
    
    def __ne__(self, __value: object) -> bool:
        return not self==__value
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value > obj.value
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value >= obj.value
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value < obj.value
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value <= obj.value
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__() -> str:
        return 'Z'


class R:
    def __init__(self,v):
        assert type(v)==float  or type(v)==int
        self.value=v

    def __float__(self):
        return self.value
    
    def recognize(ch):
        return all([car in '.-0123456789' for car in ch]) and ch !=''
    
    @classmethod
    def from_str(cls,ch):
        assert R.recognize(ch)
        return cls(float(ch))
    
    def __str__(self) -> str:
        return 'R'+str(self.value)

    def __add__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return R(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return R(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __sub__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return R(self.value-obj.value)
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return R(self.value/obj.value)
        else:
            return type(obj)(self.value)/obj
        
    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return False
        if type(__value)==C:
            return self.value==__value.re and __value.im==0
        else:
            return self.value==__value.value
    
    def __ne__(self, __value: object) -> bool:
        return not self==__value
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value > obj.value
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value >= obj.value
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value < obj.value
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise
        return self.value <= obj.value
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__() -> str:
        return 'R'


class C:
    def __init__(self,a,b=0):
        assert type(a) in (float,int) and type(b) in (float,int)
        self.re=a
        self.im=b

    def __complex__(self):
        return self.re+1j*self.im
    
    def recognize(ch):
        return all([car in '.-0123456789+i' for car in ch])and ch !=''
    
    @classmethod
    def from_str(cls,ch):
        assert C.recognize(ch)
        l=ch.split('+')
        return cls(float(l[0]),float(l[1]))
    
    def __str__(self) -> str:
        return 'C'+str(self.re)+'+'+str(self.im)+'i' if self.im>=0 else 'C'+str(self.re)+str(self.im)+'i' 

    def __add__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) == C:
            return C(self.re+obj.re,self.im+obj.im)
        return C(self.re+obj.value,self.im)
    
    def __mul__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return C(obj.value*self.re,obj.value*self.im)
        else:
            return C(self.re*obj.re-self.im*obj.im,self.im*obj.re+self.re*obj.im)
    
    def __sub__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return C(self.re-obj.value)
        else:
            return C(self.re-obj.re,self.im-obj.im)

    def __truediv__(self,obj):
        assert type(obj)in NUMERAL
        if type(obj) in (N,Z,R):
            return C(self.re/obj.value,self.im/obj.value)
        else:
            return self*obj.conj()/abs(obj)
        
    def conj(self):
        return C(self.re,-self.im)
    
    def __abs__(self):
        return R(math.sqrt(self.re**2+self.im**2))
    
    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return False
        if type(__value)==C:
            return self.value==__value.re and __value.im==0
        else:
            return self.value==__value.value
    
    def __ne__(self, __value: object) -> bool:
        return not self==__value
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__() -> str:
        return 'C'


NUMERAL = (N,Z,R,C)

class S:
    def __init__(self,v):
        self.value = v
    
    def __str__(self) -> str:
        return self.value
    
    def recognize(ch):
        if len(ch)<2:
            return False
        if not (ch[0]==ch[-1]=='"'):
            return False
        for car in ch[1:-1]:
            if car=='"':return False
        return True
    
    @classmethod
    def from_str(cls,ch):
        assert S.recognize(ch)
        return S(ch[1:-1])
    
    def __len__(self):
        return len(self.value)
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__() -> str:
        return 'C'

class B:
    def __init__(self,v):
        assert v in (True,False)
        self.v=v
    
    def __str__(self) -> str:
        return {True:'⊤',False:'⊥'}[self.v]
    
    @classmethod
    def from_str(cls,ch):
        if ch == '⊤':return cls(True)
        elif ch == '⊥':return cls(False)
        raise

    def recognize(ch):
        return ch in ('⊤','⊥')


    
class SET:
    def __init__(self,t):
        assert t in (N,Z,R,C,S,B)
        self.__l=set()
        self.type=t
    
    def add(self,v):
        #print(self.type.recogn
        if type(v) != self.type and not self.type.recognize(v):
            raise
        self.__l.add(self.type.from_str(v))
    
    def __str__(self) -> str:
        if len(self.__l)==0:
            return '∅'
        l_=[str(x) for x in self.__l]
        return '{ '+' ; '.join(l_)+' }'

    def inclusion(self):
        return 'SET('+self.type.__repr__()+')'
    
    def __len__(self):
        return len(self.__l)
    
    def __hash__(self) -> int:
        return hash(self.__str__())

class CrossSet:
    def __init__(self,*t):
        assert all(typ in (N,Z,R,C,S,B) for typ in t)
        self.schema = t

    @classmethod
    def from_str(cls,ch):
        assert CrossSet.recognize(ch)
        t=[]
        ch =ch.replace(' ','')
        for elt in ch.split('×'):
            t.append({"ϩ":S,"ℕ":N,"ℤ":Z,"ℝ":R,"ℂ":C}[elt])
        return cls(*t)

    def recognize(ch):
        ch =ch.replace(' ','')
        for elt in ch.split('×'):
            if elt not in ("ϩ","ℕ","ℤ","ℝ","ℂ"):
                return False
        return True

from __future__ import annotations
import math,copy
import default_functions,error

class Types:
    def __init__(self):pass
    def call(self,f,*args):
        if f not in dir(self):
            raise error.AttributeError(f,stringify(type(self)))
        r = 'self.'+f
        r=eval(r)
        return r(*args)


class N(Types):
    def __init__(self,v):
        super().__init__()
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
        return str(self.value)

    def __add__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("+",stringify(N),stringify(type(obj)))
        if type(obj) == N:
            return N(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("×",stringify(N),stringify(type(obj)))
        if type(obj) == N:
            return N(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __neg__(self):
        return Z(-self.value)
    
    def __sub__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("-",stringify(N),stringify(type(obj)))
        if type(obj) == N and obj.value<= self.value:
            return N(self.value-obj.value)
        elif type(obj) == N:
            return Z(self.value)-obj
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("÷",stringify(N),stringify(type(obj)))
        if type(obj) in (N,Z) and self.value%obj.value==0:
            return type(obj)(int(self.value/obj.value))
        elif type(obj) in (N,Z):
            return R(self.value)/obj
        else:
            return type(obj)(self.value)/obj
    
    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return B(False)
        if type(__value)==C:
            return B(self.value==__value.re and __value.im==0)
        else:
            return B(self.value==__value.value)
    
    def __ne__(self, __value: object) -> bool:
        return B(not (self==__value))
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation(">",stringify(N),stringify(type(obj)))
        return B(self.value > obj.value)
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩾",stringify(N),stringify(type(obj)))
        return B(self.value >= obj.value)
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("<",stringify(N),stringify(type(obj)))
        return B(self.value < obj.value)
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩽",stringify(N),stringify(type(obj)))
        return B(self.value <= obj.value)
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def div(self,obj):
        if type(obj) not in (N,Z):
            raise error.UnsupportedOperation('|',stringify(N),stringify(type(obj)))
        return B(obj.value % self.value == 0)

    def __pow__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation('^',stringify(N),stringify(type(obj)))
        if type(obj) == N : 
            return N(self.value ** obj.value)
        elif type(obj)!=C:
            return R(self.value ** obj.value)
        elif type(obj)==C:
            return self**obj.re * C((self.value ** (obj.im*1j)).real,(self.value ** (obj.im*1j)).imag)

class Z(Types):
    def __init__(self,v):
        super().__init__()
        assert type(v)==int 
        self.value=v

    def __int__(self):
        return self.value
    
    def TurnIntoN(self):
        if self.value >=0:
            return N(self.value)
        else:
            return N(-self.value)
    
    def recognize(ch):
        return all([car in '-0123456789' for car in ch]) and ch.replace('-','')!=''
    
    @classmethod
    def from_str(cls,ch):
        assert Z.recognize(ch)
        return cls(int(ch))
    
    def __str__(self) -> str:
        return str(self.value)

    def __add__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("+",stringify(Z),stringify(type(obj)))
        if type(obj) in (N,Z):
            return Z(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("×",stringify(Z),stringify(type(obj)))
        if type(obj) in (N,Z):
            return Z(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __neg__(self):
        return Z(-self.value)
    
    def __sub__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("-",stringify(Z),stringify(type(obj)))
        if type(obj) in (N,Z):
            return Z(self.value-obj.value)
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("÷",stringify(Z),stringify(type(obj)))
        if type(obj) in (N,Z) and self.value%obj.value==0:
            return Z(int(self.value/obj.value))
        elif type(obj) in (N,Z):
            return R(self.value)/obj
        else:
            return type(obj)(self.value)/obj

    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return B(False)
        if type(__value)==C:
            return B(self.value==__value.re and __value.im==0)
        else:
            return B(self.value==__value.value)
    
    def __ne__(self, __value: object) -> bool:
        return B(not self==__value)
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation(">",stringify(Z),stringify(type(obj)))
        return B(self.value > obj.value)
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩾",stringify(Z),stringify(type(obj)))
        return B(self.value >= obj.value)
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("<",stringify(Z),stringify(type(obj)))
        return B(self.value < obj.value)
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩽",stringify(Z),stringify(type(obj)))
        return B(self.value <= obj.value)
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def div(self,obj):
        if type(obj) not in (N,Z):
            raise error.UnsupportedOperation('|',stringify(Z),stringify(type(obj)))
        return B(obj.value % self.value == 0)
    
    def __pow__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation('^',stringify(N),stringify(type(obj)))
        if type(obj) == N : 
            return N(self.value ** obj.value)
        elif type(obj)!=C:
            return R(self.value ** obj.value)
        elif type(obj)==C:
            return self**obj.re * C((self.value ** (obj.im*1j)).real,(self.value ** (obj.im*1j)).imag)

class R(Types):
    def __init__(self,v):
        super().__init__()
        assert type(v)==float  or type(v)==int
        self.value=v

    def TurnIntoZ(self):
        if self.value >=0:
            return Z(int(self.value))
        else:
            return Z(int(self.value)) - Z(1)

    def TurnIntoN(self):
        return self.TurnIntoZ().TurnIntoN()


    def __float__(self):
        return self.value
    
    def recognize(ch):
        return all([car in ',-0123456789' for car in ch]) and ch.replace('-','').replace(',','') !=''
    
    @classmethod
    def from_str(cls,ch):
        assert R.recognize(ch)
        return cls(float(ch.replace(',','.')))
    
    def __str__(self) -> str:
        return str(self.value).replace('.',',')

    def __add__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("+",stringify(R),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return R(self.value+obj.value)
        else:
            return type(obj)(self.value)+obj
    
    def __mul__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("×",stringify(R),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return R(self.value*obj.value)
        else:
            return type(obj)(self.value)*obj
    
    def __neg__(self):
        return R(-self.value)
    
    def __pow__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("^",stringify(R),stringify(type(obj)))
        if type(obj) != C:
            return R(self.value**obj.value) 
        elif type(obj)==C:
            return self**obj.re * C((self.value ** (obj.im*1j)).real,(self.value ** (obj.im*1j)).imag)

    def __sub__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("-",stringify(R),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return R(self.value-obj.value)
        else:
            return type(obj)(self.value)-obj

    def __truediv__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("÷",stringify(R),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return R(self.value/obj.value)
        else:
            return type(obj)(self.value)/obj
        
    def __eq__(self, __value: object) -> bool:
        if type(__value)not in NUMERAL:
            return B(False)
        if type(__value)==C:
            return B(bool(self.value==__value.re and __value.im==0))
        else:
            return B(self.value==__value.value)
    
    def __ne__(self, __value: object) -> bool:
        return B(not self==__value)
    
    def __gt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation(">",stringify(R),stringify(type(obj)))
        return B(self.value > obj.value)
    
    def __ge__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩾",stringify(R),stringify(type(obj)))
        return B(self.value >= obj.value)
    
    def __lt__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("<",stringify(R),stringify(type(obj)))
        return B(self.value < obj.value)
    
    def __le__(self,obj):
        if type(obj)==C or type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("⩽",stringify(N),stringify(type(obj)))
        return B(self.value <= obj.value)
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__(self) -> str:
        return self.__str__()

class C(Types):#verifier si from_str(str) -> x
    def __init__(self,a,b=0):
        super().__init__()
        assert (type(a) in (float,int) and type(b) in (float,int) )or (type(a)in NUMERAL and type(b) in NUMERAL and C not in (type(a),type(b)))
        if type(a) in NUMERAL:
            self.re=a
        else:
            self.re=R(a)
        if type(b) in NUMERAL:
            self.im=b
        else:
            self.im=R(b)
    
    def call(self,f,*args):
        if f=='R' or f == 'C':raise error.AttributeError(f,stringify(C))
        return super().call(f,*args)
    
    def TurnIntoR(self):
        return self.re

    def TurnIntoZ(self):
        return self.TurnIntoR().TurnIntoZ()

    def TurnIntoN(self):
        return self.TurnIntoZ().TurnIntoN()

    def ℜ(self):
        return self.re
    
    def ℑ(self):
        return self.im

    def __complex__(self):
        return self.re+1j*self.im
    
    def recognize(ch):
        return all([car in '.-0123456789+ι' for car in ch])and ch !='' and ch.replace('.','').replace('-','').replace('+','') != ''
    
    @classmethod
    def from_str(cls,ch):
        assert C.recognize(ch)
        l=['']
        for car in ch:
            if car in ('-','+'):
                l.append(car)
                l.append('')
            else:
                l[-1]+=car
        if l[0] in ('-','+'):
            s=l[0]
            del l[0]
            if s =='-':
                l[0] = s +l[0]
        
        if len(l) == 1:
            if 'ι' in l[0]:
                l = ['0','+']+l
            else:
                l = l + ['+','0ι']

        s=l[1]
        del l[1]
        if s == '-':
            l[1]=s + l[1]
        
        l[1] = l[1][:-1]
        if l[1]=='':
            l[1]='1'
        
        return cls(float(l[0]),float(l[1]))
        
    def __str__(self) -> str:
        return str(self.re.value)+'+'+str(self.im.value)+'ι' if self.im>=R(0) else str(self.re.value)+str(self.im.value)+'ι' 

    def __add__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("+",stringify(C),stringify(type(obj)))
        if type(obj) == C:
            return C(self.re+obj.re,self.im+obj.im)
        return C(self.re+obj.value,self.im)
    
    def __mul__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("×",stringify(C),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return C(obj.value*self.re,obj.value*self.im)
        else:
            return C(self.re*obj.re-self.im*obj.im,self.im*obj.re+self.re*obj.im)
    
    def __neg__(self):
        return C(-self.re,-self.im)
    
    def __sub__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("-",stringify(C),stringify(type(obj)))
        if type(obj) in (N,Z,R):
            return C(self.re-obj.value)
        else:
            return C(self.re-obj.re,self.im-obj.im)

    def __truediv__(self,obj):
        if type(obj) not in NUMERAL:
            raise error.UnsupportedOperation("÷",stringify(C),stringify(type(obj)))
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
            return B(False)
        if type(__value)!=C:
            return self.re==__value.value and self.im==0
        else:
            return self.re == __value.re and self.im == __value.im
    
    def __ne__(self, __value: object) -> bool:
        return B(not self==__value)
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __pow__(self,n):
        if type(n) not in NUMERAL:
            raise error.UnsupportedOperation('^',stringify(C),stringify(type(n)))
        if type(n) == C:
            r = complex(self) ** complex(n)
            return C(r.real,r.imag)
        else:
            r = complex(self) ** n.value
            return C(r.real,r.imag)

    def __gt__(self,obj):
        raise error.UnsupportedOperation(">",stringify(C))
    
    def __ge__(self,obj):
        raise error.UnsupportedOperation("⩾",stringify(C))
    
    def __lt__(self,obj):
        raise error.UnsupportedOperation("<",stringify(C))
    
    def __le__(self,obj):
        raise error.UnsupportedOperation("⩽",stringify(C))

NUMERAL = (N,Z,R,C)

class S(Types):
    def __init__(self,v:str):
        super().__init__()
        self.value = v
    
    def __str__(self) -> str:
        return self.value

    def Length(self):
        return N(len(self.value))
    
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
    
    def __repr__(self) -> str:
        return '"'+self.__str__()+'"'

    def __add__(self,obj):
        if type(obj)!=S:
            raise error.UnsupportedOperation('+',stringify(S),stringify(type(obj)))
        return S(self.value+obj.value)
    
    def __mul__(self,obj):
        if type(obj)!=N:
            raise error.UnsupportedOperation('×',stringify(S),stringify(type(obj)))
        return S(self.value*obj.value)
    
    def __eq__(self, __value: object) -> bool:
        if type(__value) != S:return B(False)
        return B(self.value == __value.value)
    
    def __ne__(self, __value: object) -> bool:
        return B( not (self==__value))
    
    def __iter__(self):
        self.i=0
        return self
    
    def __next__(self):
        self.i+=1
        if self.i <= len(self.value):
            return S(self.value[self.i-1])
        raise StopIteration
    
    def get(self,v):
        if type(v)!=ZIntervalle:
            v = default_functions.convert(v,Z)
            if v < Z(0):
                return self.Reverse().get(-v)
            if v == Z(0) or v > self.Length():
                raise error.IndexError(v)
            return S(self.value[v.value-1])
        else:
            r=S("")
            for i in v:
                r += self.get(i)
            return r 
    
    def Reverse(self):
        v = ""
        for i in range(len(self.value)-1,-1,-1):
            v += self.value[i]
        return S(v)
    
    def Capitalize(self):
        return S(self.value.capitalize())
    
    def UpperCase(self):
        return S(self.value.upper())
    
    def LowerCase(self):
        return S(self.value.lower())
    
    def Split(self,car:S):
        lch = self.value.split(car.value)
        t = CrossSet(*[S for _ in range(len(lch))])
        r = Tuple([S(elt) for elt in lch],t)
        return r

    def Count(self,car:S):
        return N(self.value.count(car.value))

class B(Types):
    def __init__(self,v):
        super().__init__()
        assert v in (True,False)
        self.v=v
    
    def __str__(self) -> str:
        return {True:'⊤',False:'⊥'}[self.v]
    
    def __bool__(self):
        return self.v

    def TurnIntoN(self):
        return {True:N(1),False:N(0)}[self.v]
    
    @classmethod
    def from_str(cls,ch):
        if ch == '⊤':return cls(True)
        elif ch == '⊥':return cls(False)
        raise

    def recognize(ch):
        return ch in ('⊤','⊥')
    
    def __not__(self):
        return not self.v
    
    def impl(self,obj):
        assert type(obj)==B
        return B(not (self.v and not obj.v))

    def equiv(self,obj):
        assert type(obj)==B
        return self.impl(obj) and obj.impl(self)

    def xor(self,obj):
       assert type(obj)==B
       return B(self.v!=obj.v) 

    def __repr__(self) -> str:
        return self.__str__()
    
class SET(Types):
    def __init__(self,t):
        super().__init__()
        assert t in (N,Z,R,C,S,B) or type(t)==CrossSet or type(t) == Parts
        self.__l=set()
        self.type=t
    
    def add(self,v):
        if type(self.type) ==CrossSet:
            assert type(v)==Tuple and v.type==self.type
        elif (type(v) != SET and type(v) != self.type and (not include(type(v),self.type))):
            raise
        elif type(v)==SET and type(self.type) !=Parts:
            raise
        elif type(v)==SET and (not include(Parts(v.type),self.type)):
            raise
        if type(v)==str:
            self.__l.add(self.type.from_str(v))
        else:
            self.__l.add(default_functions.convert(v,self.type))
    
    def listify(ch):
        assert ch[0] == '{' and ch[-1]=='}'
        l=['']
        t,s = False,False
        for car in ch[1:-1]:
            if t or s:
                l[-1]+=car
            elif car ==';':
                l.append('')
            else:
                l[-1]+=car

            if car == '"':
                s = not s
            elif car == '(':
                t =True
            elif car ==')':
                t =False
        return l

    def recognize(ch,typ):
        if ch =='':return False
        if ch == '∅':return True
        if ch[0] != '{' or ch[-1]!='}':return False

        l = SET.listify(ch)
        for elt in l:
            if (type(typ)==Parts and not SET.recognize(elt,typ.typ))or(type(typ)==CrossSet and not Tuple.recognize(elt,typ)) or (type(typ)!=CrossSet and not typ.recognize(elt)):return False
        
        return True

    def union(self,__o):
        if type(__o) != SET:raise
        if self.type == __o.type or include(__o.type,self.type):
            s=SET(self.type)
            for elt in self:
                s.add(elt)
            for elt in __o:
                s.add(elt)
        elif include(self.type,__o.type):
            s=SET(__o.type)
            for elt in self:
                s.add(elt)
            for elt in __o:
                s.add(elt)
        else:
            raise
        return s
    
    def deep_get(self):
        return self.__l

    def inter (self,__o):
        if type(__o) != SET:raise
        if self.type == __o.type or include(__o.type,self.type):
            s=SET(self.type)
            for elt in self:
                for thing in __o:
                    if (thing == elt):
                        s.add(elt)
                        break
        elif include(self.type,__o.type):
            s=SET(__o.type)
            for elt in self:
                for thing in __o:
                    if (thing == elt):
                        s.add(elt)
                        break
        else:
            raise
        return s

    def setminus(self,__other):
        if type(__other) == EmptySet:
            return copy.copy(self)
        assert type(__other)==SET
        r = SET(self.type)
        for elt in self:
            if elt in __other.deep_get():
                continue
            r.add(elt)
        return r
    
    def __contains__(self,elt):
        for k in self:
            if k==elt:
                return True
        return False
    
    def __str__(self) -> str:
        if len(self.__l)==0:
            return '∅'
        l_=[str(x) for x in self.__l]
        return '{ '+' ; '.join(l_)+' }'

    def __repr__(self) -> str:
        l_=[x.__repr__() for x in self.__l]
        return '{'+';'.join(l_)+'}'

    def inclusion(self):
        return 'SET('+self.type.__repr__()+')'
    
    def __len__(self):
        return len(self.__l)
    
    def __hash__(self) -> int:
        return hash(self.__str__())
    
    def __eq__(self, __value: object) -> bool:
        if type(__value)==EmptySet:
            return B(self.__l==set())
        if type(__value) != SET:return B(False)
        return B(self.deep_get()==__value.deep_get())
    
    def __ne__(self, __value: object) -> bool:
        return B(not (self==__value))

    
    
    def __iter__(self):
        return iter(self.__l)

class CrossSet(Types):
    def __init__(self,*t):
        super().__init__()
        assert all(typ in (N,Z,R,C,S,B,EmptySet) or type(typ)==Parts  for typ in t)
        self.schema = t

    @classmethod
    def from_str(cls,ch):
        assert CrossSet.recognize_type(ch)
        t=[]
        ch =ch.replace(' ','')
        for elt in split_tup(ch):
            t.append(type_from_str(elt))
        return cls(*t)
    
    def __getitem__(self,i):
        return self.schema[i]

    def recognize_type(ch):
        if '×' not in ch:return False
        ch =ch.replace(' ','')
        for elt in split_tup(ch):
            if not recognize_type(elt):
                return False
        return True

    def __str__(self) -> str:
        return ' × '.join([stringify(elt) for elt in self.schema])
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self,obj):
        if type(obj)!=CrossSet:return False
        return self.schema == obj.schema
    
    def __hash__(self) -> int:
        return hash(str(self))

class Tuple(Types):
    def __init__(self,obj,typ:CrossSet):
        super().__init__()
        self.type=typ
        self.v = tuple(obj)
        assert  len(obj) == len(typ.schema)
        for i in range(len(obj)):
            if type(typ.schema[i])==Parts:
                assert type(obj[i]) == SET and obj[i].type == typ.schema[i].typ
            else :assert type(obj[i])== typ.schema[i] 
    
    @classmethod
    def from_str(cls,ch,typ):
        assert Tuple.recognize(ch,typ)
        l=ch[1:-1].split(';')
        l_=[]
        for i in range(len(l)):
            l_.append(typ.schema[i].from_str(l[i]))
        l_=tuple(l_)
        return cls(l_,typ)

    def recognize(ch:str,typ:CrossSet):
        if ch[0] != '(' or ch[-1] != ')':return False
        l=ch[1:-1].split(';')
        if len(l) != len(typ.schema):return False

        for i in range(len(l)):
            if not typ.schema[i].recognize(l[i]):return False
        return True

    def __repr__(self) -> str:
        return '('+';'.join([x.__repr__() for x in self.v])+')'
    
    def __str__(self) -> str:
        return str(self.v).replace(',',';')

    def __getitem__(self,i):
        return self.v[i]
    
    def get(self,v):
        v = default_functions.convert(v,N)
        if v == 0 or v > len(self.v):
            raise error.IndexError(v)
        return self.v[v.value]

    def __iter__(self):
        return iter(self.v)
    
    def __next__(self):
        return next(self.v)
    
    def __eq__(self, __value: object) -> bool:
        if type(__value) != Tuple:return B(False)
        return B(self.v==__value.v)
    
    def __ne__(self, __value: object) -> bool:
        if type(__value) != Tuple:return B(True)
        return B(self.v!=__value.v)

class Parts(Types):
    def __init__(self,t):
        super().__init__()
        assert t in (N,Z,R,C,B,S) or type(t)==CrossSet  or type(t)==Parts or t == EmptySet
        self.typ = t
    
    def __str__(self) -> str:
        return chr(8472) + '(' + stringify(self.typ) + ')'
    
    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __value: object) -> bool:
        if type(__value) != Parts:return False
        return self.typ == __value.typ
    
    def recognize(v:str):
        if len(v) <=3:return False
        return v[0]==chr(8472) and v[1]=='(' and v[-1]==')' and recognize_type(v[2:-1])
    
    @classmethod
    def from_str(cls,ch:str):
        assert Parts.recognize(ch)
        return cls(type_from_str(ch[2:-1]))
    #bien coder Parts (from_str etc. ) puis faire dans executor
    def __hash__(self) -> int:
        return hash(str(self))

class RIntervalle:
    def __init__(self,binf:float|int,bsup:float|int):
        self.binf = binf
        self.bsup = bsup
    
    def __in(self,v):
        return self.binf <= v <= self.bsup
    
class ZIntervalle:
    def __init__(self,binf:Z,bsup:Z):
        self.binf = binf
        #if self.binf >= N(0)
        self.bsup = bsup
    
    def __in(self,v):
        return self.binf <= v <= self.bsup
    
    def recognize(ch:str):
        if len(ch) <= 3:return False
        if ch[0] != '⟦' or ch[-1] != '⟧' or ch.count(';')!=1:return False
        l = ch[1:-1].split(';')
        return all(Z.recognize(elt) for elt in l)
    
    @classmethod
    def from_str(cls,ch:str):
        assert ZIntervalle.recognize(ch)
        return cls(*[Z.from_str(elt) for elt in ch[1:-1].split(';')])
    
    def __iter__(self):
        if (self.binf >=N(0)):
            
            self.binf = N(self.binf.value)
        self.i = self.binf
        return self
    
    def __next__(self):
        if (self.i <=self.bsup):
            self.i+=N(1)
            return self.i-N(1)
        else:raise StopIteration


    def symbolic(self):
        return range(self.binf.value,self.bsup.value+1)
    
    def __str__(self) -> str:
        return "["+str(self.binf)+';'+str(self.bsup)+']'

class Niterator:
    def __init__(self):
        self.i=N(0)
    def __iter__(self):return self
    def __next__(self):
        self.i+=N(1)
        return self.i-N(1)

class EmptySet(Types):
    def __init__(self):
        super().__init__()
    def __str__(self) -> str:
        return '∅'
    def __repr__(self) -> str:
        return self.__str__()
    def recognize(ch:str):
        return ch == '∅'
    def __eq__(self, __value: object) -> bool:
        return type(__value)==EmptySet
    @classmethod
    def from_str(cls,ch):
        assert EmptySet.recognize(ch)
        return cls()
    def __hash__(self) -> int:
        return hash(str(self))
    

TYPES={"ϩ":S,"ℕ":N,"ℤ":Z,"ℝ":R,"ℂ":C,'ℬ':B}
TYPES_ = {v:k for k,v in TYPES.items()}
INCLUSIONS = {
    N:[Z,R,C],
    Z:[R,C],
    R:[C]
}
def attribute_type(ch:str):
    if ch == '∅':return EmptySet()
    for elt in TYPES.values():
        if elt.recognize(ch):
            return elt.from_str(ch)
    if is_tuple(ch):
        return Tuple.from_str(ch,CrossSet(*get_tuple_type(ch)))
    return None

def has_tuple_schema(ch:str):
    if ch[0] != "(" or ch[-1] != ')':
        return False
    return ch.count(';')>=1

def get_tuple_type(ch:str):
    assert has_tuple_schema(ch)
    ch_=ch[1:-1]
    l=ch_.split(';')
    schema =[]
    for elt in l:
        schema.append(type(attribute_type(elt)))
    return schema

def is_tuple(ch:str):
    if not has_tuple_schema(ch):return False
    return not (type(None) in get_tuple_type(ch))


def type_from_str(ch:str):
    if ch == '℘(∅)':return Parts(EmptySet)
    if ch in  TYPES:return TYPES[ch]
    if Parts.recognize(ch):return Parts.from_str(ch)
    if CrossSet.recognize_type(ch):return CrossSet.from_str(ch)
    
    return None

def recognize_type(ch:str):
    if ch == '':return False
    if ch == '℘(∅)':return True
    if ch in TYPES:
        return True
    if ch[0]==chr(8472):
        return Parts.recognize(ch)
    return  CrossSet.recognize_type(ch)

def split_tup(ch:str):
    s,p=False,False
    l=['']
    for car in ch:
        if car =='"' and not s:
            s =not s
        if car =='(' and not p:
            p=not p
        
        if car != '×' or p or s:
            l[-1]+=car
        
        if car =='×' and not s and not p:
            l.append('')


        if car =='"' and  s:
            s =not s
        if car ==')' and  p:
            p=not p

    return l

def stringify(t):
    if t == EmptySet:return '∅'
    if t in TYPES_:
        return TYPES_[t]
    return str(t)

def include (t1,t2):
    #t1 inclus dans t2
    if t1 == t2:return True
    if t1 in INCLUSIONS : return t2 in INCLUSIONS[t1]

    if type(t1)==Parts:
        if type(t2)!=Parts:return False
        return include(t1.typ,t2.typ)
    
    if type(t1)==CrossSet:
        if type(t2) != CrossSet:return False
        if len(t1.schema) != len(t2.schema):return False
        return all(include(t1.schema[i],t2.schema[i]) for i in range(len(t1.schema)))
    
    if t1 == EmptySet and type(t2) == Parts:return True
    raise
    return False

def has_type(obj,t):
    if type(t) == Parts:
        return type(obj)==SET and obj.type == t.typ
    if type(t)==CrossSet:
        return type(obj)==Tuple and obj.type==t
    return type(obj)==t


def full_typize(ch:str):
    if ch =='':
        return None
    String,Set,Tup = False,0,False
    for elt in TYPES_.keys():
        if elt.recognize(ch):
            return elt.from_str(ch)
    
    if ch[0]=='(' and ch[-1]==')':
        ch_ =ch[1:-1]
        l=[]
        mot=''
        for elt in ch_:
            if elt=='"':
                String=not String
            elif elt == ';' and not String and Set ==0:
                l.append(mot)
                mot=''
            else:
                mot += elt
        l.append(mot)
        l_ = [full_typize(elt) for elt in l]
        if any(type(elt)==Tuple for elt in l_):
            return None
        t = CrossSet(*[type(elt) for elt in l_])
        return Tuple.from_str(ch,t)
    
    if ch=='∅' or ch == '{}':
        return EmptySet()
    
    if ch[0]=='{' and ch[-1]=='}':
        ch_ =ch[1:-1]
        l=[]
        mot=''
        for elt in ch_:
            if elt=='"':
                String=not String
            elif elt == '{' and not String:
                Set +=1
            elif elt == '}' and not String:
                Set -=1
            elif elt == '(' and not String:
                if Tup:
                    return None
                Tup=True
            elif elt == ')' and not String:
                if  not Tup:
                    return None
                Tup=False
            if elt == ';' and not String and Set ==0 and not Tup:
                l.append(mot)
                mot=''
            else:
                mot += elt
        l.append(mot)
        l_ = list(set([full_typize(elt) for elt in l]))
        if l_==[EmptySet()]:
            return None
        test = l_[0]
        if test==EmptySet():
            test = l_[1]
        t = type(test)
        if t == SET:
            test:SET
            t = Parts(test.type)
        
        try:
            for i in range(len(l_)):
                l_[i] = default_functions.convert(l_[i],t)
        except:
            return None
        
        r=SET(t)
        for elt in l_:
            r.add(elt)
        return r 
    
    return None




if __name__=='__main__':
    print()
    z = C.from_str('1')
    print(z)
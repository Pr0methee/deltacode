import copy

PREC = 20 #nombre de chiffres après la virgule

class Number:
    def __init__(self,sgn:bool,ent:list[int],frac:list[int]):
        """
        sgn : bool, True -> négatif, False -> positif (0 est +)
        """
        assert type(sgn)==bool
        assert type(ent)==type(frac)==list and len(frac)<=PREC
        assert all([type(elt)==int for elt in ent]) and all([type(elt)==int for elt in frac])
        assert all([0<=elt<10 for elt in ent]) and all([0<=elt<10 for elt in frac])
        self.sgn=sgn#True : <0, False >0
        self.ent=ent#partie entière
        while self.ent[0]==0 and len(self.ent)>1:
            self.ent.pop(0)
        if self.ent == [0] and self.sgn:
            self.sgn=False
        self.frac=frac #partie decimale
        while len(self.frac) != PREC:
            self.frac.append(0)

    def __str__(self):
        r=''
        if self.sgn:
            r+='-'
        r+= ''.join([str(elt) for elt in self.ent])
        if all([elt==0 for elt in self.frac]):
            return r

        r+=','
        r+= ''.join([str(elt) for elt in self.frac])
        while r[-1]=='0':
            r=r[:-1]
        return r
    
    def __add__(self,__other):
        assert type(__other)==Number

        if __other == Number(False,[0],[0]):
            return Number(self.sgn,self.ent,self.frac)
        
        if self.sgn==__other.sgn:
            sgn=self.sgn
            enta=self.ent
            entb=__other.ent
            while len(enta) <len(entb):
                enta=[0]+enta
            while len(entb) <len(enta):
                entb=[0]+entb
            ent=[enta[i]+entb[i] for i in range(len(enta))]
            frac=[self.frac[i]+__other.frac[i] for i in range(PREC)]
            for k in range(PREC-1,0,-1):
                if frac[k]>=10:
                    frac[k]-=10
                    frac[k-1]+=1
            if frac[0]>=10:
                frac[0]-=10
                ent[-1]+=1
            for k in range(len(ent)-1,0,-1):
                if ent[k]>=10:
                    ent[k]-=10
                    ent[k-1]+=1
            if ent[0]>=10:
                ent[0]-=10
                ent=[1]+ent
            return Number(sgn,ent,frac)
        if __other.sgn:
            return self-Number(False,__other.ent,__other.frac)
        return __other-Number(False,self.ent,self.frac)

    def __gt__(self,__other):
        assert type(__other)==Number
        if self==__other:return False
        if self.sgn == __other.sgn == False:
            if len(self.ent) > len(__other.ent):
                return True
            elif len(self.ent) < len(__other.ent):
                return False
            
            #cas partie entière de même longueur
            la=self.ent+self.frac
            lb = __other.ent+__other.frac
            #len(la)=len(lb)
            for i in range(len(la)):
                if la[i]> lb[i]:
                    return True
                elif la[i] < lb[i]:
                    return False
        if self.sgn and not __other.sgn:
            return False#neg > pos -> faux!
        #cas pos > neg -> vrai !
        return True
    
    def __eq__(self, __other) -> bool:
        if type(__other) != Number:return False

        return str(self)==str(__other)

    def __sub__(self,__other):
        assert type(__other)==Number
        if self == __other:
            return Number(False,[0],[0])
        if __other == Number(False,[0],[0]):
            return Number(self.sgn,self.ent,self.frac)
        
        #self - __other
        if __other.sgn:#__other <0 donc self - __other = self + |__other|
            return self + Number(False,__other.ent,__other.frac)
        
        if self.sgn:#cas self <0 donc self-__other = -(|self| + __other)
            r=Number(False,self.ent,self.frac)+__other
            r.sgn=not r.sgn
            return r
        
        #cas pos - pos
        if self > __other:
            enta = self.ent
            entb = __other.ent
            while len(entb)> len(enta):
                enta = [0]+enta
            while len(enta)> len(entb):
                entb = [0]+entb
            
            la = enta + self.frac
            lb = entb + __other.frac
            lc = [0 for _ in range(len(la))]
            for k in range(len(la)-1,-1,-1):
                if la[k]>= lb[k]:
                    lc[k] = la[k]-lb[k]
                else:
                    lc[k] = la[k]-lb[k]+10
                    lb[k-1] += 1
            entc,fracc = lc[:-PREC],lc[-PREC:]
            return Number(False,entc,fracc)
        #self-__other = -(__other - self)
        r = __other-self
        r.sgn = not r.sgn
        return r

    def __mul__(self,__o):
        assert type(__o) == Number
        
        if __o == Number(False,[0],[0]) or self == Number(False,[0],[0]):
            return Number(False,[0],[0])
        
        if self == Number(False,[1],[0]):
            return copy.copy(__o)
        
        if __o == Number(False,[1],[0]):
            return copy.copy(self)
        
        if self.frac == [0 for _ in range(PREC)] and self.ent[-1] ==0:
            a=Number(self.sgn,self.ent[:-1],[0])
            entb=__o.ent+[__o.frac[0]]
            
            fracb=__o.frac[1:]
            b = Number(__o.sgn,entb,fracb)
            return a*b
        if __o.frac == [0 for _ in range(PREC)] and __o.ent[-1] ==0:
            return __o*self


        
        la = self.ent+self.frac
        lb = __o.ent + __o.frac
        while len(la)>len(lb):
            lb = [0]+lb
        while len(lb)>len(la):
            la = [0]+la
        lc=[]
        for k in range(len(la)):
            i = len(la)-1-k
            if la[i]==0:continue
            j = len(lb) - 1
            act=[0 for _ in range(k)]
            while j >=0:
                act = [lb[j]*la[i]]+act
                j-=1

            for j in range(len(act)-1,-1,-1):
                i =0
                while act[j]>=10:
                    i+=1
                    act[j]-=10
                if j == 0 :
                    act = [i]+act
                else:
                    act[j-1] += i

            while len(act)< 2*PREC+1:
                act=[0]+act
            lc.append(NumberD(act[:-2*PREC],act[-2*PREC:]))
        
        S=NumberD([0],[0])
        for elt in lc:
            S += elt
        r=S.troncate()
        r.sgn=(self.sgn!=__o.sgn)
        return r

    def __truediv__(self,__o):
        assert type(__o)==Number
        if __o == Number(True,[1],[0]):
            return Number(not self.sgn,self.ent,self.frac)
        if __o == Number(False,[1],[0]):
            return copy.copy(self)
        if self == Number(False,[0],[0]):
            return Number(False,[0],[0])
        if __o == Number(False,[0],[0]):
            raise ZeroDivisionError
        if __o.frac != [0 for  _ in range(PREC)]:
            a = Number(False,[1,0],[0]) * self
            b = Number(False,[1,0],[0]) * __o
            return a/b
        if __o.ent[-1] ==0:
            a = Number(self.sgn, [0]+self.ent[:-1],[self.ent[-1]]+ self.frac[:-1])
            b = Number(__o.sgn, [0]+__o.ent[:-1],[self.__o[-1]]+ __o.frac[:-1])
            return a/b
        
        la = self.ent+self.frac
        entc,fracc= [],[]
        i = len(__o.ent)
        act =la [:i]
        n = Number(False,act,[0])
        f = False #flag, est-ce qu'on a commencé a remplir la partie decimale
        while len(fracc) != PREC:
            k=Number(False,[0],[0])
            while k*__o-n<Number(False,[0],[0]):
                k+=Number(False,[1],[0])
            k -= Number(False,[1],[0])
            m = __o * k
            n -= m
            n *= Number(False,[1,0],[0])
            if i ==len(la):
                la.append(0)
            n += Number(False,[la[i]],[0])
            i += 1
            if f :
                fracc.append(k.ent[0])
            else:
                entc.append(k.ent[0])
            
            if i > len(self.ent) and not f:
                f = True
        return Number(self.sgn != __o.sgn, entc,fracc)

                
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def from_str(cls,ch:str):
        assert Number.recognize(ch)
        if ch[0]=='-':
            sgn=True
            ch=ch[1:]
        else:sgn=False
        l=ch.split(',')
        l+=['0']
        ent = [int(car) for car in l[0]]
        frac = [int(l[1][i]) for i in range(min(PREC,len(l[1])))]
        return cls(sgn,ent,frac)
    
    def recognize(ch:str):
        return all([car in '0123456789,-' for car in ch])



class NumberD:
    def __init__(self,ent:list[int],frac:list[int]):
        """
        Toujours positif !
        Nombre avec 2PREC chiffres après la virgule
        Sert seulement pour multiplier !
        """
        assert type(ent)==type(frac)==list and len(frac)<=2*PREC
        assert all([type(elt)==int for elt in ent]) and all([type(elt)==int for elt in frac])
        assert all([0<=elt<10 for elt in ent]) and all([0<=elt<10 for elt in frac])
        self.ent=ent#partie entière
        while self.ent[0]==0 and len(self.ent)>1:
            self.ent.pop(0)
        self.frac=frac #partie decimale
        while len(self.frac) != 2*PREC:
            self.frac.append(0)

    
    def __add__(self,__other):
        assert type(__other)==NumberD

        if __other == NumberD([0],[0]):
            return NumberD(self.ent,self.frac)
        

        enta=self.ent
        entb=__other.ent
        while len(enta) <len(entb):
            enta=[0]+enta
        while len(entb) <len(enta):
            entb=[0]+entb
        ent=[enta[i]+entb[i] for i in range(len(enta))]
        frac=[self.frac[i]+__other.frac[i] for i in range(2*PREC)]
        for k in range(2*PREC-1,0,-1):
            if frac[k]>=10:
                frac[k]-=10
                frac[k-1]+=1
        if frac[0]>=10:
            frac[0]-=10
            ent[-1]+=1
        for k in range(len(ent)-1,0,-1):
            if ent[k]>=10:
                ent[k]-=10
                ent[k-1]+=1
        if ent[0]>=10:
            ent[0]-=10
            ent=[1]+ent
        return NumberD(ent,frac)

    def troncate(self):
        return Number(False,self.ent,self.frac[:PREC])










if __name__ == '__main__':
    a =Number(False,[1],[0])
    b = Number(False,[2],[2,3])
    c = Number(True,[2],[2,0,4])
    d= Number.from_str("10")
    print(d*b)
    print("a/b=",a/b)

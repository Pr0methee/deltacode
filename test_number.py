class Number:
    def __init__(self,sgn:bool,ent:list[int],frac:list[int]):
        """
        sgn : bool, True -> négatif, False -> positif (0 est +)
        """
        assert type(sgn)==bool
        assert type(ent)==type(frac)==list and len(frac)<=20
        assert all([type(elt)==int for elt in ent]) and all([type(elt)==int for elt in frac])
        assert all([0<=elt<10 for elt in ent]) and all([0<=elt<10 for elt in frac])
        self.sgn=sgn#True : <0, False >0
        self.ent=ent#partie entière
        while self.ent[0]==0 and len(self.ent)>1:
            self.ent.pop(0)
        if self.ent == [0] and self.sgn:
            self.sgn=False
        self.frac=frac #partie decimale
        while len(self.frac) != 20:
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
            frac=[self.frac[i]+__other.frac[i] for i in range(20)]
            for k in range(19,0,-1):
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
            entc,fracc = lc[:-20],lc[-20:]
            return Number(False,entc,fracc)
        #self-__other = -(__other - self)
        r = __other-self
        r.sgn = not r.sgn
        return r
                
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
        frac = [int(l[1][i]) for i in range(min(20,len(l[1])))]
        return cls(sgn,ent,frac)
    
    def recognize(ch:str):
        return all([car in '0123456789,-' for car in ch])

if __name__ == '__main__':
    a =Number(False,[1],[0])
    a_ = Number.from_str("1")
    assert a==a_
    b = Number(False,[2],[2,3])
    b_ = Number.from_str("2,23")
    assert b==b_
    c = Number(True,[2],[2,0,4])
    c_ = Number.from_str('-2,204')
    assert c==c_
    print('a=',a,';b=',b,';c=',c)
    print('a+a=',a+a)
    print('a-a=',a-a)
    print('a+b=',a+b)
    print('a-b=',a-b)
    print('a+c=',a+c)
    print('a-c=',a-c)
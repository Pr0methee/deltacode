kw = '∃∊≔∀:⇝➣⇴□⟼⟶∄≜'#⟦⟧[]{}
op='+-×÷∧∨¬⇔⇒⊆|^⩾=⊕⩽≠<>⋃⋂∖'
t=("ϩ","ℕ","ℤ","ℝ","ℂ",'ℬ')
indic = (chr(8472),'ℱ','δ')

def without_comments(ch:str):
    r=''
    c,s=False,False
    for car in ch:
        if car =='%' and not c and not s:
            c=True
        if car =='"':
            s=not s
        if not c:
            r +=car
        if car=='\n' and c:
            c=False
    return r.replace('\r','')


def parse_in_sentences(ch:str):
    #l_=parse_g(ch)
    #if l_ == 'ERROR':return l_
    l=[]
    s=False;sc=0;mot='';a=False;d=False#string,sous-code,actual word,arobas, dièse ?
    for car in ch:
        if car =='#':
            d=not d
            if not d:
                l.append(mot+'#')
                mot=''
        if car =='"':s=not s
        if car =='\\' and not s:sc+=1
        if car =='/' and not s :sc-=1

        if car =='.' and not s and sc ==0 and not d:
            if a:
                a=False
            l.append(mot)
            mot=''
        elif car =='\n' and not s and sc==0 and not d :
            if a :
                raise
            continue
        elif car =='@' and not s and sc ==0 and not d:
            assert mot.replace(' ','') ==''
            a=True
            mot='@'
        elif car ==' ' and not s and sc==0 and not d and not a:
            continue
        else:
            if car =='#' and not d:continue
            mot+=car
    if mot != '' and mot[0]==mot[-1]=='#':
        l.append(mot)
    while '' in l:
        l.remove('')
    return l

def parse_types(ch:list[str])-> list[list[str]]:
    mot=''
    l=[[]]
    comp = False
    parenthesis = 0
    d=False
    for sentence in ch:
        for car in sentence:
            if car =='#':d=not d

            if car in indic and not comp and not d:
                comp=True
                l[-1].append(mot)
                mot = car
            elif car in t and not comp and not d:
                l[-1].append(mot)
                l[-1].append(car)
                mot=''
            else: 
                mot += car
            
            if car in '()' and comp:
                if car =='(':
                    parenthesis +=1
                else:
                    parenthesis -=1
                assert parenthesis >=0
                if parenthesis == 0:
                    comp=False
                    l[-1].append(mot)
                    mot=''

        if mot != '':
            l[-1].append(mot)
            mot=''
        verif(l[-1])
        l.append([])
    return l

def verif(l):
    i=0
    while i  < len(l):
        elt = l[i]
        if (elt == '×' and i != 0 and any(car in t for car in l[i-1])) or (any(car in t for car in l[i]) and i != 0 and l[i-1]!='' and l[i-1][-1]== '×'):
            l[i-1]+=elt
            del l[i]
        else:
            i+=1

def parse_a_sentence_(ch:list[str]):
    if ch == []:return []
    if len(ch) == 1:
        return parse_a_sentence(ch[0])
    
    l=[]
    for elt in ch:
        if any(car in t or car in indic for car in elt):
            #c'est un type
            l.append(elt)
        else:
            l_ = parse_a_sentence(elt)
            l+=l_
    return l
    

def parse_a_sentence(ch:str):
    if ch =='':return []
    if ch[0]=='@' or ch[0]==ch[-1]=='#':return [ch]
    l=[]
    mot=''
    s=False;SET = 0;sc=0;chevron=0
    for car in ch:
        if car =='"':s=not s
        if car ==' ' and not s:continue
        if car =='{' and not s:SET +=1
        if car  == '\\' and not s:sc+=1
        if car == '⟨' and not s and sc==0: chevron+=1
        if (car in kw or car in op ) and not s and SET==0 and sc==0 and chevron==0:
            if car == '×' and mot != '' and mot[-1] in t:
                mot+=car
                continue
            if mot !='':
                l.append(mot)
                mot=''
            l.append(car)
        else:
            mot +=car
        if car =='}'and not s:
            SET -=1
        if car =='/' and not s : sc-=1
        if car == '⟩' and not s and sc==0: chevron-=1
    if mot != '':l.append(mot)
    return l


        

def parse(ch:str):
    ch=without_comments(ch)
    l_=parse_in_sentences(ch)
    l_=(parse_types(l_))
    return (list(map(parse_a_sentence_,l_)))#[parse_a_sentence(ch) for ch in l_]
#(chr(2080))

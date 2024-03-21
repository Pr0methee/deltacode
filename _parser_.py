kw = '∃∊+-×÷∧∨¬⇔⇒⊆|^≔⩾=⊕⩽∀≠<>:├?⇝➣⇴□⟼⟶∄≜⋃⋂∖'#⟦⟧[]{}
t=("ϩ","ℕ","ℤ","ℝ","ℂ",'ℬ')

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
    return r


def parse_in_sentences(ch:str):
    #l_=parse_g(ch)
    #if l_ == 'ERROR':return l_
    l=[]
    s=False;sc=0;mot='';a=False;d=False#string,sous-code,actual word,arobas, dièse ?
    for car in ch:
        if car =='#':d=not d
        if car =='"':s=not s
        if car =='\\' and not s:sc+=1
        if car =='/' and not s :sc-=1

        if car =='.' and not s and sc ==0 and not d:
            l.append(mot)
            mot=''
        elif car =='\n' and not s and sc==0 and not d :
            if a :
                l.append(mot)
                a=False
                mot=''
            continue
        elif car =='@' and not s and sc ==0 and not d:
            assert mot.replace(' ','') ==''
            a=True
            mot='@'
        else:
            mot+=car
    if mot != '' and mot[0]==mot[-1]=='#':
        l.append(mot)
    while '' in l:
        l.remove('')
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
        if (car in kw ) and not s and SET==0 and sc==0 and chevron==0:
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
    return (list(map(parse_a_sentence,l_)))#[parse_a_sentence(ch) for ch in l_]
#(chr(2080))

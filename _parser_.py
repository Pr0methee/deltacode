kw = '∃∊+-×÷'
kw2 =[':=']
t=("ϩ","ℕ","ℤ","ℝ","ℂ",'ℬ')


def parse_g (ch:str):
    l=[]
    ch=ch.replace('\n','')
    mot=''
    for car in ch:
        if car =='#':
            if '#' in mot:
                mot+=car
                l.append(mot)
                mot=''
            else:
                l.append(mot)
                mot='#'            
        else:
            mot+=car
    if mot != '':
        l.append(mot)
    return l



def parse_in_sentences(ch:str):
    l_=parse_g(ch)
    l=['']
    s=False
    for elt in l_:
        for car in elt :
            if car == '"':
                s=not s
            if car != '.' or s:
                l[-1]+=car
            else:
                l.append('')

    while '' in l:
        l.remove('')
    return l

def parse_a_sentence(ch:str):
    l=['']
    s=False
    p=False
    for i in range(len(ch)):
        car=ch[i]
        if p:
            p=False
            continue

        if car == '"':
            s=not s

        if s : 
            l[-1] += car
        elif (car in kw and car != '×') or (car == '×' and (l[-1] == '' or l[-1][-1] not in t)): 
            if not l[-1] =='':
                l.append('')
            l[-1] += car
            l.append('')
        elif car in [elt[0] for elt in kw2]:
            if i+1<len(ch) and ch[i:i+2] in kw2:
                if not l[-1] =='':
                    l.append('')
                l[-1] += ch[i:i+2]
                l.append('')
                p=True
        elif car == ' ' and l[-1] != '':
            l.append('')
        elif car != ' ':
            assert car != ' '
            l[-1] += car
        
        
    return l
        

def parse(ch:str):
    l_=parse_in_sentences(ch)
    l=[parse_a_sentence(elt) for elt in l_]
    return l

#parse intervals

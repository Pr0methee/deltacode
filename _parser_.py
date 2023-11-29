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

def parse_p(ch:str):
    l_=parse_g(ch)
    l=[]
    mot=''
    for elt in l_:
        for car in elt:
            if car =='%':
                if '%' in mot:
                    mot+=car
                    l.append(mot)
                    mot=''
                else:
                    l.append(mot)
                    mot='%'            
            else:
                mot+=car
        if mot != '':
            l.append(mot)
    return l


def parse(ch:str):
    l_=parse_g(ch)
    l=[]
    for elt in l_:l += elt.split('.')
    while '' in l:
        l.remove('')
    return l
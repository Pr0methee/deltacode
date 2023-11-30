from tkinter import *
import tkinter.scrolledtext as scrolledtext
import compilator,_parser_

class App(Tk):
    def __init__(self):
        super().__init__()

        self.f1=Frame(self)
        self.f1.pack(side=TOP)
        self.btn = Button(self.f1,text="Parse",command=self.parse)
        self.btn.pack(side=LEFT)
        self.comp = Button(self.f1,text="Compiler",command=self.compile)
        self.comp.pack(side=RIGHT)
        self.run = Button(self.f1,text="Run")#,command=self.Run)
        self.run.pack(side=RIGHT)

        self.text=scrolledtext.ScrolledText(self,cursor="xterm black",font=("Arial 12"))
        self.text.pack(side=TOP,expand=True,fill=BOTH)
        self.text.update()

        i = (self.text.winfo_width()-len('Hello, Begin your code here !'))//23-2
        self.text.insert(END,chr(8422)+'#'*i+'Hello, Begin your code here !'+'#'*i+'\n')
        i = (self.text.winfo_width())//5
        self.text.insert(END,chr(8422)+'-'*i+'\n')
        self.text.bind("<KeyRelease>", self.on_change)
        self.text.bind("<period>", self.compile)
        self.text.bind("<BackSpace>", lambda _:'break' if int(self.text.index(INSERT).split('.')[0]) <=2 else None)

        self.text.tag_config('kw',foreground='#D4AF37')
        self.text.tag_config('t',foreground='#702670')
        self.text.tag_config('v',foreground='#ff8040')
        self.text.tag_config('str',foreground='#329b2f')
        self.text.tag_config('n',foreground='#1E2F97')
        self.text.tag_config('h',foreground='#008000')
        self.text.tag_config('intervalle',foreground='#A04000')
        self.text.tag_config('f',foreground='#804000')
        self.text.tag_config('label',foreground='#0080ff')
        self.text.tag_config('B',font=('Script MT Bold',12),foreground='#702670')
        self.text.tag_config('i',font=('Lucida Calligraphy',12),foreground='#ff8040')

        

        Label(self,text='RETOUR D\'EXECUTION :',fg='#39FF14',bg='black',font=('Terminal',11,'bold')).pack(side=TOP,expand=True,fill=X)
        self.exec = scrolledtext.ScrolledText(self,state='disabled',bg='black',fg='#00FF00',height=10)
        self.exec.pack(side=BOTTOM,expand=True,fill=BOTH)
        self.exec.tag_config("err",foreground='red')
    
    def compile(self,*args):
        place = self.text.index(INSERT)
        if self.text.tag_ranges('B') != ():
            i=0
            while i < len(self.text.tag_ranges('B')):
                self.text.replace(self.text.tag_ranges('B')[i],self.text.tag_ranges('B')[i+1],'\B')
        if self.text.tag_ranges('i') != ():
            i=0
            while i < len(self.text.tag_ranges('i')):
                self.text.replace(self.text.tag_ranges('i')[i],self.text.tag_ranges('i')[i+1],'\i')
        
        t=self.text.get(0.0,END)
        t=t.replace(chr(8422),'')
        t = compilator.compile(t)
        #while t!='' and t[-1]=='\n':
        #    t=t[:-1]
        self.text.delete(0.0,END)
        self.text.insert(END,t[:-1])
        self.colorize()
        self.text.mark_set(INSERT,place)
    
    def parse(self):
        self.compile()
        r=(_parser_.parse(self.text.get(3.0,END)))
        print(r)
            
    def on_change(self,event):
        # Check if the cursor is on the first line
        if int(self.text.index(INSERT).split('.')[0]) <=2:
            self.text.mark_set(INSERT,END)
            if int(self.text.index(INSERT).split('.')[0]) <=2:
                self.text.insert(END,'\n')
                self.text.mark_set(INSERT,END)
        #self.compile()
    
    def colorize(self):
        d=compilator.colorise(self.text.get(3.0,END+'-1c'))
        
        for k,v in d.items():
            for elt in v:
                if k == 'B':self.text.replace(str(elt[0])+'.'+str(elt[1])+'-1c',str(elt[0])+'.'+str(elt[1]),'B')
                elif k == 'i':self.text.replace(str(elt[0])+'.'+str(elt[1])+'-1c',str(elt[0])+'.'+str(elt[1]),'i')
                self.text.tag_add(k,str(elt[0])+'.'+str(elt[1])+'-1c',str(elt[0])+'.'+str(elt[1]))          


if __name__ == '__main__':
    app=App()
    app.mainloop()
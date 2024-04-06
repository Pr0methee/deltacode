from tkinter import *
import tkinter.scrolledtext as scrolledtext
import tkinter.filedialog as filedialog
import compilator,_parser_,Executor,os

class App(Tk):
    def __init__(self):
        super().__init__()
        Grid.columnconfigure(self,0,weight=1)        
        Grid.rowconfigure(self,1,weight=1)
        self.F=True

        self.f1=Frame(self)
        self.f1.grid(row=0,column=0,sticky=NSEW)

        self.file = Menubutton(self.f1,text="Fichier")
        menu = Menu(self.file)
        menu.add_command(label='Enregistrer Sous',accelerator="Ctrl+S",command=self.saveas)
        menu.add_command(label='Ouvrir',accelerator="Ctrl+O",command=self.open)
        self.file.config(menu=menu)
        self.file.pack(side=LEFT)
        self.btn = Button(self.f1,text="Parse",command=self.parse)
        self.btn.pack(side=LEFT)
        self.comp = Button(self.f1,text="Compiler",command=self.compile)
        self.comp.pack(side=LEFT)
        self.run = Button(self.f1,text="Run",command=self.Run)
        self.run.pack(side=LEFT)
        

        self.f2=Frame(self)
        self.f2.grid(row=1,column=0,sticky=NSEW)

        self.text=scrolledtext.ScrolledText(self.f2,cursor="xterm black",font=("Arial 12"))
        self.text.pack(side=TOP,expand=True,fill=BOTH)
        self.text.update()

        i = (self.text.winfo_width())//5
        self.text.insert(END,chr(8422)+'-'*i+'\n')
        self.text.bind("<KeyRelease>", self.on_change)
        self.text.bind("<period>", self.compile)
        self.text.bind("<BackSpace>", lambda _:'break' if int(self.text.index(INSERT).split('.')[0]) <=1 else None)
        self.bind("<Configure>",self.redim)

        self.text.tag_config('kw',foreground='#D4AF37')
        self.text.tag_config('t',foreground='#702670')
        self.text.tag_config('v',foreground='#ff8040')
        self.text.tag_config('str',foreground='#329b2f')
        self.text.tag_config('n',foreground='#1E2F97')
        self.text.tag_config('h',foreground='#008000')
        self.text.tag_config('intervalle',foreground='#A04000')
        self.text.tag_config('f',foreground='#804000')
        self.text.tag_config('label',foreground='#0080ff')
        self.text.tag_config('@',foreground='#808000')
        self.text.tag_config('comm',foreground='#455926')
        self.text.tag_config('i',font=('Lucida Calligraphy',12),foreground='#ff8040')
        

        Label(self.f2,text='RETOUR D\'EXECUTION :',fg='#39FF14',bg='black',font=('Terminal',11,'bold'),height=1).pack(pady=0,side=TOP,expand=True,fill=X)
        self.exec = scrolledtext.ScrolledText(self.f2,bg='black',fg='#39FF14',cursor="xterm black",insertbackground = '#39FF14')
        self.exec.insert(END,chr(8422))
        self.exec.config(state='disabled')
        self.exec.pack(side=BOTTOM,fill=BOTH)
        self.exec.tag_config("err",foreground='red')
        self.exec.tag_config("dec",foreground='orange')
        self.exec.tag_config("inf",foreground='white')
    
    def redim(self,evt):
        d={}
        for elt in self.text.tag_names():
            d[elt]=self.text.tag_ranges(elt)

        if self.F:
            self.F=False
            return
        self.update()
        txt=self.text.get(2.0,END)
        i = (self.text.winfo_width())//5
        up=chr(8422)+'-'*i+'\n'
        txt=up+txt
        self.text.delete(0.0,END)
        
        while txt[-1] == '\n':
            txt=txt[:-1]
        self.text.insert(0.0,txt+'\n')

        for k in d:
            for i in range(len(d[k])//2):
                self.text.tag_add(k,d[k][2*i],d[k][2*i+1])

    
    def compile(self,*args):
        place = self.text.index(INSERT)
        if self.text.tag_ranges('i') != ():
            i=0
            while i < len(self.text.tag_ranges('i')):
                self.text.replace(self.text.tag_ranges('i')[i],self.text.tag_ranges('i')[i+1],'\i')
        
        t=self.text.get(0.0,END)
        t=t.replace(chr(8422),'')
        t = compilator.compile(t)

        self.text.delete(0.0,END)
        self.text.insert(END,t[:-1])
        self.colorize()
        self.text.mark_set(INSERT,place)
    
    def parse(self):
        self.compile()
        r=(_parser_.parse(self.text.get(2.0,END)))
        print(r)
            
    def on_change(self,event):
        # Check if the cursor is on the first line
        if int(self.text.index(INSERT).split('.')[0]) <=1:
            self.text.mark_set(INSERT,END)
            if int(self.text.index(INSERT).split('.')[0]) <=1:
                self.text.insert(END,'\n')
                self.text.mark_set(INSERT,END)
        #self.compile()
    
    def colorize(self):
        d=compilator.colorise(self.text.get(2.0,END+'-1c'))
        
        for k,v in d.items():
            for elt in v:
                self.text.tag_add(k,str(elt[0])+'.'+str(elt[1])+'-1c',str(elt[0])+'.'+str(elt[1]))    

    def Run(self):      
        self.compile()
        ex=Executor.Executor(self.exec)
        ex.execute(self.text.get(2.0,END))
    
    def saveas(self):
        self.compile()
        f = filedialog.asksaveasfilename(defaultextension='.dc',filetypes=[('Compiled delta files','.dc'),('Uncompiled delta files','.du')])
        with open(f,'wb') as file:
            if os.path.splitext(f)[1]=='.dc':
                file.write(bytes(self.text.get(2.0,END),'utf-8'))
            else:
                file.write(bytes(compilator.decompile(self.text.get(2.0,END)),'utf-8'))

    def open(self):
        f = filedialog.askopenfilename(defaultextension='.dc',filetypes=[('Compiled delta files','.dc'),('Uncompiled delta files','.du')])
        if f=='':return
        with open(f,'rb') as file:
            r=file.read().decode('utf-8')
            self.text.insert(END,r)
            self.update()
        self.colorize()





if __name__ == '__main__':
    app=App()
    app.mainloop()

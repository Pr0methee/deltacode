from tkinter import *
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import compilator,_parser_,Executor,os,file


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
        menu.add_command(label='Enregistrer',accelerator="Ctrl+s",command=self.save)
        menu.add_command(label='Nouveau',accelerator="Ctrl+n",command=self.new)
        menu.add_command(label='Ouvrir',accelerator="Ctrl+O",command=self.open)
        self.file.config(menu=menu)
        self.file.pack(side=LEFT)
        self.btn = Button(self.f1,text="Parse",command=self.parse)
        self.btn.pack(side=LEFT)
        self.comp = Button(self.f1,text="Compiler",command=self.compile)
        self.comp.pack(side=LEFT)
        self.run = Button(self.f1,text="Run",command=self.Run)
        self.run.pack(side=LEFT)
        self.close_btn = Button(self.f1,text='x',command=self.close)
        self.close_btn.pack(side=RIGHT)
        self.new_window = Button(self.f1,text='+',command=self.new_tab)
        self.new_window.pack(side=RIGHT)
        
        
        self.f2=Frame(self)
        self.f2.grid(row=1,column=0,sticky=NSEW)

        self.notebook = ttk.Notebook(self.f2)
        self.notebook.pack(fill=BOTH,expand=True)

        self.new_tab()

        Label(self.f2,text='RETOUR D\'EXECUTION :',fg='#39FF14',bg='black',font=('Terminal',11,'bold'),height=1).pack(pady=0,side=TOP,expand=True,fill=X)
        self.exec = scrolledtext.ScrolledText(self.f2,bg='black',fg='#39FF14',cursor="xterm black",insertbackground = '#39FF14')
        self.exec.insert(END,chr(8422))
        self.exec.config(state='disabled')
        self.exec.pack(side=BOTTOM,fill=BOTH)
        self.exec.tag_config("err",foreground='red')
        self.exec.tag_config("dec",foreground='orange')
        self.exec.tag_config("inf",foreground='white')
        self.path=''
    
    def new_tab(self,name='New File'):
        text=scrolledtext.ScrolledText(self.notebook,cursor="xterm black",font=("Consolas",14))
        text.pack(side=TOP,expand=True,fill=BOTH)
        text.update()

        i = (text.winfo_width())//10
        text.insert(END,chr(8422)+'-'*i+'\n')
        text.bind("<KeyRelease>", self.on_change)
        text.bind("<Control-s>", self.save)
        text.bind("<Control-o>", self.open)
        text.bind("<Control-n>", self.new)
        text.bind("<Control-S>", self.saveas)
        text.bind("<period>", self.compile)
        text.bind("<BackSpace>", lambda _:'break' if int(text.index(INSERT).split('.')[0]) <=1 else None)
        self.bind("<Configure>",self.redim)

        text.tag_config('kw',foreground='#D4AF37')
        text.tag_config('t',foreground='#702670')
        text.tag_config('v',foreground='#ff8040')
        text.tag_config('str',foreground='#329b2f')
        text.tag_config('n',foreground='#9191ff')
        text.tag_config('h',foreground='#008000')
        text.tag_config('intervalle',foreground='#A04000')
        text.tag_config('f',foreground='#804000')
        text.tag_config('label',foreground='#0080ff')
        text.tag_config('@',foreground='#808000')
        text.tag_config('comm',foreground='#455926')
        text.tag_config('op',foreground='#0000ff')
        text.tag_config('i',font=('Lucida Calligraphy',12),foreground='#ff8040')

        lst = [self.notebook.tab(tab_index, "text") for tab_index in range(len(self.notebook.tabs()))]
        i=1
        if name == 'New File':
            while name in lst:
                name = 'New File '+str(i)
                i+=1

        self.notebook.add(text,text=name)
        
        last_tab_index = len(self.notebook.tabs()) - 1
        last_tab = self.notebook.tabs()[last_tab_index] 
        self.notebook.select(last_tab)
    
    def close(self):
        self.notebook.forget(self.notebook.select())
        if len( self.notebook.tabs())==0:
            self.new_tab()

    def redim(self,evt):
        if len(self.notebook.tabs())==0:return 
        d={}
        for elt in self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_names():
            d[elt]=self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_ranges(elt)

        if self.F:
            self.F=False
            return
        self.update()
        txt=self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(2.0,END)
        i = (self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].winfo_width())//10
        up=chr(8422)+'-'*i+'\n'
        txt=up+txt
        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].delete(0.0,END)
        
        while txt[-1] == '\n':
            txt=txt[:-1]
        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].insert(0.0,txt+'\n')

        for k in d:
            for i in range(len(d[k])//2):
                self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_add(k,d[k][2*i],d[k][2*i+1])

    
    def compile(self,*args):
        place = self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].index(INSERT)
        if self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_ranges('i') != ():
            i=0
            while i < len(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_ranges('i')):
                self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].replace(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_ranges('i')[i],self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_ranges('i')[i+1],'\i')
        
        t=self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(0.0,END)
        t=t.replace(chr(8422),'')
        t = compilator.compile(t)

        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].delete(0.0,END)
        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].insert(END,t[:-1])
        self.colorize()
        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].mark_set(INSERT,place)
    
    def parse(self):
        self.compile()
        r=(_parser_.parse(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(2.0,END)))
        print(r)
            
    def on_change(self,event):
        # Check if the cursor is on the first line
        if int(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].index(INSERT).split('.')[0]) <=1:
            self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].mark_set(INSERT,END)
            if int(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].index(INSERT).split('.')[0]) <=1:
                self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].insert(END,'\n')
                
                self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].mark_set(INSERT,END)
            self.redim(None)
        #self.compile()
    
    def colorize(self):
        d=compilator.colorise(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(2.0,END+'-1c'))
        
        for k,v in d.items():
            for elt in v:
                self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].tag_add(k,str(elt[0])+'.'+str(elt[1])+'-1c',str(elt[0])+'.'+str(elt[1]))    

    def Run(self):      
        self.compile()
        if self.path =='':
            messagebox.showinfo("Run","You should save your code before running it.")
            self.saveas()
            if self.path == '':
                return
        else:
            self.save()

        ex=Executor.Executor(self.exec)
        nom = self.path.split('/')[-1].split('.')[0]
        ex.execute(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(2.0,END),name=nom)
    
    def saveas(self,*evt):
        self.compile()
        f = filedialog.asksaveasfilename(defaultextension='.df',filetypes=[('Delta files','.df')])
        if f == '':return
        self.path=f
        self.write()
        self.notebook.tab(self.notebook.select(),text=self.path)
    
    def save(self,*evt):
        if self.path == '':
            self.saveas()
            return
        self.compile()
        self.write()

    def write(self):
        r = os.path.splitext(self.path)
        if r[1]=='':
            r=(r[0],'.df')
        assert r[1]=='.df'

        if not os.path.exists(r[0]+'.df'):
            file.create(r[0],r[0].split('/')[-1])

        file.save_text(r[0],r[0].split('/')[-1],compilator.decompile(self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].get(2.0,END)))

    def open(self,*evt):
        f = filedialog.askopenfilename(defaultextension='.df',filetypes=[('Delta files','.df')])
        if f=='':return
        self.path=f
        self.new_tab(self.path)
        r = os.path.splitext(self.path)
        r=file.get_text(r[0],r[0].split('/')[-1])
        self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].insert(END,r)
        self.compile()
        self.update()
        """with open(f,'rb') as file:
            r=file.read().decode('utf-8')
            self.notebook.nametowidget(self.notebook.select()).children['!scrolledtext'].insert(END,r)
            self.update()"""
        self.colorize()
        
    
    def new(self,*evt):
        rep = messagebox.askyesno("New page","Do you want to save before cleanning ?")
        if rep:self.save()
        self.new_tab()





if __name__ == '__main__':
    app=App()
    app.mainloop()

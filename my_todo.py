from tkinter import *
from tkinter import ttk, messagebox
import sqlite3


class Database:
    ''' constructor: Needs Database Name and Table Name
        querry: Uses self
        get_tables staticmethod: Pre-set database
        drop_table staticmethod: Needs Table name
        alter_table staticmethod: Rename a table, Need old Table name, New Table name
        copy_table staticmethod: Needsn Table name
        insert: Needs Completion and Task
        update: Needs Completion, Task and the rowid
        search: Needs the search_word
        delete: Needs the rowid,
        destructor: closes connection'''
    def __init__(self, table_name, database = 'ToDo.db'):
        
        self.database = database
        self.table_name = table_name

        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS """ + self.table_name + """ (
                    completion text,
                    task text
                    )""")
        self.conn.commit()

    def querry(self):
        self.cursor.execute("SELECT rowid, * FROM " + self.table_name + " ORDER BY task ASC")
        database = self.cursor.fetchall()
        return database

    @staticmethod
    def get_tables(database = 'ToDo.db'):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name ASC")
        table_list = cursor.fetchall()
        return table_list

    @staticmethod
    def drop_table(table_name, database = 'ToDo.db'):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE " + table_name)

    @staticmethod
    def alter_table(old_table_name, new_table_name, database = 'ToDo.db'):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE " + old_table_name + " RENAME TO " + new_table_name)

    @staticmethod
    def copy_table(table_name, database = 'ToDo.db'):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE " + table_name + "_COPY AS SELECT * FROM "+ table_name)
        
    def insert(self, completion, task):
        self.cursor.execute("INSERT INTO " + self.table_name + " VALUES (?,?)",
                (completion, task))
        self.conn.commit()

    def update(self, rowid, completion, task):
        self.cursor.execute("UPDATE "+ self.table_name + " SET completion=?, task=? WHERE rowid = ?",
                                (completion, task, rowid))
        self.conn.commit()

    def delete(self, rowid):
        self.cursor.execute("DELETE FROM "+ self.table_name + " WHERE rowid=?",
                            (rowid,))
        self.conn.commit()

    def search(self, search_word):
        self.cursor.execute("SELECT rowid, * FROM " + self.table_name + " WHERE task LIKE ? ORDER BY task ASC", ("%"+search_word+"%",))
        database = self.cursor.fetchall()
        return database

    def delete_all(self, table_name):
        self.cursor.execute("DELETE FROM "+ self.table_name)
        self.conn.commit()
        
    def __del__(self):
        self.conn.close()

class Color:
    screen = '#184E77'
    frame = '#34A0A4'
    label = '#1E6091'
    text = 'white' #
    button ='#1A759F'
    pressed = '#1E6091'
    box = '#D7D9CE' #

def main_window():

    def get_tables():
        tables=Database.get_tables()
        tables_lb.delete(0, END)
        length=0
        for each in sorted(tables):
            tables_lb.insert(END,each[0].replace('_',' '))
            length +=1
        if length >= 6:
            tables_scroll.pack(side=RIGHT, padx=(0,5), pady=5, fill=Y)
            tables_lb.pack(side=LEFT, padx=(5,0), pady=5, expand=True, fill=BOTH)
        else:
            tables_lb.pack(side=RIGHT, padx=5, pady=5, expand=True, fill=BOTH)
            tables_scroll.pack_forget()            

    def view_list():
        try:
            tables_lb.get(tables_lb.curselection())
            global table_name
            table_name = tables_lb.get(ANCHOR)
            table_screen.pack_forget()
            main_screen.pack(expand=TRUE, fill=BOTH)
            main_title.config(text=table_name)
            populate_data()
        except TclError:
            messagebox.showerror('Error', 'Select a List')

    def add_table():
        if table_form_mode == 'new':
            try:         
                Database(table.get().replace(' ','_'))
                get_tables()
                table.delete(0, END)
                tables_entry_frame.pack_forget()
                tables_button_frame.pack(padx=5, pady=5, fill=X)
            except sqlite3.OperationalError as oe:
                messagebox.showerror('Error', oe)        
        elif table_form_mode == 'edit':
            tables=Database.get_tables()
            old_table_name = tables_lb.get(tables_lb.curselection()).replace(' ','_')
            new_table_name = table.get().replace(' ','_')
            if old_table_name == new_table_name:
                messagebox.showerror('Error', 'Change the Name') 
            elif [item for item in tables if item[0] == new_table_name]:
                messagebox.showerror('Error', 'Name already exists.')
            else:
                try:
                    Database.alter_table(old_table_name, new_table_name)
                    get_tables()
                    table.delete(0, END)
                    tables_entry_frame.pack_forget()
                    tables_button_frame.pack(padx=5, pady=5, fill=X)
                except sqlite3.OperationalError as oe:
                    messagebox.showerror('Error', oe)

    def new_table_form():
        global table_form_mode
        table_form_mode = 'new'
        tables_button_frame.pack_forget()
        tables_entry_frame.pack(padx=5, pady=5, fill=X)

    def edit_table_form():
        try:
            tables_lb.get(tables_lb.curselection())
            global table_form_mode
            table_form_mode = 'edit'
            tables_button_frame.pack_forget()
            tables_entry_frame.pack(padx=5, pady=5, fill=X)
            table.delete(0, END)
            table.insert(0, tables_lb.get(tables_lb.curselection()))
        except TclError:
            messagebox.showerror('Error', 'Select a List')        

    def delete_table():
        try:
            tables_lb.get(tables_lb.curselection())
            selected = tables_lb.get(ANCHOR)
            response = messagebox.askyesno("Delete List", "Do you want to Delete\n"+ selected+"?")
            if response == 1:
                Database.drop_table(selected.replace(' ','_'))
                get_tables()
        except TclError:
            messagebox.showerror('Error', 'Select a List')

    def change_list():
        if table_screen.winfo_ismapped() == 1:
            pass
        elif main_screen.winfo_ismapped() == 1:
            main_screen.pack_forget()
            table_screen.pack(expand=TRUE, fill=BOTH)
            get_tables()
        elif help_screen.winfo_ismapped() == 1:
            help_screen.pack_forget()
            table_screen.pack(expand=TRUE, fill=BOTH)
            get_tables()

    def new_list():
        if table_screen.winfo_ismapped() == 1:
            pass
        elif main_screen.winfo_ismapped() == 1:
            main_screen.pack_forget()
            table_screen.pack(expand=TRUE, fill=BOTH)
        elif help_screen.winfo_ismapped() == 1:
            help_screen.pack_forget()
            table_screen.pack(expand=TRUE, fill=BOTH)
        new_table_form()

    def clear_list():
        if help_screen.winfo_ismapped() == 1:
            pass
        elif table_screen.winfo_ismapped() == 1:
            try:
                tables_lb.get(tables_lb.curselection())
                table_name = tables_lb.get(ANCHOR)
                connection = Database(table_name.replace(' ','_')) 
                response = messagebox.askyesno("Clear List", "Do you want to Clear\n"+ table_name+"?")
                if response == 1:
                    connection.delete_all(table_name.replace(' ','_'))
                    get_tables()
                    messagebox.showinfo('Cleared',table_name+"\n Cleared")
            except TclError:
                messagebox.showerror('Error','Select a List')                
        elif main_screen.winfo_ismapped() == 1:
            connection = Database(table_name.replace(' ','_')) 
            response = messagebox.askyesno("Clear List", "Do you want to Clear\n"+ table_name+"?")
            if response == 1:
                connection.delete_all(table_name.replace(' ','_'))
                populate_data()

    def copy_list():
        if help_screen.winfo_ismapped() == 1:
            pass
        elif table_screen.winfo_ismapped() == 1:
            try:
                tables_lb.get(tables_lb.curselection())
                response = messagebox.askyesno("Copy List", "Do you want to Copy\n"+ tables_lb.get(ANCHOR)+"?")
                if response == 1:
                    try:
                        Database.copy_table(tables_lb.get(ANCHOR).replace(' ','_'))
                        get_tables()
                    except sqlite3.OperationalError as oe:
                        messagebox.showerror('Error', oe)
            except TclError:
                messagebox.showerror('Error','Select a List')                
        elif main_screen.winfo_ismapped() == 1:
            response = messagebox.askyesno("Clear List", "Do you want to Copy\n"+ table_name+"?")
            if response == 1:
                try:
                    Database.copy_table(table_name.replace(' ','_'))
                    messagebox.showinfo('Copy',table_name+"\n Copied")
                except sqlite3.OperationalError as oe:
                        messagebox.showerror('Error', oe)

    def show_help():
        if help_screen.winfo_ismapped() == 1:
            pass
        elif main_screen.winfo_ismapped() == 1:
            main_screen.pack_forget()
            help_screen.pack(expand=TRUE, fill=BOTH)
        elif table_screen.winfo_ismapped() == 1:
            table_screen.pack_forget()
            help_screen.pack(expand=TRUE, fill=BOTH)
            
    def change_status(event):
        connection = Database(table_name.replace(' ','_'))        
        selected = todo_tree.focus()
        values = todo_tree.item(selected, 'values')
        if values[1] == '☐':
            connection.update(values[0], 'True', values[2])
        elif values[1] == '✔':
            connection.update(values[0], 'False', values[2])
        if search.get() == 'SEARCH ITEMS':
            populate_data()
        elif search.get() != 'SEARCH ITEMS':
            search_record(event)

    def delete_record():
        connection = Database(table_name.replace(' ','_'))
        try:
            selected = todo_tree.focus()
            values = todo_tree.item(selected, 'values')
            if  values[1] != '-':
                response = messagebox.askyesno("Delete Entry", "Do you want to Delete\n "+ values[2]+" ?")
                if response == 1:
                    connection.delete(values[0])
                    populate_data()
        except IndexError:
            messagebox.showerror('Error', 'Select an Item')
            
    def add_record():
        connection = Database(table_name.replace(' ','_'))
        database = connection.querry()        
        if task.get() == '':
            messagebox.showerror('Error', 'Task is empty.')
        elif task.get().upper() in map(lambda a: a[2].upper(), database):
            response = messagebox.askyesno('Duplicate', task.get()+' is already on the list.\nWould you like to add another?')
            if response == 1:
                connection.insert('False', task.get())
                task.delete(0, END)
                entry_frame.pack_forget()
                button_frame.pack(padx=5, pady=5, fill=X)
                populate_data()
            else:
                task.delete(0, END)
                entry_frame.pack_forget()
                button_frame.pack(padx=5, pady=5, fill=X)
        else:
            connection.insert('False', task.get())
            task.delete(0, END)
            entry_frame.pack_forget()
            button_frame.pack(padx=5, pady=5, fill=X)
            populate_data()

    def on_entry_click(event):
        """function that gets called whenever entry is clicked"""
        if search.get() == 'SEARCH ITEMS':
           search.delete(0, "end") # delete all the text in the entry
           search.insert(0, '') #Insert blank for user input
           search.config(fg = 'black')
    def on_focusout(event):
        if search.get() == '':
            search.delete(0, "end")
            search.insert(0, 'SEARCH ITEMS')
            search.config(fg = 'grey')

    def search_record(event):           
        connection = Database(table_name.replace(' ','_'))
        database = connection.search(search.get())
        database.sort(key=lambda a: (a[2].lower()))
        undone = len(list(filter(lambda x: 'False' in x, database)))
        done = len(list(filter(lambda x: 'True' in x, database)))
        todo_tree.delete(*todo_tree.get_children())

        if len(database) == 0:
            todo_tree.insert(parent='', index='end', values=(' ', '-', 'NONE FOUND'), tags=('header'))
        
        if undone > 0:
            todo_tree.insert(parent='', index='end', values=(' ', '-', 'TO DO: ' +str(undone)), tags=('header'))
            
        count = 0
        for record in database:
            if record[1] == 'False':
                if count % 2 == 0:
                    todo_tree.insert(parent='', index='end', values=(record[0],'☐', record[2]), tags=('evenrow'))
                else:
                    todo_tree.insert(parent='', index='end', values=(record[0],'☐', record[2]), tags=('oddrow'))
                count+=1
                
        if done > 0:
            todo_tree.insert(parent='', index='end', values=(' ', '-', 'Completed: ' +str(done)), tags=('header'))
        
        for record in database:
            if record[1] == 'True':
                if count % 2 == 0:
                    todo_tree.insert(parent='', index='end', values=(record[0],'✔', record[2]), tags=('evenrow', 'done',))
                else:
                    todo_tree.insert(parent='', index='end', values=(record[0],'✔', record[2]), tags=('oddrow', 'done',))
                count+=1
      
    def populate_data():
        connection = Database(table_name.replace(' ','_'))
        database = connection.querry()
        database.sort(key=lambda a: (a[2].lower()))
        undone = len(list(filter(lambda x: 'False' in x, database)))
        done = len(list(filter(lambda x: 'True' in x, database)))
        todo_tree.delete(*todo_tree.get_children())
        
        if undone > 0:
            todo_tree.insert(parent='', index='end', values=(' ', '-', 'TO DO: ' +str(undone)), tags=('header'))
            
        count = 0
        for record in database:
            if record[1] == 'False':
                if count % 2 == 0:
                    todo_tree.insert(parent='', index='end', values=(record[0],'☐', record[2]), tags=('evenrow'))
                else:
                    todo_tree.insert(parent='', index='end', values=(record[0],'☐', record[2]), tags=('oddrow'))
                count+=1
                
        if done > 0:
            todo_tree.insert(parent='', index='end', values=(' ', '-', 'Completed: ' +str(done)), tags=('header'))
        
        for record in database:
            if record[1] == 'True':
                if count % 2 == 0:
                    todo_tree.insert(parent='', index='end', values=(record[0],'✔', record[2]), tags=('evenrow', 'done',))
                else:
                    todo_tree.insert(parent='', index='end', values=(record[0],'✔', record[2]), tags=('oddrow', 'done',))
                count+=1

    # BUILD THE MENU BAR
    menubar = Menu(app)
    app.config(menu=menubar)
    file = Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file)
    file.add_command(label='Change List', command=change_list)
    file.add_command(label='New List', command=new_list)
    file.add_separator()
    file.add_command(label='Clear List', command=clear_list)
    file.add_command(label='Copy List', command=copy_list)
    file.add_separator()
    file.add_command(label='Help', command=show_help)
    file.add_separator()
    file.add_command(label='Exit', command=app.destroy)

    #----------------------------------------- THE TABLE SCREEN     
    help_screen = Frame(app, bg=Color.screen)

    # TITLE BAR
    help_title_frame = Frame(help_screen, bg=Color.frame)
    help_title_frame.pack(padx=5, pady=5, fill=X)
    help_title = Label(help_title_frame, text='App Info', font=('courier',16,'bold'), bg=Color.label, fg=Color.text)
    help_title.pack(padx=5, pady=5, fill=X)

    # THE MAIN BODY
    help_body_frame = Frame(help_screen, bg=Color.frame)
    help_body_frame.pack(padx=5, pady=5, expand=True, fill=BOTH)
    
    help_info = Text(help_body_frame, font=('courier', 7), bg=Color.box)
    help_info.pack(padx=5, pady=5, expand=True, fill=BOTH)
    help_info.insert(1.0,"""
TABLE SCREEN:
- Here you can see all of your ToDo lists,
  Sorted by name.
  
- You view the list contents by first 
  selecting a list, then pressing the 
  View List button.
  
- Add a New List with the Add List button.
  (List names cannot start with numbers.)

- Edit a List Name by selecting a list and
  pressing the Edit Button.
    
- Delete a list by selecting a list and 
  pressing the Delete Button.

LIST SCREEN:
- This is where your ToDo items are, 
  Sorted by name.
    
- Things ToDo are at the top, and completed
  items on the bottom.
    
- Add a ToDo item by pressing the Add
  button.
    
- Mark an item complete by double clicking
  the item.
    
- To Delete an item first select an item 
  then press the Delete button.

FILE MENU:
- Here you change the list you are viewing.
     
- You can add a new list.
    
- Or clear the list you are working on.
    """)
    help_info.configure(state='disabled')
    
    #----------------------------------------- THE TABLE SCREEN     
    table_screen = Frame(app, bg=Color.screen)
    table_screen.pack(expand=TRUE, fill=BOTH)

    # TITLE BAR
    tables_title_frame = Frame(table_screen, bg=Color.frame)
    tables_title_frame.pack(padx=5, pady=5, fill=X)
    tables_title = Label(tables_title_frame, text='Select List', font=('courier',16,'bold'), bg=Color.label, fg=Color.text)
    tables_title.pack(padx=5, pady=5, fill=X)
    
    # THE MAIN BODY
    tables_body_frame = Frame(table_screen, bg=Color.frame)
    tables_body_frame.pack(padx=5, pady=5, expand=True, fill=BOTH)

    tables_scroll = Scrollbar(tables_body_frame)    
    tables_lb = Listbox(tables_body_frame, yscrollcommand=tables_scroll.set, font=('courier', 15), height=5, justify=CENTER)
    tables_scroll.config(command=tables_lb.yview)
    # THEY GET PACKED FROM THE GET_TABLES FUNCTION
    
    # THE BUTTONS FRAME
    tables_button_frame = Frame(table_screen, bg=Color.frame)
    tables_button_frame.pack(padx=5, pady=5, fill=BOTH)

    enter_button = Button(tables_button_frame, text='VIEW LIST', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=view_list)
    enter_button.pack(padx=5, pady=5, expand=True, fill=BOTH)

    tables_add_button = Button(tables_button_frame, text='ADD LIST', font=('courier',10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=new_table_form)
    tables_add_button.pack(side=LEFT, padx=5, pady=5, expand=True)

    tables_edit_button = Button(tables_button_frame, text='EDIT', font=('courier',10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=edit_table_form)
    tables_edit_button.pack(side=LEFT, padx=5, pady=5, expand=True)
    
    tables_delete_button = Button(tables_button_frame, text='DELETE', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=delete_table)
    tables_delete_button.pack(side=LEFT, padx=5, pady=5, expand=True)

    # ENTRY FRAME
    tables_entry_frame = Frame(table_screen, bg=Color.frame)
    
    table = Entry(tables_entry_frame, font=('courier', 14), justify=CENTER)
    table.pack(anchor=N,padx=5, pady=5, expand=True, fill=X)

    tables_save_button = Button(tables_entry_frame, text='SAVE', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=add_table)
    tables_save_button.pack(side=LEFT,padx=5, pady=5, expand=True)

    tables_cancel_button = Button(tables_entry_frame, text='CANCEL', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=lambda:[
        table.delete(0, END),
        tables_entry_frame.pack_forget(),
        tables_button_frame.pack(padx=5, pady=5, fill=X)])
    tables_cancel_button.pack(side=LEFT,padx=5, pady=5, expand=True)

    get_tables()
    
    #----------------------------------------- MAIN SCREEN
    main_screen = Frame(app, bg=Color.screen)
    # TITLE BAR
    title_frame = Frame(main_screen, bg=Color.frame)
    title_frame.pack(padx=5, pady=5, fill=X)
    main_title = Label(title_frame, text='', font=('courier',16,'bold'), bg=Color.label, fg=Color.text)
    main_title.pack(padx=5, pady=5, fill=X)

    # THE MAIN BODY
    body_frame = Frame(main_screen, bg=Color.frame)
    body_frame.pack(padx=5, pady=5, expand=True, fill=BOTH)

    search = Entry(body_frame, font=('courier', 14), justify=CENTER)
    search.pack(anchor=N,padx=5, pady=5, expand=True, fill=X)
    search.insert(0, 'SEARCH ITEMS')
    search.config(fg = 'grey')
    search.bind('<FocusIn>', on_entry_click)
    search.bind('<FocusOut>', on_focusout)
    search.bind('<KeyRelease>', search_record)

    tree_scroll = Scrollbar(body_frame)
    tree_scroll.pack(side=RIGHT, padx=(0,5), pady=5, fill=Y)
    todo_tree = ttk.Treeview(body_frame, yscrollcommand=tree_scroll.set, selectmode='browse')
    todo_tree.pack(side=RIGHT, padx=(5,0), pady=5, expand=True, fill=BOTH)
    tree_scroll.config(command=todo_tree.yview)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview", font=('courier', 12), background="#F8F8FF", foreground="black", rowheight=100, fieldbackground="#D3D3D3")
    style.map('Treeview',background=[('selected', "#347083")])

    todo_tree['columns'] = ("rowid","completion", "task")
    todo_tree.column("#0", width=0, stretch=NO)
    todo_tree.column("rowid", width=0, stretch=NO)
    todo_tree.column("completion", anchor=CENTER, width=100, stretch=NO)
    todo_tree.column("task", anchor=CENTER, width=8)

    todo_tree.heading("#0",text="", anchor=W)
    todo_tree.heading("rowid",text="", anchor=W)
    todo_tree.heading("completion",text="", anchor=CENTER)
    todo_tree.heading("task",text="Task", anchor=CENTER)
    todo_tree.bind("<Double-Button>", change_status)
       
    todo_tree.tag_configure('header',font=('courier',12), foreground=Color.text, background=Color.label)
    todo_tree.tag_configure('done',font=('courier',12, 'overstrike'), foreground='grey')    
    todo_tree.tag_configure('oddrow', background="white")
    todo_tree.tag_configure('evenrow', background="lightblue")

    # THE BUTTONS FRAME
    button_frame = Frame(main_screen, bg=Color.frame)
    button_frame.pack(padx=5, pady=5, fill=X)

    add_button = Button(button_frame, text='ADD ITEM', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=lambda:[
        button_frame.pack_forget(),entry_frame.pack(padx=5, pady=5, fill=X)])
    add_button.pack(side=LEFT,padx=5, pady=5, expand=True)

    delete_button = Button(button_frame, text='DELETE', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=delete_record)
    delete_button.pack(side=LEFT,padx=5, pady=5, expand=True)

    # THE ENTRY FRAME
    entry_frame = Frame(main_screen, bg=Color.frame)

    task = Entry(entry_frame, font=('courier', 14), justify=CENTER)
    task.pack(anchor=N,padx=5, pady=5, expand=True, fill=X)

    save_button = Button(entry_frame, text='SAVE', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=add_record)
    save_button.pack(side=LEFT,padx=5, pady=5, expand=True)

    cancel_button = Button(entry_frame, text='CANCEL', font=('courier', 10), bg=Color.button, fg=Color.text, activebackground=Color.pressed, command=lambda:[
        task.delete(0, END), entry_frame.pack_forget(), button_frame.pack(padx=5, pady=5, fill=X)])
    cancel_button.pack(side=LEFT,padx=5, pady=5, expand=True)


if __name__=='__main__':
    app = Tk()
    app.title('TO DO')
    main_window()
    app.mainloop()

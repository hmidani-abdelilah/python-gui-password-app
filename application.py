from customtkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as ms
import tkcalendar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3
import hashlib
import time 
from datetime import datetime
from tkinter import filedialog as fd
from PIL import ImageTk,Image
import csv
import bcrypt
import re 
from io import BytesIO

start_time = time.perf_counter()
db = sqlite3.connect("manageapp.db")
c =  db.cursor()
# creat table account
c.execute('''CREATE TABLE IF NOT EXISTS "account" (
            "username"	TEXT NOT NULL,
            "password"	TEXT NOT NULL,
            "Email"	TEXT,
            "photo"	BLOB,
            "admin"	INTEGER NOT NULL,
            "datecreated"	NUMERIC NOT NULL,
            PRIMARY KEY("username"));''')
# creat table event
c.execute('''CREATE TABLE IF NOT EXISTS "event" (
                "logindate"	NUMERIC NOT NULL,
                "event"	TEXT,
                "username"	TEXT NOT NULL,
                CONSTRAINT "usepk" FOREIGN KEY("username") REFERENCES "account"("username")
                ON DELETE SET DEFAULT ON UPDATE SET DEFAULT
            );''')
# creat table userapplication
c.execute('''CREATE TABLE IF NOT EXISTS "userapplication" (
                    "nameapp"	TEXT NOT NULL,
                    "user_app"	TEXT NOT NULL,
                    "password"	TEXT,
                    "expiredate"	NUMERIC NOT NULL,
                    "email_in_app"	TEXT,
                    "creationdate"	NUMERIC,
                    "note"  TEXT,
                    "username"	TEXT,
                    CONSTRAINT "user_info_app" FOREIGN KEY("nameapp") REFERENCES "infoapplication" ON DELETE NO ACTION ON UPDATE SET DEFAULT,
                    CONSTRAINT "user_creat_recored" FOREIGN KEY("username") REFERENCES "account"("username") ON DELETE NO ACTION ON UPDATE SET DEFAULT
                );''')
# creat table infoapplication
c.execute("""CREATE TABLE IF NOT EXISTS "infoapplication" (
                    "nameapp"	TEXT NOT NULL,
                    "location"	TEXT,
                    "ip_link"	TEXT,
                    "note"      TEXT,
                    "photo"	BLOB,
                    PRIMARY KEY("nameapp")
                );""")
# creat table ifuserapp
c.execute("""CREATE TABLE IF NOT EXISTS "ifuserapp" (
                "nameapp"	TEXT,
                "personid"	INTEGER,
                CONSTRAINT "nameappofperson" FOREIGN KEY("nameapp") REFERENCES  "infoapplication"("nameapp") ,
                CONSTRAINT "personofappname" FOREIGN KEY("personid") REFERENCES "person"("personid") 
                );
                """)
# creat table person
c.execute("""CREATE TABLE IF NOT EXISTS "person" (
                                        "personid"	INTEGER NOT NULL,
                                        "firstname"	TEXT,
                                        "lastname"	TEXT,
                                        "email"	TEXT,
                                        "phone"	TEXT,
                                        "div_service"	TEXT,
                                        "photo"	BLOB,
                                        PRIMARY KEY("personid" AUTOINCREMENT)
                                    );""")
#c.execute("CREATE TABLE IF NOT EXISTS user(username text not null  primary key,password text not null,email text,admin NUMERIC);")
db.commit()
db.close()

set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App:
    def __init__(self,windows):
        self.windows = windows
        self.widgets()
        self.appearance(self.windows)
        self.fetchall_app()
        #self.appname = StringVar()
    
    def fetchall_app(self):
        db = sqlite3.connect("manageapp.db")
        c =  db.cursor()
        self.find_infouserapp = """
                SELECT ua.nameapp, ua.user_app, ua.password, ua.expiredate, ua.email_in_app, ua.creationdate , ia.note, ia.location, ia.ip_link
                FROM userapplication ua
                INNER JOIN infoapplication ia ON ia.nameapp = ua.nameapp
            """
        c.execute(self.find_infouserapp)
        result = c.fetchall()
        # generate sample data
        #contacts = []
        #for n in range(1, 10):
        #    contacts.append((f'name app {n}', f'user app {n}', f'password app {n}', datetime.now() ,f'emailapp{n}@example.com', f'note app{n}', f'location app{n}', f'url of app{n}', f'url dof app{n}'))

        # add data to the treeview
        #for contact in contacts:
        #    tree.insert('', tk.END, values=contact)
        # add counter 
        self.tree.delete(*self.tree.get_children())
        global cnt 
        self.cnt = 0

        # add data to the treeview
        for contact in result:
            if self.cnt % 2 == 0:
                self.tree.insert('', tk.END, values=contact,text="",tags=('evenrow',))
            else:
                self.tree.insert('', tk.END, values=contact,text="",tags=('oddrow',))
            self.cnt += 1
        db.commit()
        db.close()

    def emailValid(self,email):  
        global regex
        regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        if re.fullmatch(regex, email):  
            return True  
        else:  
            return False
    
    def regestration(self):
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.login_page.place_forget()
        self.regitration_page.place(relx=.5, rely=.5 ,anchor=CENTER)
    
   
    def go_to_login(self):
        self.reusername_entry.delete(0, END)
        self.repassword_entry.delete(0, END)
        self.repassword_entry1.delete(0, END)
        self.reemail_entry.delete(0, END)    
        self.regitration_page.place_forget()
        self.login_page.place(relx=.5, rely=.5 ,anchor=CENTER)
    
    # hashed password 
    def encrypt_password(self,crid :str):
        self.crid_encrypt = crid.encode("utf-8")
        # generating the salt 
        self.salt = bcrypt.gensalt()
        self.hashed_crid = bcrypt.hashpw(self.crid_encrypt, self.salt)
        print(self.hashed_crid)
        return self.hashed_crid
    
    # convert to binary
    def convertToBinaryData(self,filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            self.blobData = file.read()
        return self.blobData
   
    """   # Convert binary data
    def writeTofile(self,data, filename):
        # Convert binary data to proper format and write it on Hard Disk
        with open(filename, 'wb') as file:
            file.write(data)
        print("Stored blob data into: ", self.filename, "\n") """
    
    def submit(self):
        self.admin = 0
        self.photoa = None
        self.new_user = self.reusername_entry.get().lower().strip()
        self.new_password = self.repassword_entry.get()
        self.new_repassword = self.repassword_entry1.get()
        self.new_email = self.reemail_entry.get().lower().strip()
        if self.new_user == "":
            ms.showerror("Bot Error", "'Username' cannot be blank.")
        elif self.new_password == "":
            ms.showerror("Bot Error", "'Password' cannot be blank.")
        elif self.new_repassword == "":
            ms.showerror("Bot Error", "'Password' cannot be blank.")
        elif self.new_email == "":
            ms.showerror("Bot Error", "'Email' cannot be blank.")
        elif not self.emailValid(self.new_email):
            ms.showerror("Bot Error", "'Email' Isn't Valide \n Write for example : hmidaniabdelilah92@gmail.com.")
        elif not self.new_user or not self.new_password or not self.new_repassword or not self.new_email :
            ms.showerror("Error", "Please Enter a Username and Password and Email ")
        elif self.new_password == self.new_repassword :
            
            # hashed user
            self.hashed_user = self.encrypt_password(self.new_user)
            # hashed password
            self.hashed_password = self.encrypt_password(self.new_password)

            db = sqlite3.connect("manageapp.db")
            c =  db.cursor()
            c.execute("INSERT INTO account VALUES (?,?,?,?,?,datetime('now'))",(self.hashed_user,self.hashed_password,self.new_email,self.photoa,self.admin))
            db.commit()
            db.close()
            self.reusername_entry.delete(0, END)
            self.repassword_entry.delete(0, END)
            self.repassword_entry1.delete(0, END)
            self.reemail_entry.delete(0, END)
            ms.showinfo("Great", "Account has been Created") 
            self.go_to_login()        
        else:
            ms.showerror("Bot Error", "'Password' is not mutch.")

    def login(self,a=None):
        self.username = self.username_entry.get().lower().strip()
        self.password = self.password_entry.get().strip()
        # Here you can add your own code to check if the username and password are valid.
        # For this example, we'll just assume they are.
        if self.username == "":
            ms.showerror("Bot Error", "'username' cannot be blank.")
        elif self.password == "":
            ms.showerror("Bot Error", "'password' cannot be blank.")
        elif not self.username or not self.password:
            ms.showerror("Error", "Please enter a username and password")
            self.error_label.configure(text="Invalid username or password")
        # encode user
        self.userh = self.username.encode("utf-8")
        # encode password
        self.passwordh = self.password.encode("utf-8")
        db = sqlite3.connect("manageapp.db")
        cursor = db.cursor()           
        self.find_user = "select username,password from account "
        cursor.execute(self.find_user)
        result = cursor.fetchall()
        db.close()
        #print(result)
        """ for i,r  in result:
            print(f"this is user: {i}")
            print(f"this is password : {r}") 
        if bcrypt.checkpw(password.encode("utf-8"), var):
                print("It matches")
        else:
                print("Didn't match") """
        global user_existe
        user_existe = False

        global password_existe 
        password_existe = False

        for r,i in result:
            if bcrypt.checkpw(self.userh, r) and bcrypt.checkpw(self.passwordh, i) :            
                user_existe = True
                password_existe = True

        if user_existe and password_existe:
            self.login_page.place_forget()
            #self.appearance_mode_label.grid_forget()
            #self.appearance_mode_optionemenu.grid_forget()
            #self.appearance_mode_label.grid(row=0,column=0,sticky=NE)
            #self.appearance_mode_optionemenu.grid(row=0,column=1,sticky=NE)
            self.search_fram.grid(row=0,column=0,sticky=NSEW)
            self.windows_frame.grid(row=1,column=0,sticky=NW)
            self.info_fram.grid(row=0,column=3,sticky=NE,padx=1,pady=2)
            self.info_fram1.grid(row=0,column=3,sticky=NE,padx=1,pady=2)
            self.button_fram.grid(row=2,column=0,columnspan=4,sticky=W)
            self.button_fram1.grid(row=2,column=0,columnspan=4,sticky=W)

            ms.showinfo("Great", f"Wellcome {self.username_entry.get()}")
            ############### w9ft hna  
        else:
            ms.showerror("Error", "Invalid username or password")
            self.error_label.configure(text="Invalid username or password")
            

    def show_passwd(self):
        if self.password_entry.cget('show') == "•":
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")
        
    def reshow_repassword(self):
        if self.repassword_entry.cget('show') == "•" or self.repassword_entry1.cget('show'):
            self.repassword_entry.configure(show="")
            self.repassword_entry1.configure(show="")
        else:
            self.repassword_entry.configure(show="•")
            self.repassword_entry1.configure(show="•")

    def logout(self):
        self.reusername_entry.delete(0, END)
        self.repassword_entry.delete(0, END)
        self.repassword_entry1.delete(0, END)
        self.reemail_entry.delete(0, END) 
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.windows_frame.grid_forget()
        self.info_fram.grid_forget()
        self.button_fram.grid_forget()
        self.button_fram1.grid_forget()
        self.search_fram.grid_forget()
        self.login_page.place(relx=.5, rely=.5 ,anchor=CENTER)
        self.regiter_button.configure(state="disabled")
        #self.gotologin_button.invoke()
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def appearance(self,fram):
        #self.appearance_mode_label = CTkLabel(fram, text="Appearance Mode:")
        #self.appearance_mode_label.grid(row=0,column=0)
        self.appearance_mode_optionemenu = CTkOptionMenu(fram, values=["Light", "Dark", "System"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=0,column=0,padx=10,pady=5,sticky=NW)
    
    
    def optionmenu_callback(self,choice):
        print("optionmenu dropdown clicked:", choice)
    # delete recored from tree 1
    def delete_recordtree(self):
        # Get the selected item
        message = ms.askyesno(title="Delete recored",message="Are you shore to delete it \n Worning !!!")
        if message:
            db = sqlite3.connect("manageapp.db")
            c =  db.cursor()
            c.execute("DELETE FROM userapplication WHERE user_app = ?", (self.user_application.get(),))
            db.commit()
            db.close()
            self.tree.delete(*self.tree.get_children())
            self.cleartree()
            self.fetchall_app()
            #selected_item = self.tree.selection()
            #if selected_item:
                # Delete the selected item
            #    self.tree.delete(selected_item)
    
    # delete multi recored from treeview application
    def delete_recordstree(self):
        message = ms.askyesno(title="Delete recored Selected",message="Are you shore to delete it \n Worning !!!")
        if message:
            # Get selected items
            selected_items = self.tree.selection()
            if selected_items:
                # Delete all selected items
                for item in selected_items:
                    self.tree.delete(item)

    # delete all recoreds in treeview application
    def delete_all_recordstree(self):
        message = ms.askyesno(title="Delete All Recored",message="Are you shore to delete All \n Worning !!!")
        if message:
            # Delete all items from the TreeView
            self.tree.delete(*self.tree.get_children())

    # export selected recored as csv on treeview
    def export_selectedtree(self):
        # Get selected items
        selected_items = self.tree.selection()
        if selected_items:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                # Create a CSV file and write selected data
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    
                    # Write headers to the CSV file
                    headers = ['application name', 'user application', 'password application','email application','note application','location application', 'link of application']  
                    writer.writerow(headers)
                    
                    # Write selected data to the CSV file
                    for item in selected_items:
                        values = self.tree.item(item, 'values')
                        writer.writerow(list(values))
                ms.showinfo(title="Export Selected recored",message=f"Export Select Recored \n file name: {file.name} \n Will Done ...!!")
        else:
            ms.showinfo(title="Not Selected Any recored",message="Select Any Record !!?? \n And contineu.....")
    # export all recored of application treeview
    def export_alltree(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            # Create a CSV file and write all data
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)

                # Write headers to the CSV file
                headers = ['application name', 'user application', 'password application','email application','note application','location application', 'link of application']  
                writer.writerow(headers)

                # Write all data from the TreeView to the CSV file
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    writer.writerow(list(values))
            ms.showinfo(title="Export All recoreds",message=f"Export All Recored \n file name: {file.name} \n Will Done ...!!")

    # add recored in treeview application 
    def add_recordtree(self):
        # Get the values from the entry fields or wherever you want to retrieve them
        #contact = [self.application_name.get(),self.user_application.get(),self.password_application.get(),datetime.now(),self.email_application.get(),datetime.now(),self.note_application.get(),self.location_application.get(),self.LINK_of_application.get()]
        # Insert a new record (row) into the TreeView
        #if self.cnt % 2 == 0:
        #    self.tree.insert('', tk.END, values=contact,text="",tags=('evenrow',))
        #else:
        #    self.tree.insert('', tk.END, values=contact,text="",tags=('oddrow',))
        #self.cnt += 1
        
        try:
            app_Photo = self.convertToBinaryData(self.filename)
        except:
            app_Photo = None

        db = sqlite3.connect("manageapp.db")
        c =  db.cursor()
        c.execute("INSERT OR IGNORE INTO infoapplication VALUES (?,?,?,?,?)",(self.application_name.get(),self.location_application.get(),self.LINK_of_application.get(),self.note_application.get(),app_Photo))
        db.commit()
        c.execute("INSERT INTO userapplication VALUES (?,?,?,datetime('now','74 days'),?,datetime('now'),?,?)",
                  (self.application_name.get(),self.user_application.get(),self.password_application.get(),self.email_application.get(),self.LINK_of_application.get(),self.username))
        db.commit()
        db.close()
        self.cleartree()
        ms.showinfo(title="Add recored",message="Will Done ...!!")
        self.tree.delete(*self.tree.get_children())
        self.fetchall_app()
        app_Photo = None
        self.filename = None
    # update recored treeview application
    def update_recordtree(self):
        # Get the selected item
        #selected_item = self.tree.selection()
        #if selected_item:
            # Get the values from the entry fields or wherever you want to retrieve them
            # Update the values of the selected item in the TreeView
        #    self.tree.item(selected_item, values=(self.application_name.get(),self.user_application.get(),self.password_application.get(),self.email_application.get(),self.note_application.get(),self.location_application.get(),self.LINK_of_application.get()))      
        #self.application_name.delete(0, END)
        #self.user_application.delete(0, END)
        #self.password_application.delete(0, END)
        #self.email_application.delete(0, END)
        #self.note_application.delete(0, END)
        #self.location_application.delete(0, END)
        #self.LINK_of_application.delete(0, END)
        #ms.showinfo(title="Update recored",message="Will Done ...!!")
        try:
            app_Photo = self.convertToBinaryData(self.filename)
        except:
            app_Photo = self.result_bind[0]

        db = sqlite3.connect("manageapp.db")
        c =  db.cursor()
        c.execute("UPDATE infoapplication SET nameapp = ? , location = ? , ip_link = ? , note = ? , photo = ? WHERE nameapp = ?",(self.application_name.get(),self.location_application.get(),self.LINK_of_application.get(),self.note_application.get(),app_Photo,record[0]))
        db.commit()
        # Update userapplication table including the nameapp field
        c.execute("UPDATE userapplication SET nameapp = ?, user_app = ?, password = ?, expiredate = datetime('now','74 days'), email_in_app = ?, creationdate = datetime('now'), note = ?, username = ? WHERE nameapp = ?", (self.application_name.get(), self.user_application.get(), self.password_application.get(), self.email_application.get(), self.LINK_of_application.get(), self.username, record[0]))
        db.commit()
        db.close()
        self.cleartree()
        ms.showinfo(title="Update recored",message="Will Done ...!!")
        self.tree.delete(*self.tree.get_children())
        self.fetchall_app()
        app_Photo = None
        self.filename = None


    
    # clear Entry application 
    def cleartree(self):
        self.application_name.delete(0, END)
        self.user_application.delete(0, END)
        self.password_application.delete(0, END)
        self.email_application.delete(0, END)
        self.note_application.delete(0, END)
        self.location_application.delete(0, END)
        self.LINK_of_application.delete(0, END)
        # If no image data is found in the database, create an empty image
        image_width = 150
        image_height = 150
        color = (192, 192, 192)  # gray color
        blank_image = Image.new("RGB", (image_width, image_height), color)
        img_io = BytesIO()
        blank_image.save(img_io, format='PNG')  # Save as PNG or any desired format
        img_io.seek(0)
        self.foo(img_io)
    
    # search in treeview application 
    def search_records(self):
        self.search_query = self.search_entry.get().lower()  # Get the search query from the entry field
        failed_results = []
        
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if any(self.search_query in str(value).lower() for value in values):
                self.tree.selection_add(item)
            else:
                failed_results.append(item)
                self.tree.selection_remove(item)
        
        return failed_results
    # return to the originalresult in treeview application
    '''def return_to_original(self):
        self.search_entry.delete(0, tk.END)  # Clear the search entry
        for item in self.tree.get_children():
            self.tree.selection_add(item)'''
    def return_to_original(self):
        self.search_entry.delete(0, tk.END)  # Clear the search entry
        # Store the selected items before search
        self.selected_before_search = set()
        self.original_items = set(self.tree.get_children())
        # Clear current selection and add previously selected items
        self.tree.selection_clear()
        for item in self.selected_before_search:
            self.tree.selection_add(item)
        
        # Remove any extra items added during search
        for item in self.tree.get_children():
            if item not in self.original_items:
                self.tree.delete(item)
        self.fetchall_app()
   
################################################### controle cavas #################################################################    
    def foo(self,fun):
        self.img = Image.open(fun)
        #Resize the Image using resize method
        self.resized_image= self.img.resize((150,150), Image.LANCZOS)
        self.new_image= ImageTk.PhotoImage(self.resized_image)
        self.canvas.create_image(150,150, anchor=SE, image=self.new_image)
        self.canvas.image = self.new_image
        

    def select_file_app(self):
        filetypes = (
            ('photo ', '*.png'),
            ('photo ', '*.jpg'),
            ('photo ', '*.jpeg'),
            ('All files', '*.*')
            )

        self.filename = fd.askopenfilename(
            title='Open a file',
            initialdir='~/application/',
            filetypes=filetypes)
        if self.filename :
            ms.showinfo(
                title='Selected File',
                message=self.filename
            )
        #filename.seek(0, os.SEEK_END)
        #if self.filename :
            
            self.foo(self.filename)
            return self.filename
        else:
            ms.showwarning("Warning", "Has not shouse image !! ")
######################################################################################################################################
######################################################## controle cavase 2 ###########################################################
    def foo1(self,fun1):
        self.img1 = Image.open(fun1)
        #Resize the Image using resize method
        self.resized_image1= self.img1.resize((150,150), Image.LANCZOS)
        self.new_image1= ImageTk.PhotoImage(self.resized_image1)
        self.canvas2.create_image(150,150, anchor=SE, image=self.new_image1)
        self.canvas2.image = self.new_image1
    

    def selecte_file_person(self):
        filetypes = (
            ('photo ', '*.png'),
            ('photo ', '*.jpg'),
            ('photo ', '*.jpeg'),
            ('All files', '*.*')
            )

        self.filename1 = fd.askopenfilename(
            title='Open a file',
            initialdir='~/application/',
            filetypes=filetypes)
        if self.filename1 :
            ms.showinfo(
                title='Selected File',
                message=self.filename1
            )
        #filename.seek(0, os.SEEK_END)
        #if self.filename :

            self.foo1(self.filename1)
            return self.filename1
        else:
            ms.showwarning("Warning", "Has not shouse image !! ")
######################################################################################################################################
# #############################################     #################################       ####################################

# Function to sort the Treeview Application Manager by column
    def sort_treeview(self,tree, col, descending):
        data = [(tree.set(item, col), item) for item in tree.get_children('')]
        data.sort(reverse=descending)
        for index, (val, item) in enumerate(data):
            tree.move(item, '', index)
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not descending))

# Function to sort the Treeview Application Manager by column
    def sort_treeview1(self,treee, col, descending):
        data = [(treee.set(item, col), item) for item in treee.get_children('')]
        data.sort(reverse=descending)
        for index, (val, item) in enumerate(data):
            treee.move(item, '', index)
        treee.heading(col, command=lambda: self.sort_treeview1(treee, col, not descending))
        
######################################################################################################################################    
    def widgets(self):
        self.login_page = CTkFrame(self.windows,width=300, height=300,corner_radius=10)
        self.username_entry = CTkEntry(self.login_page,placeholder_text="Username",justify="center",corner_radius=10)
        self.password_entry = CTkEntry(self.login_page,placeholder_text="Password",show="•",justify="center",corner_radius=10)
        self.login_button = CTkButton(self.login_page, text="Login",hover_color="#F49000", command=self.login)
        self.shpw_passwd_button = CTkButton(self.login_page, text="Show password",hover_color="#FA520D", command=self.show_passwd)
        self.regiter_button = CTkButton(self.login_page, text="Register",hover_color="#FA520D",command=self.regestration)
        #login_button.bind("<Enter>", login)
        #login_button.bind("<Leave>", login)
        # to use enter to login and add variable (a=none ) to work
        self.username_entry.bind("<Return>", self.login)
        self.username_entry.bind("<KP_Enter>", self.login)
        self.password_entry.bind("<Return>", self.login)
        self.password_entry.bind("<KP_Enter>", self.login)
        self.error_label = CTkLabel(self.login_page ,text='',text_color="#FA120D",font=("",20,"bold"),anchor=CENTER)
        #username_label.grid(row=0,column=0)
        self.username_entry.grid(row=0, column=0, padx=5, pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.username_entry.grid_rowconfigure(0, weight=2)
        self.username_entry.grid_propagate(0)
        self.username_entry.update()
        #password_label.grid(row=1,column=0)
        self.password_entry.grid(row=2,column=0, padx=5 ,pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.login_button.grid(row=6,column=0,padx=5 ,pady=(20,0),rowspan=2)
        self.shpw_passwd_button.grid(row=6,column=1,padx=5,pady=(20,0),rowspan=2)
        self.regiter_button.grid(row=6,column=2,padx=5,pady=(20,0))
        
        db = sqlite3.connect("manageapp.db")
        cursor = db.cursor()           
        self.find_user = "select username,password from account "
        cursor.execute(self.find_user)
        resultt = cursor.fetchone()
        #print(resultt)
        # hna
        if resultt:
            # disable regestration button
            self.regiter_button.configure(state="disabled")
        
        self.error_label.grid(row=4,column=0,padx=5 ,pady=(20,0),columnspan=3)
        self.login_page.place(relx=.5, rely=.5 ,anchor=CENTER)

#############################################################################################################################################################

#############################################################################################################################################################
        self.regitration_page = CTkFrame(self.windows,width=300, height=300,corner_radius=10)
        
        self.reusername_entry = CTkEntry(self.regitration_page,placeholder_text="Username",justify="center",corner_radius=10)
        self.repassword_entry = CTkEntry(self.regitration_page,placeholder_text="Password",show="•",justify="center",corner_radius=10)
        self.repassword_entry1 = CTkEntry(self.regitration_page,placeholder_text="Password 1",show="•",justify="center",corner_radius=10)
        self.reemail_entry = CTkEntry(self.regitration_page,placeholder_text="Example@gmail.com",justify="center",corner_radius=10)
        self.reusername_entry.bind("<Return>", self.submit)
        self.repassword_entry.bind("<Return>", self.submit)
        self.repassword_entry1.bind("<Return>", self.submit)
        self.reemail_entry.bind("<Return>", self.submit)
        self.error_label1 = CTkLabel(self.regitration_page ,text='')

        self.submit_button = CTkButton(self.regitration_page, text="Submit",hover_color="#F49000", command=self.submit)
        self.shpw_passwd_button1 = CTkButton(self.regitration_page, text="Show password",hover_color="#FA520D", command=self.reshow_repassword)
        self.gotologin_button = CTkButton(self.regitration_page, text="Go to login",hover_color="#FA520D",command=self.go_to_login)

        #username_label.grid(row=0,column=0)
        self.reusername_entry.grid(row=0, column=0, padx=5, pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.reusername_entry.grid_rowconfigure(0, weight=2)
        self.reusername_entry.grid_propagate(0)
        self.reusername_entry.update()
        #password_label.grid(row=1,column=0)
        self.repassword_entry.grid(row=2,column=0, padx=5 ,pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.repassword_entry1.grid(row=5,column=0, padx=5 ,pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.reemail_entry.grid(row=8,column=0, padx=5 ,pady=(20,0),columnspan=3,rowspan=2,ipadx=100,sticky="WENS")
        self.submit_button.grid(row=10,column=0,padx=5 ,pady=(20,0),rowspan=2)
        self.shpw_passwd_button1.grid(row=10,column=1,padx=5,pady=(20,0),rowspan=2)
        self.gotologin_button.grid(row=10,column=2,padx=5,pady=(20,0))
        self.error_label1.grid(row=10,column=0,padx=5 ,pady=(20,0),columnspan=2,rowspan=2)
################################################################################################################################################################

################################################ MAIN PAGE #####################################################################################################
        self.windows_frame = CTkFrame(self.windows,width=1095, height=605,corner_radius=10)
        
        ####################################### add dashboard



        # create tabview width=1095,height=615 sticky="nsew"
        tabview = CTkTabview(self.windows_frame,width=1095,height=615)
        tabview.grid(row=1, column=0, padx=(50, 50), pady=(0, 0), sticky=NSEW)
        tabview.add("Dashboard")
        tabview.add("Application Manager")
        tabview.add("Person Info")
        tabview.add("Manage Users")
        tabview.add("Registered User")
        tabview.tab("Dashboard").grid_columnconfigure(2, weight=1)  # configure grid of individual tabs
        tabview.tab("Person Info").grid_columnconfigure(2, weight=1)
        tabview.tab("Registered User").grid_columnconfigure(2, weight=1)
        #tabview.tab("treeview Users").grid_columnconfigure(2,weight=1)
        x = [1,2,3,4,5,6,7,8,9]
        y = [9,8,7,6,5,4,3,2,1]

        co = ['#FF6D60','#F7D060','#F3E99F','#98D8AA']

        fig, axes = plt.subplots(2,2 ,figsize=(11,5.6))
        fig.patch.set_facecolor('#F2F2F2')
        axes[0][0].bar(x,y,color=co)
        axes[0][0].set_ylabel('count',weight='semibold',fontname='calibri',size=14)
        axes[0][0].set_xlabel('Programming Language')
        axes[0][0].tick_params(labelrotation=80,labelsize=11)
        axes[0][0].patch.set_facecolor('#F2F2F2')
        axes[0][0].grid(color='#5cc6e3',alpha=0.5,linestyle='--')
        axes[0][0].spines['bottom'].set_color('black')
        axes[0][0].spines['left'].set_color('black')
        axes[0][0].spines['top'].set_visible(False)
        axes[0][0].spines['right'].set_visible(False)
        axes[0][0].axhline(len(x)/2, color="black", linestyle="--")
        ## axes[0][1]
        axes[0][1].pie(x,labels=y,autopct='%1.1f%%',colors=co,explode=[0.04 for i  in range(len(x))])
        axes[0][1].legend(bbox_to_anchor = (0.5, 0.4, 0.9, 0.7),loc ='right', labels=x)
        # axes [1][0]
        axes[1][0].scatter(x,y)
        axes[1][0].set_ylabel('count',weight='semibold',fontname='calibri',size=20)
        axes[1][0].set_xlabel('Programming Language')
        axes[1][0].tick_params(labelrotation=80,labelsize=11)
        axes[1][0].grid()
        #axes[1][1]
        axes[1][1].plot(x,y)
        axes[1][1].set_ylabel('count',weight='semibold',fontname='calibri',size=20)
        axes[1][1].set_xlabel('Programming Language')
        axes[1][1].tick_params(labelrotation=80,labelsize=15)


        plt.suptitle('programming language Distribution of users',weight='bold',fontname='calibri',size=20)
        plt.tight_layout()
        #plt.show()

        dash = CTkFrame(tabview.tab("Dashboard"))
        canvas1 = FigureCanvasTkAgg(fig, dash)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="top", fill="both", expand=True)
        dash.pack()

####################################################################################################
        # add Some Style
        self.style = ttk.Style()
        # Pick A Theme
        self.style.theme_use('default')
        # Configure the Treeview Colors
        self.style.configure("Treeview", background="#D3D3D3",foreground="black",rowheight=20,fieldbackground="#D3D3D3")

        # Change Selected Color
        self.style.map('Treeview',background=[('selected',"#147083")])
        # define columns
        self.columns = ('application_name', 'user_application', 'password_application','exipred_date','email_application','creation_date','note_application','location_application', 'link_of_application')

        self.tree = ttk.Treeview(tabview.tab("Application Manager"), columns=self.columns, show='headings',height=26)
        # Configure column headings and sorting functionality
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.tree, c, False))
            self.tree.column(col)

        # define headings
        self.tree.heading('application_name', text='Application name')
        self.tree.heading('user_application', text='User in application')
        self.tree.heading('password_application', text='Password in application')
        self.tree.heading('exipred_date', text='Expired date')
        self.tree.heading('email_application', text='Email in application')
        self.tree.heading('creation_date', text='Creation date')
        self.tree.heading('note_application', text='Note of application')
        self.tree.heading('location_application', text='Location of application')
        self.tree.heading('link_of_application', text='URL of application')

        self.tree.column('application_name', width=130,stretch=False)
        self.tree.column('user_application', width=100,stretch=False)
        self.tree.column('password_application', width=130,stretch=False)
        self.tree.column('exipred_date', width=130,stretch=False)
        self.tree.column('email_application', width=130,stretch=False)
        self.tree.column('creation_date', width=100,stretch=False)
        self.tree.column('note_application', width=130,stretch=False)
        self.tree.column('location_application', width=130,stretch=False)
        self.tree.column('link_of_application', width=130,stretch=False)
                # Create Striped Row Tags
        self.tree.tag_configure('oddrow',background="white")
        self.tree.tag_configure('evenrow',background="lightblue")

        """ # generate sample data
        contacts = []
        for n in range(1, 10):
            contacts.append((f'name app {n}', f'user app {n}', f'password app {n}', datetime.now() ,f'emailapp{n}@example.com', f'note app{n}', f'location app{n}', f'url of app{n}', f'url dof app{n}'))

        # add data to the treeview
        #for contact in contacts:
        #    tree.insert('', tk.END, values=contact)
        # add counter 
        global cnt 
        self.cnt = 0

        # add data to the treeview
        for contact in contacts:
            if self.cnt % 2 == 0:
                self.tree.insert('', tk.END, values=contact,text="",tags=('evenrow',))
            else:
                self.tree.insert('', tk.END, values=contact,text="",tags=('oddrow',))
            self.cnt += 1 """

        def item_selected(event):
            for selected_item in self.tree.selection():
                item = self.tree.item(selected_item)
                global record
                record = item['values']
                # show a message
                ms.showinfo(title='Information', message=','.join(record))
                self.application_name.delete(0, END)
                self.application_name.insert(0,record[0])
                self.user_application.delete(0, END)
                self.user_application.insert(0, record[1])
                self.password_application.delete(0, END)
                self.password_application.insert(0, record[2])
                self.email_application.delete(0, END)
                self.email_application.insert(0, record[4])
                self.note_application.delete(0, END)
                self.note_application.insert(0, record[6])
                self.location_application.delete(0, END)
                self.location_application.insert(0, record[7])
                self.LINK_of_application.delete(0, END)
                self.LINK_of_application.insert(0, record[8])
                db = sqlite3.connect("manageapp.db")
                c =  db.cursor()
                self.find_infouserappphoto = """
                SELECT  photo from infoapplication where nameapp = ?
                """
                c.execute(self.find_infouserappphoto,(record[0],))
                global result_bind
                self.result_bind = c.fetchone()
                if self.result_bind[0] != None:
                    self.foo(BytesIO(self.result_bind[0]))
                else:
                    #print(self.result_bind[0])
                    # If no image data is found in the database, create an empty image
                    image_width = 150
                    image_height = 150
                    color = (192, 192, 192)  # gray color
                    blank_image = Image.new("RGB", (image_width, image_height), color)
                    img_io = BytesIO()
                    blank_image.save(img_io, format='PNG')  # Save as PNG or any desired format
                    img_io.seek(0)
                    self.foo(img_io)
                db.commit()
                db.close()




        self.tree.bind('<<TreeviewSelect>>', item_selected)

        self.tree.grid(row=0, column=0, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(tabview.tab("Application Manager"), orient=tk.VERTICAL, command=self.tree.yview)

        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.scrollbar.config(command=self.tree.yview)

        self.scrollbar1 = ttk.Scrollbar(tabview.tab("Application Manager"), orient=tk.HORIZONTAL, command=self.tree.xview)
        self.scrollbar1.grid(row=1, column=0,sticky='nsew')
        self.scrollbar1.config(command=self.tree.xview)

        self.tree.configure(yscrollcommand=self.scrollbar.set,xscrollcommand=self.scrollbar1.set)

####################################################################################################
####################################################################################################

                # define columns
        columnss = ('first_name', 'last_name', 'emailp','division_orr_service','date_now','location_application', 'link_ofapplication')

        treee = ttk.Treeview(tabview.tab("Person Info"), columns=columnss,show="headings",height=26,selectmode="extended")
        # Configure column headings and sorting functionality
        for col in columnss:
            treee.heading(col, text=col, command=lambda c=col: self.sort_treeview1(treee, c, False))
            treee.column(col)
        # define headings
        treee.heading('first_name', text='First Name', anchor=CENTER)
        treee.heading('last_name', text='Last Name', anchor=CENTER)
        treee.heading('emailp', text='Email', anchor=CENTER)
        treee.heading('division_orr_service', text='Division or service', anchor=CENTER)
        treee.heading('date_now', text='date', anchor=CENTER)
        treee.heading('location_application', text='Location of application', anchor=CENTER)
        treee.heading('link_ofapplication', text='URL of application', anchor=CENTER)

        treee.column('first_name', width=80,stretch=False, anchor=CENTER)
        treee.column('last_name', width=80,stretch=False, anchor=CENTER)
        treee.column('emailp', width=180,stretch=False, anchor=CENTER)
        treee.column('division_orr_service', width=180,stretch=False, anchor=CENTER)
        treee.column('date_now', width=180,stretch=False, anchor=CENTER)
        treee.column('location_application', width=180,stretch=False, anchor=CENTER)
        treee.column('link_ofapplication', width=180,stretch=False, anchor=CENTER)
        # Create Striped Row Tags
        treee.tag_configure('oddrow',background="white")
        treee.tag_configure('evenrow',background="lightblue")

        

        # generate sample data
        contactt = []
        for b in range(1, 40):
            contactt.append((f'f name {b}', f'l name {b}', f'email{b}@example.com', f'divsion{b}/service', f'{datetime.now()}', f'location app{b}', f'url of app{b}'))

        # add data to the treeview
        #for conta in contactt:
        #    treee.insert('', tk.END, values=conta)
                
        # add counter 
        global count
        count = 0

        # add data to the treeview
        for contact in contactt:
            if count % 2 == 0:
                treee.insert('', tk.END, values=contact,text="",tags=('evenrow',))
            else:
                treee.insert('', tk.END, values=contact,text="",tags=('oddrow',))
            count += 1

        def item_selectedd(event):
            for selectedd_item in treee.selection():
                item = treee.item(selectedd_item)
                recordd = item['values']
                # show a message
                ms.showinfo(title='Information', message=','.join(recordd))
                first_name.delete(0, END)
                first_name.insert(0,recordd[0])
                last_name.delete(0, END)
                last_name.insert(0, recordd[1])
                emailp.delete(0, END)
                emailp.insert(0, recordd[2])
                division_orr_service.delete(0, END)
                division_orr_service.insert(0, recordd[3])

        treee.bind('<<TreeviewSelect>>', item_selectedd)

        treee.grid(row=0, column=0, sticky='nsew')

        # add a scrollbar
        scrolllbar = ttk.Scrollbar(tabview.tab("Person Info"), orient=tk.VERTICAL, command=treee.yview)

        scrolllbar.grid(row=0, column=1, sticky='ns')
        scrolllbar.config(command=treee.yview)

        scrolllbar1 = ttk.Scrollbar(tabview.tab("Person Info"), orient=tk.HORIZONTAL, command=treee.xview)
        scrolllbar1.grid(row=1, column=0,sticky='nsew')
        scrolllbar1.config(command=treee.xview)

        treee.configure(yscrollcommand=scrolllbar.set,xscrollcommand=scrolllbar1.set)
####################################################################################################
####################################################################################################
        """ # first and last name
        fname_label = CTkLabel(self.windows_frame,text="First Name :")
        fname_label.grid(row=0,column=0)
        fname_entry = CTkEntry(self.windows_frame,width=10)
        fname_entry.grid(row=0,column=1,padx=(20, 0), pady=(20, 0), sticky="nsew")
        lname_label = CTkLabel(self.windows_frame,text="Last Name :")
        lname_label.grid(row=0,column=2)
        lname_entry = CTkEntry(self.windows_frame,width=10)
        lname_entry.grid(row=0,column=3,padx=(20, 0), pady=(20, 0), sticky="nsew")
        #birth date
        birth_label = CTkLabel(self.windows_frame,text="Birth Date")
        birth_label.grid(row=1,column=0,padx=(20, 0), pady=(20, 0))
        birth_entry = tkcalendar.DateEntry(self.windows_frame,width=10)
        birth_entry.grid(row=1,column=1,padx=(20, 0), pady=(20, 20), sticky="nsew")
        birth_label = CTkLabel(self.windows_frame,text="Gender")
        birth_label.grid(row=2,column=0,padx=(20, 0), pady=(20, 0))
        gender = StringVar()
        gender.set("none")
        male = CTkRadioButton(self.windows_frame,text="Male",variable=gender,value="Male")
        male.grid(row=2,column=1,padx=(20, 0), pady=(20, 0) )
        female = CTkRadioButton(self.windows_frame,text="Female",variable=gender,value="Female")
        female.grid(row=2,column=2,padx=(20, 0), pady=(20, 0) )
        #country
        country_label = CTkLabel(self.windows_frame,text="Country")
        country_label.grid(row=3,column=0,padx=(20, 0), pady=(20, 0) )
        country_choices = ttk.Combobox(self.windows_frame,width=20, values=["Maroc","Algirie","Syria","Egypt","UAE","KSA"] ,state="readonly")
        country_choices.grid(row=3,column=1,padx=(20, 0), pady=(20, 20), sticky="nsew")
        # address
        address_label = CTkLabel(self.windows_frame,text="Address")
        address_label.grid(row=4,column=0,padx=(20, 0), pady=(20, 0) )
        text_entry = CTkTextbox(self.windows_frame,width=50,height=20)
        text_entry.grid(row=4,column=1,padx=(20, 0), pady=(20, 20), sticky="nsew") """

################################################################################################################################################################
        self.info_fram = CTkFrame(tabview.tab("Application Manager"),width=400, height=615,corner_radius=10)
        
        self.application_name = CTkEntry(self.info_fram,placeholder_text="application name",justify="center",corner_radius=10)
        self.application_name.grid(row=1,column=0,padx=2,pady=5)
        self.user_application = CTkEntry(self.info_fram,placeholder_text="user application",justify="center",corner_radius=10)
        self.user_application.grid(row=2,column=0,padx=2,pady=5)
        self.password_application = CTkEntry(self.info_fram,placeholder_text="password application",justify="center",corner_radius=10)
        self.password_application.grid(row=3,column=0,padx=2,pady=5)
        self.email_application = CTkEntry(self.info_fram,placeholder_text="email application",justify="center",corner_radius=10)
        self.email_application.grid(row=4,column=0,padx=2,pady=5)
        self.note_application = CTkEntry(self.info_fram,placeholder_text="note application",justify="center",corner_radius=10)
        self.note_application.grid(row=5,column=0,padx=2,pady=5)
        self.location_application = CTkEntry(self.info_fram,placeholder_text="location application",justify="center",corner_radius=10)
        self.location_application.grid(row=6,column=0,padx=2,pady=5)
        self.LINK_of_application = CTkEntry(self.info_fram,placeholder_text="IP / LINK of application",justify="center",corner_radius=10)
        self.LINK_of_application.grid(row=7,column=0,padx=2,pady=5)
        CTkButton(self.info_fram, text="Export Selected Records", command=self.export_selectedtree).grid(row=8,column=0,padx=2,pady=5)
        CTkButton(self.info_fram, text="Export All Records", command=self.export_alltree).grid(row=9,column=0,padx=2,pady=5)
        #photoapp = CTkEntry(self.info_fram,placeholder_text="photo",justify="center",corner_radius=10)
        #photoapp.grid(row=7,column=0,padx=10,pady=9)
        #person_info = CTkLabel(self.info_fram,text="person info",font=('calibri',14),width=230,height=10,bg_color="transparent",anchor=CENTER)
        #person_info.grid(row=8,column=0)
        #first_name = CTkEntry(self.info_fram,placeholder_text="first name",justify="center",corner_radius=10)
        #first_name.grid(row=9,column=0,padx=10,pady=9)
        #last_name = CTkEntry(self.info_fram,placeholder_text="last name",justify="center",corner_radius=10)
        #last_name.grid(row=10,column=0,padx=10,pady=9)
        #emailp = CTkEntry(self.info_fram,placeholder_text="email",justify="center",corner_radius=10)
        #emailp.grid(row=11,column=0,padx=10,pady=9)
        #phonep = CTkEntry(self.info_fram,placeholder_text="phone",justify="center",corner_radius=10)
        #phonep.grid(row=12,column=0,padx=10,pady=9)
        #division_orr_service = CTkEntry(self.info_fram,placeholder_text="division or service",justify="center",corner_radius=13)
        #division_orr_service.grid(row=12,column=0,padx=10,pady=9)
        #photop = CTkEntry(self.info_fram,placeholder_text="photo",justify="center",corner_radius=10)
        #photop.grid(row=15,column=0,padx=10,pady=9)
        
############################################################# cavas ################################################################
        self.canvas = tk.Canvas(self.info_fram,width=150, height=150,bg="#D3D3D3")
        self.canvas.grid(row=0,column=0,sticky=NW,padx=10,pady=9)
####################################################################################################################################
        self.info_fram1 = CTkFrame(tabview.tab("Person Info"),width=400, height=615,corner_radius=10)
        
        self.canvas2 = tk.Canvas(self.info_fram1,width=150, height=150)
        self.canvas2.grid(row=0,column=0,sticky=NW,padx=10,pady=9)
        
        #person_info = CTkLabel(self.info_fram1,text="person info",font=('calibri',14),width=230,height=10,bg_color="transparent",anchor=CENTER)
        #person_info.grid(row=2,column=0)
        first_name = CTkEntry(self.info_fram1,placeholder_text="first name",justify="center",corner_radius=10)
        first_name.grid(row=1,column=0,padx=10,pady=9)
        last_name = CTkEntry(self.info_fram1,placeholder_text="last name",justify="center",corner_radius=10)
        last_name.grid(row=2,column=0,padx=10,pady=9)
        emailp = CTkEntry(self.info_fram1,placeholder_text="email",justify="center",corner_radius=10)
        emailp.grid(row=3,column=0,padx=10,pady=9)
        #phonep = CTkEntry(self.info_fram1,placeholder_text="phone",justify="center",corner_radius=10)
        #phonep.grid(row=4,column=0,padx=10,pady=9)
        division_orr_service = CTkEntry(self.info_fram1,placeholder_text="division or service",justify="center",corner_radius=13)
        division_orr_service.grid(row=4,column=0,padx=10,pady=9)
        
        #photop = CTkEntry(self.info_fram,placeholder_text="photo",justify="center",corner_radius=10)
        #photop.grid(row=15,column=0,padx=10,pady=9)
####################################################################################################################################
        self.button_fram = CTkFrame(tabview.tab("Application Manager"),width=1200, height=61,corner_radius=10)
        CTkButton(self.button_fram, text="Add",hover_color="#58D68D",command=self.add_recordtree).grid(row=0,column=0,padx=5,pady=10)
        CTkButton(self.button_fram, text="update",hover_color="#889000",command=self.update_recordtree).grid(row=0,column=1,padx=5,pady=10)
        CTkButton(self.button_fram, text="delete",hover_color="#CB4335",command=self.delete_recordtree).grid(row=0,column=2,padx=5,pady=10)
        CTkButton(self.button_fram, text="clear",hover_color="#5DADE2",command=self.cleartree).grid(row=0,column=3,padx=5,pady=10)
        CTkButton(self.button_fram, text="show password",hover_color="#34495E").grid(row=0,column=5,padx=5,pady=10)
        CTkButton(self.button_fram, text="Delete Multi recored",hover_color="#CB4035",command=self.delete_recordstree).grid(row=0,column=6,padx=5,pady=10)
        CTkButton(self.button_fram, text="Delete All recored",hover_color="#CB4035",command=self.delete_all_recordstree).grid(row=0,column=7,padx=5,pady=10)
        CTkButton(self.button_fram, text="photo application",hover_color="#34155E",command=self.select_file_app).grid(row=0,column=8,padx=5,pady=10)
        #CTkButton(self.button_fram, text="photo person",hover_color="#29005E",command=self.selecte_file).grid(row=0,column=7,padx=5,pady=10)
        
        # buttun manage application treeview 
        self.button_fram1 = CTkFrame(tabview.tab("Person Info"),width=1200, height=61,corner_radius=10)
        CTkButton(self.button_fram1, text="Add",hover_color="#58D68D").grid(row=0,column=0,padx=5,pady=10)
        CTkButton(self.button_fram1, text="update",hover_color="#889000").grid(row=0,column=1,padx=5,pady=10)
        CTkButton(self.button_fram1, text="Delete",hover_color="#CB4335").grid(row=0,column=2,padx=5,pady=10)
        CTkButton(self.button_fram1, text="clear",hover_color="#5DADE2").grid(row=0,column=3,padx=5,pady=10)
        CTkButton(self.button_fram1, text="show password",hover_color="#34495E").grid(row=0,column=5,padx=5,pady=10)
        CTkButton(self.button_fram1, text="Delete Multi recored",hover_color="#CB4035").grid(row=0,column=6,padx=5,pady=10)
        CTkButton(self.button_fram1, text="Delete All recored",hover_color="#CB4035").grid(row=0,column=7,padx=5,pady=10)
        CTkButton(self.button_fram1, text="photo person",hover_color="#29005E",command=self.selecte_file_person).grid(row=0,column=8,padx=5,pady=10)
                        


        #self.button_system = self.button_fram = CTkFrame(self.windows,width=50, height=50,corner_radius=10)
        #self.appearance(self.button_system)
###############################################################################################################################
        self.search_fram = CTkFrame(self.windows,corner_radius=10)
        #self.combobox_var = StringVar(value="option 2")
        CTkLabel(self.search_fram,text="                                                ",fg_color="transparent").grid(row=0,column=0,padx=5)
        self.search_entry =  CTkEntry(self.search_fram,placeholder_text="Search ...",justify="center",corner_radius=10)
        self.search_entry.grid(row=0,column=1,padx=10,pady=5,ipadx=220)
        self.combobox = CTkOptionMenu(self.search_fram,values=["option 1", "option 2","option 3","option 4"],command=self.optionmenu_callback)
        self.combobox.grid(row=0,column=2,padx=8,pady=5,sticky=NSEW)
        CTkButton(self.search_fram,text="Search",command=self.search_records).grid(row=0,column=3,padx=5,pady=5,sticky=E)
        CTkButton(self.search_fram, text="fetch all",hover_color="#34495E",command=self.return_to_original).grid(row=0,column=4,padx=5,pady=5)
        CTkButton(self.search_fram,text="logout",command=self.logout).grid(row=0,column=5,padx=5,pady=5,sticky=E)

        
        

    
        
###############################################################################################################################
        
if  __name__ == '__main__':
    screen = CTk()
    screen.title('Password Manager')
    screen.geometry(f"{1300}x{650}+{150}+{10}")
    App(screen)
    screen.mainloop()
# End timer
end_time = time.perf_counter()

# Calculate elapsed time
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time)
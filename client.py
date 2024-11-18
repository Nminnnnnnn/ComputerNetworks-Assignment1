import os
import json
import shutil

import socket
import threading

from Base import Base, get_current_IP_address
from db_queries import *

import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
from tkinter import simpledialog
import tkinter.ttk as ttk
import customtkinter

FORMAT = "utf-8"
BUFFER_SIZE = 2048
OFFSET = 10000

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

# popup notification
def display_noti(title, content):
    tkinter.messagebox.showinfo(title, content)

class BaseClientUI(tk.Tk):
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.chatroom_textCons = None

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, RegisterPage, LoginPage, RepoPage):
            frame = F(parent=container, controller=self)
            # initializing frame of that object from
            # StartPage, RegisterPage, LoginPage and RepoPage respectively with for loop
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(bg='white')
        self.show_frame(StartPage)

    # to display the current frame passed as parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # set color mode
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")
        # create title
        self.page_title = customtkinter.CTkLabel(self, text="File Sharing Application", font=("Arial Bold", 50))
        self.page_title.pack(padx=10, pady=(70,50))
        
        # set port entry
        self.port_entry = customtkinter.CTkEntry(self, 
                                                placeholder_text=" Enter port number here... ", 
                                                border_width=1,
                                                width=300,
                                                height=50,
                                                font=("Roboto", 15, 'italic')
                                                )
        self.port_entry.pack(padx=10, pady=10)
        # create user manual 
        self.page_title = customtkinter.CTkLabel(self, 
                                                 text=" Enter your port number [1024, 65535] before \"Log in\" or \"Register\"!", 
                                                 font=("Segoe UI", 17, "italic"))
        self.page_title.pack(padx=10, pady=(10,20))
        # create a login button
        self.login_button = customtkinter.CTkButton(self, 
                                                    text="Log In", 
                                                    font=("Roboto", 20),
                                                    command=lambda: self.enter_app(controller=controller, port=self.port_entry.get(), page=LoginPage),
                                                    text_color="#0B6A9F",
                                                    fg_color="#BFE3FE", 
                                                    hover_color="#46A2E7", 
                                                    width=200,
                                                    height=50,
                                                    corner_radius=10
                                                    )
        self.login_button.pack(padx=10, pady=10)
        #
        account_prompt_label = customtkinter.CTkLabel(self, 
                                              text="Or you don't have an account yet?",
                                              font=("Roboto", 13, "italic")) 
        account_prompt_label.pack(padx=10, pady=(10, 0))
        # create a register button
        self.register_button = customtkinter.CTkButton( self,
                                                        text="Register", 
                                                        font=("Roboto", 20),
                                                        command=lambda: self.enter_app(controller=controller, port=self.port_entry.get(), page=RegisterPage),
                                                        text_color="#0B6A9F",
                                                        fg_color="#BFE3FE", 
                                                        hover_color="#46A2E7", 
                                                        width=200,
                                                        height=50,
                                                        corner_radius=10
                                                    )
        self.register_button.pack(padx=10, pady=10)
    
    def enter_app(self, controller, port, page):
        try:
            # Init server
            global peer 
            peer = Client(clientport=int(port))
           
            # Create a (daemon) child thread for receiving message
            recv_t = threading.Thread(target=peer.input_recv)
            # When this thread starts to run, it also calls input_recv
            recv_t.daemon = True
            recv_t.start()

            # Create a (daemon) child thread for receiving file
            recv_file_t = threading.Thread(target=peer.recv_file_content)
            # When this thread starts to run, it also calls input_recv
            recv_file_t.daemon = True
            recv_file_t.start()
            
            # Those 2 above threads are daemon threads, they will be terminated 
            # when program is terminated.
            
            # Move to another page: LoginPage or RegisterPage
            controller.show_frame(page)
        except:
            self.port_entry.delete(0, customtkinter.END)
            tkinter.messagebox.showinfo("Port Error!",  "The port is already in use or contains an empty value")
class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")   

        self.frame = customtkinter.CTkFrame(master=self, fg_color="white")
        self.frame.pack(fill='both', expand=True)

        # Configure grid layout
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(7, weight=1)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Register", font=("Arial Bold", 45))
        self.title_label.grid(row=1, column=1, columnspan=2, pady=(40, 20), padx=10)

        # Create Username label and entry
        self.username = customtkinter.CTkLabel(
                                            self.frame,
                                            text="Username:",
                                            font=("Roboto", 20)
                                            )
        self.username.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.username_entry = customtkinter.CTkEntry(
                                            self.frame, 
                                            placeholder_text=" Enter your username here... ", 
                                            font=("Roboto", 15, 'italic'),
                                            width=300,
                                            height=50
                                            )
        self.username_entry.grid(row=2, column=2, padx=10, pady=10)

        # Create Password label and entry
        self.password = customtkinter.CTkLabel(
                                            self.frame,
                                            text="Password:",
                                            font=("Roboto", 20))
        self.password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.password_entry = customtkinter.CTkEntry(
                                            self.frame, 
                                            placeholder_text=" Enter your password here... ", 
                                            font=("Roboto", 15, 'italic'), 
                                            show='*',
                                            width=300,
                                            height=50
                                            )
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        # Submit button
        customtkinter.CTkButton(self.frame, 
                                text='Register',
                                command=lambda: self.register_user(self.username_entry.get(), self.password_entry.get()),
                                font=('Roboto',20,),
                                text_color="#0B6A9F",
                                fg_color="#BFE3FE", 
                                hover_color="#46A2E7", 
                                width=200,
                                height=50,
                                corner_radius=10
                                ).grid(row=4, column=1, columnspan=2, pady=20)

# Link to login page
        customtkinter.CTkLabel(
                            self.frame, 
                            text="Or you already have an account?", 
                            font=("Roboto", 15, 'italic')
                            ).grid(row=5, column=1, columnspan=2, pady=10, padx=10)
        customtkinter.CTkButton(self.frame, 
                                text='Log in', 
                                command=lambda: controller.show_frame(LoginPage),
                                font=('Roboto',20),
                                text_color="#0B6A9F",
                                fg_color="#BFE3FE", 
                                hover_color="#46A2E7", 
                                width=200,
                                height=50,
                                corner_radius=10
                                ).grid(row=6, column=1, columnspan=2, pady=10, padx=10)

    def register_user(self, username, password):
        peer.name = str(username)
        peer.password = str(password) # without hashing
        # delete content of Username and Password entries
        self.username_entry.delete(0, customtkinter.END)
        self.password_entry.delete(0, customtkinter.END)
        
        peer.send_register()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")   

        self.frame = customtkinter.CTkFrame(master=self, fg_color="white")
        self.frame.pack(fill='both', expand=True)

        # Configure grid layout
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(7, weight=1)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Log in", font=("Arial Bold", 45))
        self.title_label.grid(row=1, column=1, columnspan=2, pady=(40, 20), padx=10)

        # Create Username label and entry
        self.username = customtkinter.CTkLabel(
                                            self.frame,
                                            text="Username:",
                                            font=("Roboto", 20)
                                            )
        self.username.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.username_entry = customtkinter.CTkEntry(
                                            self.frame, 
                                            placeholder_text=" Enter your username here... ", 
                                            font=("Roboto", 15, 'italic'),
                                            width=300,
                                            height=50
                                            )
        self.username_entry.grid(row=2, column=2, padx=10, pady=10)

        # Create Password label and entry
        self.password = customtkinter.CTkLabel(
                                            self.frame,
                                            text="Password:",
                                            font=("Roboto", 20))
        self.password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.password_entry = customtkinter.CTkEntry(
                                            self.frame, 
                                            placeholder_text=" Enter your password here... ", 
                                            font=("Roboto", 15, 'italic'), 
                                            show='*',
                                            width=300,
                                            height=50
                                            )
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        # self.login_user(command=lambda: username=self.username_entry.get(), password=self.password_entry.get())).pack(pady=(0, 10),padx=10)
        # command=lambda: controller.show_frame(RegisterPage)
        # Submit button
        customtkinter.CTkButton(self.frame, 
                                text='Login',
                                command=lambda: self.login_user(username=self.username_entry.get(), password=self.password_entry.get()),
                                font=('Roboto',20,),
                                text_color="#0B6A9F",
                                fg_color="#BFE3FE", 
                                hover_color="#46A2E7", 
                                width=200,
                                height=50,
                                corner_radius=10
                                ).grid(row=4, column=1, columnspan=2, pady=20)

        # Link to register page
        customtkinter.CTkLabel(
                            self.frame, 
                            text="Or you don't have account yet?", 
                            font=("Roboto", 15, 'italic')
                            ).grid(row=5, column=1, columnspan=2, pady=10, padx=10)
        customtkinter.CTkButton(self.frame, 
                                text='Register', 
                                command=lambda: controller.show_frame(RegisterPage),
                                font=('Roboto',20),
                                text_color="#0B6A9F",
                                fg_color="#BFE3FE", 
                                hover_color="#46A2E7", 
                                width=200,
                                height=50,
                                corner_radius=10
                                ).grid(row=6, column=1, columnspan=2, pady=10, padx=10)
        
    def login_user(self, username, password):
        peer.name = str(username)
        peer.password = str(password) # without hashing
        
        self.username_entry.delete(0, customtkinter.END)
        self.password_entry.delete(0, customtkinter.END)
        
        peer.send_login()

class RepoPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        
        # configure grid layout 
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((1, 2), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # create sidebar frame with widgets
        # start of sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        # create logo
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Peer", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text="Quit", 
                                                      command=lambda: self.quit_user())
        self.sidebar_button.grid(row=1, column=0, padx=20, pady=10)

        # sidebar buttons
        # Log out button
        self.logout_button = customtkinter.CTkButton(self.sidebar_frame, text="Log Out", 
                                                     command=lambda: self.logout_user())
        self.logout_button.grid(row=2, column=0, padx=20, pady=10)
        
        # change appearance mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, 
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event
                                                                       )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        # change scaling
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        # end of sidebar

        #### create frame for repo
        self.repo_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.repo_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.repo_frame.grid_rowconfigure(0, weight=1)
        self.repo_frame.grid_columnconfigure(0, weight=1)
        # create scrollable frame for repo list
        ## to do: add file names to this frame
        self.scrollable_repo_frame = customtkinter.CTkScrollableFrame(self.repo_frame, label_text="Repository")
        self.scrollable_repo_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.scrollable_repo_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_repo_files = []
        self.fileListBox = tk.Listbox(self.scrollable_repo_frame, width=75, height=20)
        self.fileListBox.grid(row=0, column=0, padx=10, pady=(10, 10))
        for file in self.scrollable_repo_files:
            self.fileListBox.insert(tk.END, file)
        # create temp frame
        self.temp_frame = customtkinter.CTkFrame(master=self.repo_frame, fg_color="transparent")
        self.temp_frame.grid(row=2, column=0, sticky="nsew")
        self.temp_frame.grid_rowconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(1, weight=1)
        # create 'Publish File' To Repository button
        # to choose file from local repo, set name and publish it
        self.publish_button = customtkinter.CTkButton(
                                            master=self.repo_frame,
                                            text="Publish File To Repository",
                                            font=('Roboto',15),
                                            text_color="#0B6A9F",
                                            fg_color="#BFE3FE", 
                                            hover_color="#46A2E7", 
                                            width=100,
                                            height=30,
                                            command=lambda: self.choose_file_to_publish()
                                            )
        self.publish_button.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nsew")
        # create 'Delete File' button
        # to delete that file out of your repo
        self.delete_button = customtkinter.CTkButton(
                                            master=self.temp_frame,
                                            text="Delete File",
                                            font=('Roboto',15),
                                            text_color="#0B6A9F",
                                            fg_color="#BFE3FE", 
                                            hover_color="#46A2E7", 
                                            width=100,
                                            height=30,
                                            command=lambda: self.delete_file_from_repo()
                                            )
        self.delete_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        # create 'Reload Repository' button
        # to reload your repository
        self.reload_button = customtkinter.CTkButton(
                                            master=self.temp_frame, 
                                            text="Reload Repository",
                                            font=('Roboto',15),
                                            text_color="#0B6A9F",
                                            fg_color="#BFE3FE", 
                                            hover_color="#46A2E7", 
                                            width=100,
                                            height=30,
                                            command=lambda: self.reload_repo()
                                            )
        self.reload_button.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        ### create frame for peer list
        self.peer_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.peer_frame.grid(row=0, column=2, columnspan = 2, rowspan=3, sticky="nsew")
        self.peer_frame.grid_rowconfigure(0, weight=1)
        self.peer_frame.grid_columnconfigure(0, weight=1)
        # create scrollable peer list
        ## to do: add peer names to this frame
        self.scrollable_peer_frame = customtkinter.CTkScrollableFrame(self.peer_frame, label_text="Peer List")
        self.scrollable_peer_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.scrollable_peer_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_peer_names = []
        self.peerListBox = tk.Listbox(self.scrollable_peer_frame, width=75, height=20)
        self.peerListBox.grid(row=0, column=0, padx=10, pady=(10, 10))
        # create search for file
        self.search_frame = customtkinter.CTkFrame(self.peer_frame, fg_color="transparent")
        self.search_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.search_frame.grid_rowconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = customtkinter.CTkEntry(
                                            master=self.search_frame, 
                                            placeholder_text=" > Search... ",
                                            font=("Roboto",13,'italic'),
                                            height=30,
                                            width=80
                                            )
        self.search_entry.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.search_button = customtkinter.CTkButton(
                                            master=self.search_frame, 
                                            text="Search",
                                            font=("Roboto",15),
                                            text_color="#0B6A9F",
                                            fg_color="#BFE3FE", 
                                            hover_color="#46A2E7", 
                                            width=100,
                                            height=30,
                                            command=lambda: self.find_file_from_user()
                                            )
        self.search_button.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        # create send connection request button
        self.request_button = customtkinter.CTkButton(master=self.peer_frame, 
                                                    text="Send Connection Request",
                                                    font=('Roboto',15),
                                                    text_color="#0B6A9F",
                                                    fg_color="#BFE3FE", 
                                                    hover_color="#46A2E7", 
                                                    width=100,
                                                    height=30,
                                                    command=lambda:self.send_connection_request()
                                                    )
        self.request_button.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # create CLI
        self.entry = customtkinter.CTkEntry(self, 
                                            placeholder_text=" > Command... ",
                                            font=("Roboto", 15, 'italic')
                                            )
        self.entry.grid(row=4, column=1, columnspan=2, padx=(10, 10), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, 
                                                    text="Enter", 
                                                    width=100,
                                                    height=30,
                                                    font=("Roboto",15),
                                                    command=lambda:self.command_line(command = self.entry.get()),fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE")
                                                    )
        self.main_button_1.grid(row=4, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

    # log out
    def logout_user(self):
        peer.send_logout_request()
        app.show_frame(StartPage)

    # quit
    def quit_user(self):
        peer.send_logout_request()
        app.destroy()
    
    def command_line(self, command):
        parts = command.split()
        
        if parts[0] == "publish":
            if len(parts) == 3:
                file_path = parts[1]
                file_name = parts[2]
                
                peer.update_repo_to_server(file_name, file_path)
                self.fileListBox.insert(0, file_name + " [" + file_path + "]")
                self.add_to_repo(file_path)
                
            else:
                message = "Lệnh không hợp lệ vui lòng nhập lại!"
                tkinter.messagebox.showinfo(message)
                
        elif parts[0] == "fetch":
            if len(parts) == 2:
                file_name = parts[1]
                
                peer.send_listpeer(file_name)
                peer_info = self.peerListBox.get(0)
                peer.send_request(peer_info, file_name)
            else:
                message = "Lệnh không hợp lệ vui lòng nhập lại!"
                tkinter.messagebox.showinfo(message)
        else:
            message = "Lệnh không hợp lệ vui lòng nhập lại!"
            tkinter.messagebox.showinfo(message)

    # this method is to publish a file into repo
    def add_to_repo(self, file_path):
        # create a folder named "repo" in this folder
        if not os.path.exists("local-repo"):
            os.makedirs("local-repo")
        destination = os.path.join(os.getcwd(), "local-repo")
        shutil.copy2(file_path, destination)    

    # this method is to choose file from your local computer
    def choose_file_to_publish(self):
        file_path = tkinter.filedialog.askopenfilename()
        msg_box = tkinter.messagebox.askquestion('Confirmation', 'Upload "{}" to local repository?'.format(file_path),
                                                 icon="question")
        if msg_box == 'yes':
            file_name = simpledialog.askstring('Input','Choose your file name after publishing to your repository',parent = self)
            peer.update_repo_to_server(file_name, file_path)
            self.fileListBox.insert(0, file_name + "::[" + file_path + "]")
            self.add_to_repo(file_path)
            
    def send_connection_request(self):
        peer_info = self.peerListBox.get(tk.ANCHOR) 
        file_name = self.search_entry.get()
        peer.send_request(peer_info, file_name)

    def add_to_repo_from_fetch(self, file_name, file_name_server):
        file_path = os.path.join(os.getcwd(), file_name)
        if not os.path.exists("local-repo"):
            os.makedirs("local-repo")
        destination = os.path.join(os.getcwd(), "local-repo")
        shutil.copy2(file_path, destination)
        os.remove(file_path)
        peer.update_repo_to_server(file_name_server, file_path)
    def delete_file_from_repo(self):
        file_name_and_path = self.fileListBox.get(tk.ANCHOR)
        repo_file_name = file_name_and_path.split("::")[0]
        self.fileListBox.delete(tk.ANCHOR)
        
        path_name = file_name_and_path.split("::")[1][1:-1]
        actual_file_name = path_name.split("/")[-1]
        print(actual_file_name)
        
        repo_path = os.path.join(os.getcwd(), "local-repo")
        target_file = os.path.join(repo_path, actual_file_name)
        
        try:
            os.remove(target_file)
            print(f'delete {target_file} successfully!')
        except OSError as e: print(f'Error, cannot delete {target_file}')
            
        peer.delete_file_at_server(repo_file_name)

    def find_file_from_user(self):
        file_name = self.search_entry.get()
        self.peerListBox.delete(0, tk.END)
        peer.send_listpeer(file_name)

    def reload_repo(self):
        for file in self.fileListBox.get(0, tk.END):
            self.fileListBox.delete(0, tk.END)
        peer.reload_client_repo_list()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

# ------ end of GUI ------- #

class Client(Base):
    def __init__(self, clientport, server_info=(get_current_IP_address(), 65432)):
        current_IP_address = get_current_IP_address()
        super(Client, self).__init__(serverhost=current_IP_address, serverport=clientport)

        print(f"Client at {self.serverhost}:{self.serverport}")

        # init host and port of central server
        self.server_info = server_info

        # peer name
        self.name = ""
        # peer password
        self.password = ""

        # all peers it can connect (network peers)
        self.connectable_peer = {}

        # peers it has connected (friend)
        self.friendlist = {}

        self.message_format = '{peername}: {message}'
        # file buffer
        self.file_buf = []

        # define handlers for received message of network peer
        handlers = {
            'REGISTER_SUCCESS': self.register_success,
            'REGISTER_ERROR': self.register_error,
            'LOGIN_SUCCESS': self.login_success,
            'LOGIN_ERROR': self.login_error,
            'LIST_USER_SHARE_FILE': self.get_users_share_file,
            'FILE_REQUEST': self.file_request,
            'FILE_ACCEPT': self.file_accept,
            'FILE_REFUSE': self.file_refuse,
        }
        for msgtype, function in handlers.items():
            self.add_handler(msgtype, function)

    ## ==========implement protocol for user registration - network peer==========##
    def send_register(self):
        """ Send a request to server to register peer's information. """
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.serverhost,
            'port': self.serverport
        }
        self.client_send(self.server_info,
                         msgtype='PEER_REGISTER', msgdata=peer_info)

    def register_success(self, msgdata):
        """ Processing received message from server: Successful registration on the server. """
        display_noti('Register Noti', 'Đăng ký thành công')
        print('Register Successful.')

    def register_error(self, msgdata):
        """ Processing received message from server: Registration failed on the server. """
        display_noti('Register Noti',
                     'Đăng ký thất bại. Tên đăng nhập đã tồn tại hoặc không hợp lệ!')
        print('Register Error. Username existed. Login!')
    ## ===========================================================##

    ## ==========implement protocol for authentication (log in) - network peer==========##
    def send_login(self):
        """ Send a request to server to login. """
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.serverhost,
            'port': self.serverport
        }
        self.client_send(self.server_info,
                         msgtype='PEER_LOGIN', msgdata=peer_info)

    def login_success(self, msgdata):
        """ Processing received message from server: Successful login on the server. """
        print('Login Successful.')
        display_noti('Login Noti', 'Login Successful.')
        app.geometry("1100x600")
        app.resizable(False, False)
        app.show_frame(RepoPage)

    def login_error(self, msgdata):
        """ Processing received message from server: Login failed on the server. """
        display_noti('Login Noti', 'Login Error. Username not existed!')
        print('Login Error. Username not existed or wrong password')
    ## ===========================================================##

    ## ==========implement protocol for getting online user list who have file that client find==========##
    def send_listpeer(self, filename):
        """ Send a request to server to get all online peers who have file that client find. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': filename
        }
        self.client_send(self.server_info,
                         msgtype='PEER_SEARCH', msgdata=peer_info)
        
    def get_users_share_file(self, msgdata):
        shareList = msgdata['online_user_list_have_file']
        for peername, data in shareList.items():
            peer_host, peer_port = data
            info = str(peer_host) + ',' + str(peer_port)
            app.frames[RepoPage].peerListBox.insert(0, info)

    def reload_client_repo_list(self):
        fileList = get_user_file(self.name)
        pathList = get_user_path(self.name)
        for i in range(0, len(fileList)): 
            res = fileList[i] + '::[' + pathList[i] + ']'
            app.frames[RepoPage].fileListBox.insert(0, res)
    ## ===========================================================##

    ## ==========implement protocol for file request==========##
    def send_request(self, peerinfo, filename):
        """ Send a file request to an online user. """
        peerhost, peerport = peerinfo.split(',')
        peer = (peerhost, int(peerport))
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': filename
        }
        self.client_send(peer, 
                         msgtype='FILE_REQUEST', msgdata=data)

    ##=====NEED MODIFY: Hàm này dùng để hiển thị có yêu cầu chia sẻ file để người dùng chọn đồng ý hoặc không====#
    def file_request(self, msgdata):
        """ Processing received file request message from peer. """
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        filename = msgdata['filename']
        msg_box = tkinter.messagebox.askquestion('File Request', '{} - {}:{} request to take the file "{}"?'.format(peername, host, port, filename),
                                            icon="question")
        if msg_box == 'yes':
            # if request is agreed, connect to peer (add to friendlist)
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            self.client_send((host, port), msgtype='FILE_ACCEPT', msgdata=data)
            display_noti("File Request Accepted",
                         "Send The File!")
            self.friendlist[peername] = (host, port)
            destination = os.path.join(os.getcwd(), "local-repo")
            file_path = tkinter.filedialog.askopenfilename(initialdir=destination)
            file_name = os.path.basename(file_path)
            msg_box = tkinter.messagebox.askquestion('File Explorer', 'Are you sure to send {} to {}?'.format(file_name, peername),
                                                 icon="question")
            if msg_box == 'yes':
                sf_t = threading.Thread(
                    target=peer.transfer_file, args=(peername, file_path, filename))
                sf_t.daemon = True
                sf_t.start()
                tkinter.messagebox.showinfo(
                    "File Transfer", '{} has been sent to {}!'.format(file_name, peername))
            else:
                self.client_send((host, port), msgtype='FILE_REFUSE', msgdata={})

    #=======Hàm này dùng để chuyển file cho máy khách sau khi đã chọn đồng ý=======#
    def file_accept(self, msgdata):
        """ Processing received accept file request message from peer.
            Add the peer to collection of friends. """
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        display_noti("File Request Result",
                     "Accepted")
        self.friendlist[peername] = (host, port)

    def file_refuse(self, msgdata):
        """ Processing received refuse chat request message from peer. """
        display_noti("File Request Result", 'FILE REFUSED!')
    ## ===========================================================##
    
    # def recv_public_message(self, msgdata):
    #     """ Processing received public chat message from central server."""
    #     # insert messages to text box
    #     message = msgdata['name'] + ": " + msgdata['message']
    #     app.chatroom_textCons.config(state=tkinter.NORMAL)
    #     app.chatroom_textCons.insert(tkinter.END, message+"\n\n")
    #     app.chatroom_textCons.config(state=tkinter.DISABLED)
    #     app.chatroom_textCons.see(tkinter.END)
    ## ===========================================================##

    ## ==========implement protocol for file tranfering==========##
    def transfer_file(self, peer, file_path, file_name_server):
        """ Transfer a file. """
        try:
            peer_info = self.friendlist[peer]
        except KeyError:
            display_noti("File Transfer Result", 'Friend does not exist!')
        else:
            file_name = os.path.basename(file_path)
            def fileThread(filename):
                file_sent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                file_sent.connect((peer_info[0], peer_info[1]+OFFSET))

                # send filename and friendname
                fileInfo = {
                    'filename': filename,
                    'friendname': peer,
                    'filenameserver': file_name_server,
                }

                fileInfo = json.dumps(fileInfo).encode(FORMAT)
                file_sent.send(fileInfo)
                
                msg = file_sent.recv(BUFFER_SIZE).decode(FORMAT)
                print(msg)

                with open(file_path, "rb") as f:
                    while True:
                        # read the bytes from the file
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        file_sent.sendall(bytes_read)
                file_sent.shutdown(socket.SHUT_WR)
                file_sent.close()
                display_noti("File Transfer Result", 'File has been sent!')
                return
            t_sf = threading.Thread(target=fileThread,args=(file_name,))
            t_sf.daemon = True
            t_sf.start()

    def recv_file_content(self):
        """ Processing received file content from peer."""
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to our local address
        self.file_socket.bind((self.serverhost, int(self.serverport) + OFFSET))
        self.file_socket.listen(5)

        while True:
            conn, addr = self.file_socket.accept()
            buf = conn.recv(BUFFER_SIZE)
            message = buf.decode(FORMAT)

            # deserialize (json type -> python type)
            recv_file_info = json.loads(message)

            conn.send("Filename received.".encode(FORMAT))
            print(recv_file_info)

            file_name = recv_file_info['filename']
            friend_name = recv_file_info['friendname']

            with open(file_name, "wb") as f:
                while True:
                    bytes_read = conn.recv(BUFFER_SIZE)
                    if not bytes_read:    
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
            
            app.frames[RepoPage].add_to_repo_from_fetch(file_name, recv_file_info['filenameserver'])
            conn.shutdown(socket.SHUT_WR)
            conn.close()

            display_noti("File Transfer Result", 'You receive a file with name ' + file_name + ' from ' + friend_name)
    
    ## ===========================================================##
    
    ## ==========implement protocol for log out & exit ===================##

    def send_logout_request(self):
        """ Central Server deletes user out of online user list """
        peer_info = {
            'peername': self.name,
        }
        self.client_send(self.server_info,
                         msgtype='PEER_LOGOUT', msgdata=peer_info)

    ## ===========================================================##
    def delete_file_at_server(self,file_name):
        """ Delete file from server. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': file_name
        }
        self.client_send(self.server_info,
                         msgtype='DELETE_FILE', msgdata=peer_info)
        
    def update_repo_to_server(self, file_name, file_path):
        """ Upload repo to server. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': file_name,
            'filepath': file_path
        }
        self.client_send(self.server_info,
                         msgtype='FILE_REPO', msgdata=peer_info)
    
# ------ app run ---------- #
if __name__ == "__main__":
    app = BaseClientUI()
    app.title('FILE SHARING APPLICATION')
    app.geometry("1200x600")
    app.resizable(True, True)

    def handle_on_closing_event():
        if tkinter.messagebox.askokcancel("Thoát", "Bạn muốn thoát khỏi ứng dụng?"):
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", handle_on_closing_event)
    app.mainloop()



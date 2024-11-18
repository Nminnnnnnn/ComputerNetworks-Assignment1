import os
import json
import shutil
import socket
import threading
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
from tkinter import simpledialog
import tkinter.ttk as ttk
import customtkinter
from Base import Base, get_current_IP_address
from db_queries import *

FORMAT = "utf-8"
BUFFER_SIZE = 2048
OFFSET = 10000

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

def display_noti(title, content):
    tkinter.messagebox.showinfo(title, content)

class BasePeerUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.chatroom_textCons = None

        self.frames = {}
        for F in (StartPage, RegisterPage, LoginPage, RepoPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(bg='white')
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")
        self.page_title = customtkinter.CTkLabel(self, text="File Sharing Application", font=("Arial Bold", 50))
        self.page_title.pack(padx=10, pady=(70, 50))

        self.port_entry = customtkinter.CTkEntry(self, placeholder_text=" Enter port number here... ", border_width=1, width=300, height=50, font=("Roboto", 15, 'italic'))
        self.port_entry.pack(padx=10, pady=10)
        self.page_title = customtkinter.CTkLabel(self, text=" Enter your port number [1024, 65535] before \"Log in\" or \"Register\"!", font=("Segoe UI", 17, "italic"))
        self.page_title.pack(padx=10, pady=(10, 20))

        self.login_button = customtkinter.CTkButton(self, text="Log In", font=("Roboto", 20), command=lambda: self.enter_app(controller=controller, port=self.port_entry.get(), page=LoginPage), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10)
        self.login_button.pack(padx=10, pady=10)
        account_prompt_label = customtkinter.CTkLabel(self, text="Or you don't have an account yet?", font=("Roboto", 13, "italic")) 
        account_prompt_label.pack(padx=10, pady=(10, 0))

        self.register_button = customtkinter.CTkButton(self, text="Register", font=("Roboto", 20), command=lambda: self.enter_app(controller=controller, port=self.port_entry.get(), page=RegisterPage), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10)
        self.register_button.pack(padx=10, pady=10)
    
    def enter_app(self, controller, port, page):
        try:
            if not port.isdigit() or not (1024 <= int(port) <= 65535):
                raise ValueError("Invalid port number")
            
            global peer 
            peer = Peer(clientport=int(port))

            recv_t = threading.Thread(target=peer.input_recv)
            recv_t.daemon = True
            recv_t.start()

            recv_file_t = threading.Thread(target=peer.recv_file_content)
            recv_file_t.daemon = True
            recv_file_t.start()
            
            controller.show_frame(page)
        except ValueError as ve:
            self.port_entry.delete(0, customtkinter.END)
            tkinter.messagebox.showinfo("Port Error!", str(ve))
        except OSError as e:
            self.port_entry.delete(0, customtkinter.END)
            tkinter.messagebox.showinfo("Port Error!", f"Socket Error: {e}")
        except Exception as e:
            self.port_entry.delete(0, customtkinter.END)
            tkinter.messagebox.showinfo("Port Error!", "The port is already in use or contains an empty value")
            print(f"Error: {e}")


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.frame = customtkinter.CTkFrame(master=self, fg_color="white")
        self.frame.pack(fill='both', expand=True)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(7, weight=1)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Register", font=("Arial Bold", 45))
        self.title_label.grid(row=1, column=1, columnspan=2, pady=(40, 20), padx=10)

        self.username = customtkinter.CTkLabel(self.frame, text="Username:", font=("Roboto", 20))
        self.username.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.username_entry = customtkinter.CTkEntry(self.frame, placeholder_text=" Enter your username here... ", font=("Roboto", 15, 'italic'), width=300, height=50)
        self.username_entry.grid(row=2, column=2, padx=10, pady=10)

        self.password = customtkinter.CTkLabel(self.frame, text="Password:", font=("Roboto", 20))
        self.password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.password_entry = customtkinter.CTkEntry(self.frame, placeholder_text=" Enter your password here... ", font=("Roboto", 15, 'italic'), show='*', width=300, height=50)
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        customtkinter.CTkButton(self.frame, text='Register', command=lambda: self.register_user(self.username_entry.get(), self.password_entry.get()), font=('Roboto', 20,), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10).grid(row=4, column=1, columnspan=2, pady=20)

        customtkinter.CTkLabel(self.frame, text="Or you already have an account?", font=("Roboto", 15, 'italic')).grid(row=5, column=1, columnspan=2, pady=10, padx=10)
        customtkinter.CTkButton(self.frame, text='Log in', command=lambda: controller.show_frame(LoginPage), font=('Roboto', 20), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10).grid(row=6, column=1, columnspan=2, pady=10, padx=10)

    def register_user(self, username, password):
        peer.name = str(username)
        peer.password = str(password)
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

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(7, weight=1)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Log in", font=("Arial Bold", 45))
        self.title_label.grid(row=1, column=1, columnspan=2, pady=(40, 20), padx=10)

        self.username = customtkinter.CTkLabel(self.frame, text="Username:", font=("Roboto", 20))
        self.username.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.username_entry = customtkinter.CTkEntry(self.frame, placeholder_text=" Enter your username here... ", font=("Roboto", 15, 'italic'), width=300, height=50)
        self.username_entry.grid(row=2, column=2, padx=10, pady=10)

        self.password = customtkinter.CTkLabel(self.frame, text="Password:", font=("Roboto", 20))
        self.password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.password_entry = customtkinter.CTkEntry(self.frame, placeholder_text=" Enter your password here... ", font=("Roboto", 15, 'italic'), show='*', width=300, height=50)
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        customtkinter.CTkButton(self.frame, text='Login', command=lambda: self.login_user(username=self.username_entry.get(), password=self.password_entry.get()), font=('Roboto', 20,), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10).grid(row=4, column=1, columnspan=2, pady=20)

        customtkinter.CTkLabel(self.frame, text="Or you don't have account yet?", font=("Roboto", 15, 'italic')).grid(row=5, column=1, columnspan=2, pady=10, padx=10)
        customtkinter.CTkButton(self.frame, text='Register', command=lambda: controller.show_frame(RegisterPage), font=('Roboto', 20), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=200, height=50, corner_radius=10).grid(row=6, column=1, columnspan=2, pady=10, padx=10)
        
    def login_user(self, username, password):
        peer.name = str(username)
        peer.password = str(password)
        
        self.username_entry.delete(0, customtkinter.END)
        self.password_entry.delete(0, customtkinter.END)
        
        peer.send_login()

class RepoPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((1, 2), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Peer", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text="Quit", command=lambda: self.quit_user())
        self.sidebar_button.grid(row=1, column=0, padx=20, pady=10)

        self.logout_button = customtkinter.CTkButton(self.sidebar_frame, text="Log Out", command=lambda: self.logout_user())
        self.logout_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.repo_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.repo_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.repo_frame.grid_rowconfigure(0, weight=1)
        self.repo_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_repo_frame = customtkinter.CTkScrollableFrame(self.repo_frame, label_text="Repository")
        self.scrollable_repo_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.scrollable_repo_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_repo_files = []
        self.fileListBox = tk.Listbox(self.scrollable_repo_frame, width=75, height=20)
        self.fileListBox.grid(row=0, column=0, padx=10, pady=(10, 10))
        for file in self.scrollable_repo_files:
            self.fileListBox.insert(tk.END, file)
        
        self.temp_frame = customtkinter.CTkFrame(master=self.repo_frame, fg_color="transparent")
        self.temp_frame.grid(row=2, column=0, sticky="nsew")
        self.temp_frame.grid_rowconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(1, weight=1)

        self.upload_button = customtkinter.CTkButton(master=self.temp_frame, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.search_button = customtkinter.CTkButton(master=self.temp_frame, text="Search File", command=self.search_file)
        self.search_button.grid(row=0, column=1, padx=20, pady=(20, 10))

        self.publish_button = customtkinter.CTkButton(master=self.repo_frame, text="Publish File To Repository", font=('Roboto',15), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=100, height=30, command=lambda: self.choose_file_to_publish())
        self.publish_button.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="nsew")

        self.delete_button = customtkinter.CTkButton(master=self.temp_frame, text="Delete File", font=('Roboto',15), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=100, height=30, command=lambda: self.delete_file_from_repo())
        self.delete_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.reload_button = customtkinter.CTkButton(master=self.temp_frame, text="Reload Repository", font=('Roboto',15), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=100, height=30, command=lambda: self.reload_repo())
        self.reload_button.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        
        self.peer_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.peer_frame.grid(row=0, column=2, columnspan = 2, rowspan=3, sticky="nsew")
        self.peer_frame.grid_rowconfigure(0, weight=1)
        self.peer_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_peer_frame = customtkinter.CTkScrollableFrame(self.peer_frame, label_text="Peer List")
        self.scrollable_peer_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.scrollable_peer_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_peer_names = []
        self.peerListBox = tk.Listbox(self.scrollable_peer_frame, width=75, height=20)
        self.peerListBox.grid(row=0, column=0, padx=10, pady=(10, 10))

        self.search_frame = customtkinter.CTkFrame(self.peer_frame, fg_color="transparent")
        self.search_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.search_frame.grid_rowconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = customtkinter.CTkEntry(master=self.search_frame, placeholder_text=" > Search... ", font=("Roboto",13,'italic'), height=30, width=80)
        self.search_entry.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.search_button = customtkinter.CTkButton(master=self.search_frame, text="Search", font=("Roboto",15), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=100, height=30, command=lambda: self.find_file_from_user())
        self.search_button.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        self.request_button = customtkinter.CTkButton(master=self.peer_frame, text="Send Connection Request", font=('Roboto',15), text_color="#0B6A9F", fg_color="#BFE3FE", hover_color="#46A2E7", width=100, height=30, command=lambda:self.send_connection_request())
        self.request_button.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.entry = customtkinter.CTkEntry(self, placeholder_text=" > Command... ", font=("Roboto", 15, 'italic'))
        self.entry.grid(row=4, column=1, columnspan=2, padx=(10, 10), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Enter", width=100, height=30, font=("Roboto",15), command=lambda:self.command_line(command = self.entry.get()),fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=4, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

    def logout_user(self):
        peer.send_logout_request()
        app.show_frame(StartPage)

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

    def upload_file(self):
        file_path = tkinter.filedialog.askopenfilename()
        msg_box = tkinter.messagebox.askquestion('Upload File', 'Upload "{}" to repository?'.format(file_path), icon='question')
        if msg_box == 'yes':
            file_name = simpledialog.askstring('Input', 'Choose a name for the file in the repository', parent=self)
            peer.update_repo_to_server(file_name, file_path)
            self.fileListBox.insert(0, f"{file_name} :: {file_path}")
            self.add_to_repo(file_path)
            
    def add_to_repo(self, file_path):
        if not os.path.exists("local-repo"):
            os.makedirs("local-repo")
        destination = os.path.join(os.getcwd(), "local-repo")
        shutil.copy2(file_path, destination)    

    def search_file(self):
        # Hiển thị hộp thoại tìm kiếm tệp
        file_name = self.search_entry.get()
        self.peerListBox.delete(0, tk.END)
        peer.send_listpeer(file_name)

    def choose_file_to_publish(self):
        file_path = tkinter.filedialog.askopenfilename()
        msg_box = tkinter.messagebox.askquestion('Confirmation', 'Upload "{}" to local repository?'.format(file_path), icon="question")
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

class Peer(Base):
    def __init__(self, clientport):
        self.clientport = clientport
        self.clienthost = get_current_IP_address()
        super(Peer, self).__init__(serverhost=self.clienthost, serverport=self.clientport)
        self.username = None
        self.server_info = (self.clienthost, 65432)  # Thêm dòng này để khởi tạo server_info với địa chỉ IP và cổng của server.

        print(f"Peer at {self.clienthost}:{self.clientport}")

        handlers = {
            'REGISTER_SUCCESS': self.register_success,
            'REGISTER_ERROR': self.register_error,
            'LOGIN_SUCCESS': self.login_success,
            'LOGIN_ERROR': self.login_error,
            'LIST_USER_SHARE_FILE': self.list_user_share_file,
            'UPLOAD_SUCCESS': self.upload_success,
            'UPLOAD_ERROR': self.upload_error,
            'FILE_REQUEST': self.file_request,
            'FILE_ACCEPT': self.file_accept,
            'FILE_REFUSE': self.file_refuse,
        }
        for msgtype, function in handlers.items():
            self.add_handler(msgtype, function)

    def send_register(self):
        peer_info = {'username': self.username, 'host': self.clienthost, 'port': self.clientport}
        self.client_send(self.server_info, msgtype='PEER_REGISTER', msgdata=peer_info)

    def register_success(self, msgdata):
        display_noti("Registration", "Registration successful!")
        self.ui.show_frame(LoginPage)

    def register_error(self, msgdata):
        display_noti("Registration Error", "Registration failed. Username may already exist.")

    def login_success(self, msgdata):
        display_noti("Login", "Login successful!")
        self.ui.show_frame(RepoPage)

    def login_error(self, msgdata):
        display_noti("Login Error", "Login failed. Username or password may be incorrect.")

    def list_user_share_file(self, msgdata):
        users_with_file = msgdata['online_user_list_have_file']
        if users_with_file:
            result = "The following users have the file:\n"
            for user in users_with_file:
                result += f"- {user}\n"
        else:
            result = "No users currently have the file."
        display_noti("Search Results", result)

    def upload_success(self, msgdata):
        display_noti("Upload", "File uploaded successfully!")

    def upload_error(self, msgdata):
        display_noti("Upload Error", "File upload failed.")

    def send_register(self):
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.clienthost,
            'port': self.clientport
        }
        self.client_send(self.server_info, msgtype='PEER_REGISTER', msgdata=peer_info)

    def send_login(self):
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.clienthost,
            'port': self.clientport
        }
        self.client_send(self.server_info, msgtype='PEER_LOGIN', msgdata=peer_info)

    def send_listpeer(self, filename):
        peer_info = {
            'peername': self.name,
            'host': self.clienthost,
            'port': self.clientport,
            'filename': filename
        }
        self.client_send(self.server_info, msgtype='PEER_SEARCH', msgdata=peer_info)
        
    def file_request(self, msgdata):
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        filename = msgdata['filename']
        msg_box = tkinter.messagebox.askquestion('File Request', '{} - {}:{} request to take the file "{}"?'.format(peername, host, port, filename), icon="question")
        if msg_box == 'yes':
            data = {
                'peername': self.name,
                'host': self.clienthost,
                'port': self.clientport
            }
            self.client_send((host, port), msgtype='FILE_ACCEPT', msgdata=data)
            display_noti("File Request Accepted", "Send The File!")
            self.friendlist[peername] = (host, port)
            destination = os.path.join(os.getcwd(), "local-repo")
            file_path = tkinter.filedialog.askopenfilename(initialdir=destination)
            file_name = os.path.basename(file_path)
            msg_box = tkinter.messagebox.askquestion('File Explorer', 'Are you sure to send {} to {}?'.format(file_name, peername), icon="question")
            if msg_box == 'yes':
                sf_t = threading.Thread(target=self.transfer_file, args=(peername, file_path, filename))
                sf_t.daemon = True
                sf_t.start()
                tkinter.messagebox.showinfo("File Transfer", '{} has been sent to {}!'.format(file_name, peername))
            else:
                self.client_send((host, port), msgtype='FILE_REFUSE', msgdata={})
    def file_accept(self, msgdata):
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        display_noti("File Request Result", "Accepted")
        self.friendlist[peername] = (host, port)

    def file_refuse(self, msgdata):
        display_noti("File Request Result", 'FILE REFUSED!')

    def transfer_file(self, peer, file_path, file_name_server):
        try:
            peer_info = self.friendlist[peer]
        except KeyError:
            display_noti("File Transfer Result", 'Friend does not exist!')
        else:
            file_name = os.path.basename(file_path)
            def fileThread(filename):
                file_sent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                file_sent.connect((peer_info[0], peer_info[1]+OFFSET))

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
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        file_sent.sendall(bytes_read)
                file_sent.shutdown(socket.SHUT_WR)
                file_sent.close()
                display_noti("File Transfer Result", 'File has been sent!')
                return
            t_sf = threading.Thread(target=fileThread, args=(file_name,))
            t_sf.daemon = True
            t_sf.start()

    def recv_file_content(self):
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_socket.bind((self.clienthost, int(self.clientport) + OFFSET))
        self.file_socket.listen(5)

        while True:
            conn, addr = self.file_socket.accept()
            buf = conn.recv(BUFFER_SIZE)
            message = buf.decode(FORMAT)

            recv_file_info = json.loads(message)

            conn.send("Filename received.".encode(FORMAT))
            print(recv_file_info)

            file_name = recv_file_info['filename']
            friend_name = recv_file_info['friendname']

            with open(file_name, "wb") as f:
                while True:
                    bytes_read = conn.recv(BUFFER_SIZE)
                    if not bytes_read:    
                        break
                    f.write(bytes_read)
            
            app.frames[RepoPage].add_to_repo_from_fetch(file_name, recv_file_info['filenameserver'])
            conn.shutdown(socket.SHUT_WR)
            conn.close()

            display_noti("File Transfer Result", 'You receive a file with name ' + file_name + ' from ' + friend_name)
    def send_logout_request(self):
        peer_info = {
            'peername': self.name,
        }
        self.client_send(self.server_info, msgtype='PEER_LOGOUT', msgdata=peer_info)

    def delete_file_at_server(self, file_name):
        peer_info = {
            'peername': self.name,
            'host': self.clienthost,
            'port': self.clientport,
            'filename': file_name
        }
        self.client_send(self.server_info, msgtype='DELETE_FILE', msgdata=peer_info)
        
    def update_repo_to_server(self, file_name, file_path):
        peer_info = {
            'peername': self.name,
            'host': self.clienthost,
            'port': self.clientport,
            'filename': file_name,
            'filepath': file_path
        }
        self.client_send(self.server_info, msgtype='FILE_REPO', msgdata=peer_info)

def run_peer():
    peer = Peer(clientport=peer.port)
    peer.input_recv()

def main():
    app = BasePeerUI()
    app.title('FILE SHARING APPLICATION')
    app.geometry("1200x600")
    app.resizable(True, True)

    def handle_on_closing_event():
        if tkinter.messagebox.askokcancel("Thoát", "Bạn muốn thoát khỏi ứng dụng?"):
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", handle_on_closing_event)
    app.mainloop()

if __name__ == '__main__':
    main()


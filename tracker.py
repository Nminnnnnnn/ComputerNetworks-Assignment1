from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from Base import Base, get_current_IP_address
from db_queries import get_user_password, get_all_users, add_new_user, delete_all_online_users, get_db, verify_password

import customtkinter
import tkinter.messagebox

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

class ClientFilesList(customtkinter.CTkToplevel):
    def __init__(self, master, username, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.username = username
        self.geometry("600x300")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_files_frame = customtkinter.CTkScrollableFrame(self, label_text="List of Files")
        self.scrollable_files_frame.grid(row=0, column=0, rowspan=4, padx=(10, 0), pady=(10, 0), sticky="nsew")
        
        self.scrollable_clients_files = get_user_file(self.username)
        self.scrollable_clients_files_labels = []
        for i, file_name in enumerate(self.scrollable_clients_files):
            client_label = customtkinter.CTkLabel(master=self.scrollable_files_frame, text=file_name)
            client_label.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_clients_files_labels.append(client_label)

class TrackerUI(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure title and size of windows
        self.title("TRACKER APPLICATION")
        self.geometry(f"{1200}x{600}")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create sidebar frame on the left
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Create 'Tracker' label
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Tracker", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create 'Reload' button to reload list of clients
        self.reload_button = customtkinter.CTkButton(self.sidebar_frame, text="Reload", command=self.reload_tracker)
        self.reload_button.grid(row=1, column=0, padx=20, pady=10)

        # Create "Appearance Mode" and its option menu
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # Create "UI Scaling" and its option menu
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # Create scrollable frame to display clients' list
        self.scrollable_clients_frame = customtkinter.CTkScrollableFrame(self, label_text="LIST OF CLIENTS")
        self.scrollable_clients_frame.grid(row=0, column=1, columnspan=2, rowspan=3, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.scrollable_clients_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_clients_labels = []
        self.status_boxes = []
        self.separators = []

        self.reload_tracker()
        
        # Create CLI for tracker actions: ping and discover
        self.entry = customtkinter.CTkEntry(self, placeholder_text=" > Command... ")
        self.entry.grid(row=3, column=1, padx=(10, 10), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Enter", command=lambda:self.command_line(command=self.entry.get()), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=2, padx=(10, 10), pady=(20, 20), sticky="nsew")

    def delete_client(self, username):
        response = tkinter.messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete client {username}?")
        if response: 
            delete_user(username)
            self.reload_tracker()

    def create_client_row(self, username, row):
        client_label = customtkinter.CTkLabel(master=self.scrollable_clients_frame, text=username)
        client_label.grid(row=row, column=0, padx=10, pady=(0, 20), sticky="w")
        self.scrollable_clients_labels.append(client_label)

        status = "Online" if username in get_onl_users() else "Offline"
        status_bg_color = "#17AE81" if status == "Online" else "#E8E8E8"
        status_text_color = "#FFFFFF" if status == "Online" else "#000000"
        status_box = customtkinter.CTkLabel(master=self.scrollable_clients_frame,
                                            text=status,
                                            fg_color=status_bg_color,
                                            text_color=status_text_color,
                                            width=100,
                                            height=25,
                                            corner_radius=10)
        status_box.grid(row=row, column=1, padx=10, pady=(0, 20))
        self.status_boxes.append(status_box)

        repo_button = customtkinter.CTkButton(
                                        master=self.scrollable_clients_frame, 
                                        text="View Repository", 
                                        command=lambda u=username: self.discover_client(u),
                                        text_color="#0B6A9F", 
                                        fg_color="#BFE3FE", 
                                        hover_color="#46A2E7", 
                                        width=120,
                                        height=30,
                                        corner_radius=10
                                        )
        repo_button.grid(row=row, column=2, padx=10, pady=(0, 20))

        delete_button = customtkinter.CTkButton(master=self.scrollable_clients_frame,
                                        text='Delete Client',
                                        command=lambda u=username: self.delete_client(u),
                                        text_color="#FFFFFF", 
                                        fg_color="#FF6347", 
                                        hover_color="#FF0000", 
                                        width=120,
                                        height=30,
                                        corner_radius=10
                                        )
        delete_button.grid(row=row, column=3, padx=10, pady=(0, 20))

    def reload_tracker(self):
        for widget in self.scrollable_clients_frame.winfo_children():
            if widget.winfo_children():
                widget.destroy()

        self.scrollable_clients_labels = []
        self.status_boxes = []
        self.separators = []
        
        # Tạo một phiên làm việc với cơ sở dữ liệu
        db = next(get_db())
        
        # Truyền phiên làm việc của cơ sở dữ liệu vào hàm get_all_users()
        self.scrollable_clients_names = get_all_users(db)
        
        for i, user in enumerate(self.scrollable_clients_names):
            self.create_client_row(user.username, i)


    # Switch between Light, Dark and System mode
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Change UI scaling
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # Handle tracker commands (discover & ping)
    def command_line(self, command):
        parts = command.split()
        error_message = "Invalid command. Please try again!"
        if len(parts) < 2:
            tkinter.messagebox.showinfo("Notification", error_message)
        
        elif parts[0] == "discover":
            if len(parts) == 2:
                username = parts[1]
                self.discover_client(username)
            else:
                tkinter.messagebox.showinfo("Notification", error_message)

        elif parts[0] == "ping":
            if len(parts) == 2:
                username = parts[1]
                self.ping_client(username)
            else:
                tkinter.messagebox.showinfo("Notification", error_message)

        else:
            tkinter.messagebox.showinfo("Notification", error_message)

    def discover_client(self, username):
        self.files_list = get_user_file(username)
        if self.files_list is None or not isinstance(self.files_list, ClientFilesList):
            self.files_list = ClientFilesList(self, username)
        else:
            self.files_list.focus()

    def ping_client(self, username):
        onlineList = get_onl_users()
        if username in onlineList:
            status_message = f"{username} is online."
        else:
            status_message = f"{username} is not online."
        tkinter.messagebox.showinfo("User Status:", status_message)

class Tracker(Base):
    def __init__(self):
        current_IP_address = get_current_IP_address()
        super(Tracker, self).__init__(serverhost=current_IP_address, serverport=65432)

        print(f"Tracker at {self.serverhost}:{self.serverport}")

        db = next(get_db())
        self.peerList = [user.username for user in get_all_users(db)]

        self.onlineList = {} 
        self.shareList = {}

        delete_all_online_users(db)

        handlers = {
            'PEER_REGISTER': self.peer_register,
            'PEER_LOGIN': self.peer_login,
            'PEER_SEARCH': self.peer_search,
            'PEER_LOGOUT': self.peer_logout,
            'FILE_REPO': self.peer_upload,
            'DELETE_FILE': self.delete_file,
        }
        for msgtype, function in handlers.items():
            self.add_handler(msgtype, function)

    def peer_login(self, data_):
        required_keys = ['username', 'password', 'host', 'port']
        if not all(key in data_ for key in required_keys):
            print("Missing keys in data_: ", data_)
            return
    
        peer_name = data_['username']
        peer_password = data_['password']
        peer_host = data_['host']
        peer_port = data_['port']

        db = next(get_db())
        if peer_name in self.peerList:
            peer_password_retrieved = get_user_password(db, peer_name)
            if peer_password_retrieved and verify_password(peer_password, peer_password_retrieved):
                self.onlineList[peer_name] = (peer_host, peer_port)
                self.client_send((peer_host, peer_port), msgtype='LOGIN_SUCCESS', msgdata={})
                print(f"{peer_name} has logged in")
            else:
                self.client_send((peer_host, peer_port), msgtype='LOGIN_ERROR', msgdata={"error": "Incorrect password"})
                print(f"Incorrect password for {peer_name}")
        else:
            self.client_send((peer_host, peer_port), msgtype='LOGIN_ERROR', msgdata={"error": "Peer not found"})
            print(f"Peer {peer_name} not found")


    def peer_register(self, msgdata):
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        peer_password = msgdata['password']

        db = next(get_db())
        if peer_name in self.peerList:
            self.client_send((peer_host, peer_port), msgtype='REGISTER_ERROR', msgdata={})
            print(peer_name, " has been existed in tracker!")
        else:
            self.peerList.append(peer_name)
            add_new_user(peer_name, peer_password, db)
            self.client_send((peer_host, peer_port), msgtype='REGISTER_SUCCESS', msgdata={})
            print(peer_name, " has been added to tracker!")

    def peer_search(self, msgdata):
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        file_name = msgdata['filename']
        user_list = search_file_name(file_name)

        for peername in user_list:
            if peername in self.onlineList:
                self.shareList[peername] = self.onlineList[peername]

        data = {'online_user_list_have_file': self.shareList}

        self.client_send((peer_host, peer_port), msgtype='LIST_USER_SHARE_FILE', msgdata=data)
        print(peer_name, " has been sent the list of users who have the file!")
        self.shareList.clear()

    def peer_logout(self, msgdata):
        peer_name = msgdata['peername']
        onlineList = get_onl_users()

        if peer_name in onlineList:
            onlineList.remove(peer_name)
            remove_onl_user(peer_name)
            print(peer_name, " has logged out!")

    def peer_upload(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        file_path = msgdata['filepath']
        add_new_file(peer_name, file_name, file_path)

    def delete_file(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        delete_file(peer_name, file_name)
        print(f"{file_name} has been removed from {peer_name}")

def run_tracker():
    tracker = Tracker()
    tracker.input_recv()

def main():
    app = TrackerUI()

    tracker_thread = Thread(target=run_tracker)
    tracker_thread.start()

    app.mainloop()

if __name__ == '__main__':
    main()

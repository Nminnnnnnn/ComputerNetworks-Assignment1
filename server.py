from threading import Thread

from Base import Base, get_current_IP_address
from db_queries import *

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

class ServerUI(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # customtkinter.CTk.__init__(self, *args, **kwargs)
        
        # Configure tilte and size of windows
        self.title("FILE SHARING APPLICATION")
        self.geometry(f"{1200}x{600}")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create sidebar frame on the left (for containing below widgets, components)
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Create 'Server' label
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Server", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create 'Reload' button to reload list of clients
        self.reload_button = customtkinter.CTkButton(self.sidebar_frame, text="Reload", command=self.reload_server)
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

        # Create scrollable frame to display clients's list
        self.scrollable_clients_frame = customtkinter.CTkScrollableFrame(self, label_text="LIST OF CLIENT")
        self.scrollable_clients_frame.grid(row=0, column=1, columnspan=2, rowspan=3, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.scrollable_clients_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_clients_labels = []
        self.status_boxes = []
        self.separators = []

        self.reload_server()
        
        # Create CLI for server action: ping and discover
        self.entry = customtkinter.CTkEntry(self, placeholder_text=" > Command... ")
        self.entry.grid(row=3, column=1, padx=(10, 10), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Enter", command = lambda:self.command_line(command = self.entry.get()), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=2, padx=(10, 10), pady=(20, 20), sticky="nsew")

    def delete_client(self, username):
        response = tkinter.messagebox.askyesno("Xác nhận xoá", f"Bạn có chắc chắn muốn xoá client {username}?")
        if response: 
            delete_user(username)
            self.reload_server()

    def create_client_row(self, username, row):
        client_label = customtkinter.CTkLabel(master=self.scrollable_clients_frame, text=username)
        client_label.grid(row=row, column=0, padx=10, pady=(0, 20), sticky="w")
        self.scrollable_clients_labels.append(client_label)

        status = "Online" if username in get_onl_users() else "Offline"
        status_bg_color = "#17AE81" if status == "Online" else "#E8E8E8"
        status_text_color = "#FFFFFF" if status == "Online" else "#000000"  # White for online, black for offline
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
                                        text_color="#0B6A9F",  # Set the text color to white (color X)
                                        fg_color="#BFE3FE",  # Set the background color to red (color Y)
                                        hover_color="#46A2E7",  # Optional: Change the hover color
                                        width=120,
                                        height=30,
                                        corner_radius=10
                                        )
        repo_button.grid(row=row, column=2, padx=10, pady=(0, 20))

        delete_button = customtkinter.CTkButton(master=self.scrollable_clients_frame,
                                        text='Delete Client',
                                        command=lambda u=username: self.delete_client(u),
                                        text_color="#FFFFFF",  # Set the text color to white (color X)
                                        fg_color="#FF6347",  # Set the background color to red (color Y)
                                        hover_color="#FF0000",  # Optional: Change the hover color
                                        width=120,
                                        height=30,
                                        corner_radius=10
                                        )
        delete_button.grid(row=row, column=3, padx=10, pady=(0, 20))

    def reload_server(self):
        for widget in self.scrollable_clients_frame.winfo_children():
            if widget.winfo_children():
                widget.destroy()

        self.scrollable_clients_labels = []
        self.status_boxes = []
        self.separators = []

        self.scrollable_clients_names = get_all_users()
        for i, username in enumerate(self.scrollable_clients_names):
            self.create_client_row(username, i)

    # Switch between Light, Dark and Default screen mode
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Change components' size
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    # Handle command of server (discover & ping)
    def command_line(self, command):
        parts = command.split()
        error_message = "Lệnh không hợp lệ. Vui lòng nhập lại!"
        if len(parts) < 2:
            tkinter.messagebox.showinfo("Thông Báo", error_message)
        
        elif parts[0] == "discover":
            if len(parts) == 2:
                username = parts[1]
                self.discover_client(username)
            else:
                tkinter.messagebox.showinfo("Thông Báo", error_message)

        elif parts[0] == "ping":
            if len(parts) == 2:
                username = parts[1]
                self.ping_client(username)
            else:
                tkinter.messagebox.showinfo("Thông Báo", error_message)

        else:
            tkinter.messagebox.showinfo("Thông Báo", error_message)

    def discover_client(self,username):
        self.files_list = get_user_file(username)
        if self.files_list is None or not isinstance(self.files_list, ClientFilesList):
            self.files_list = ClientFilesList(self, username)  # create window if its None or not a ClientFilesList
        else:
            self.files_list.focus() # if window exists focus it

    def ping_client(self, username):
        onlineList = get_onl_users()
        if username in onlineList:
            status_message = f"{username} đang online."
        else:
            status_message = f"{username} không trực tuyến."
        tkinter.messagebox.showinfo("Trạng thái người dùng:", status_message)

class Server(Base):
    def __init__(self):
        current_IP_address = get_current_IP_address()
        super(Server, self).__init__(serverhost=current_IP_address, serverport=65432)

        print(f"Server at {self.serverhost}:{self.serverport}")
        
        # get registered user list
        self.peerList = get_all_users()

        # manage online user list
        self.onlineList = {} 

        # manage online user list have file which have been searched
        self.shareList = {}

        # Delete data in table online
        delete_all_onl_users()

        # define handlers for received message of central server
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
        
    ## ==========implement protocol for user registration - server==========##
    def peer_register(self, msgdata):
        # received register info (msgdata): peername, host, port, password (hashed)
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        peer_password = msgdata['password']
        
        # register error if peer name has been existed in central server
        # otherwise add peer to managed user list of central server
        if peer_name in self.peerList:
            self.client_send((peer_host, peer_port),
                             msgtype='REGISTER_ERROR', msgdata={})
            print(peer_name, " has been existed in central server!")
        else:
            # add peer to managed user list
            self.peerList.append(peer_name)
            # save to database
            add_new_user(peer_name, peer_password)
            self.client_send((peer_host, peer_port),
                             msgtype='REGISTER_SUCCESS', msgdata={})
            print(peer_name, " has been added to server's managed list of clients!")
            
    ## ===========================================================##

    ## ==========implement protocol for authentication (log in) - central server==========##
    def peer_login(self, msgdata):
        # received login info (msgdata): peername, host, port, password (hashed)
        peer_name = msgdata['peername'] 
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        peer_password = msgdata['password']
        # login error if peer has not registered yet or password not match
        # otherwise add peer to online user list
        if peer_name in self.peerList:
            # retrieve password
            peer_password_retrieved = get_user_password(peer_name)
            if str(peer_password) == peer_password_retrieved:
                
                # add peer to online user list
                self.onlineList[peer_name] = tuple((peer_host, peer_port))
                add_onl_user(peer_name)
                self.client_send((peer_host, peer_port),
                                 msgtype='LOGIN_SUCCESS', msgdata={})

                # update ipaddress and port using by this peer
                update_user_address_port(peer_name, peer_host, peer_port)
                
                # noti
                print(peer_name, " has been added to central server's online user list!")

            else:
                self.client_send((peer_host, peer_port),
                                 msgtype='LOGIN_ERROR', msgdata={})
                print("Password uncorrect!")
        else:
            self.client_send((peer_host, peer_port),
                             msgtype='LOGIN_ERROR', msgdata={})
            print(peer_name, " has not been existed in central server!")
    ## ===========================================================##

    ## =========implement protocol for finding user list who have file searched==============##
    def peer_search(self, msgdata):
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        file_name = msgdata['filename']
        user_list = search_file_name(file_name)

        for peername in user_list:
            if peername in self.onlineList:
                self.shareList[peername] = self.onlineList[peername]

        data = {
            'online_user_list_have_file': self.shareList
        }

        self.client_send((peer_host, peer_port),
                         msgtype='LIST_USER_SHARE_FILE', msgdata=data)
        print(peer_name, " has been sent latest online user list have file!")
        self.shareList.clear()

    ## ================implement protocol for log out & exit=============##
    def peer_logout(self, msgdata):
        peer_name = msgdata['peername']
        onlineList = get_onl_users()
        # delete peer out of online user list 
        if peer_name in onlineList:
            onlineList.remove(peer_name)
            remove_onl_user(peer_name)
            # noti
            print(peer_name, " has been removed from central server's online user list!")
    ## ===========================================================##

    ## ================implement protocol for peer upload file=============##
    def peer_upload(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        file_path = msgdata['filepath']
        add_new_file(peer_name, file_name, file_path)
    ## ===========================================================##

    ##=================implement protocol for peer delete file=============##
    def delete_file(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        delete_file(peer_name, file_name)
        print(f"{file_name} has been removed out of {peer_name}")

def run_server():
    server = Server()
    server.input_recv()

def main():
    app = ServerUI()

    server_thread = Thread(target=run_server)
    server_thread.start()

    app.mainloop()

if __name__ == '__main__':
    main()

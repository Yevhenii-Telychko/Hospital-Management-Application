import tkinter as tk
from tkinter import ttk
from Window import AddUserWindow, UserWindow, StatsWindow

class App:
    def __init__(self, label, api):
        # Initialize main attributes
        self.listbox = None
        self.root = tk.Tk()
        self.label = label
        self.api = api
        self.num_of_clients = 0
        self.clients = {}
        self.filtered_clients = {}
        self.error_message = ""

    def retrieve_clients(self):
        try:
            # Retrieve client data from the API
            self.num_of_clients = self.api.get_num_of_clients()
            clients = self.api.get_all_clients()
            self.clients = clients["clients"]
            self.error_message = clients["Error Message"]
        except Exception as e:
            print(f"Error retrieving client data: {e}")

    def create_label(self):
        # Create and place the main label
        label = tk.Label(self.root, text="Hospital", font=("Helvetica", 16))
        label.grid(row=0, column=0, pady=10, columnspan=3)

    def create_sorting_widget(self):
        # Create sorting options dropdown
        sort_options = ["Sort by A-Z", "Urgent client", "Consultation client"]
        sort_var = tk.StringVar(self.root)
        sort_var.set(sort_options[0])
        sort_dropdown = ttk.Combobox(self.root, values=sort_options, textvariable=sort_var)
        sort_dropdown.grid(row=1, column=0, padx=10, pady=5, columnspan=3, sticky="ew")

        sort_dropdown.bind("<<ComboboxSelected>>", self.handle_sort_option)

    def create_search_inputs(self):
        # Create search input fields
        self.create_search_input("Search by ID:", row=2, search_func=self.search_by_id)
        self.create_search_input("Search by Last Name:", row=3, search_func=self.search_by_last_name)

    def create_search_input(self, label_text, row, search_func):
        # Create individual search input field
        label = tk.Label(self.root, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="e")

        entry = tk.Entry(self.root)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        search_button = tk.Button(self.root, text="Search", command=lambda: search_func(entry.get()))
        search_button.grid(row=row, column=2, padx=10, pady=5, sticky="w")

    def create_add_client_button(self):
        # Create "Add Client" button
        add_client_button = tk.Button(self.root, text="Add Client", command=self.open_add_user_window)
        add_client_button.grid(row=5, column=0, pady=10, columnspan=1)

    def create_stats_button(self):
        # Create "Stats" button
        add_client_button = tk.Button(self.root, text="Stats", command=self.open_stats_window)
        add_client_button.grid(row=5, column=2, pady=10, columnspan=1)

    def create_clients_list(self):
        # Create and populate the clients list
        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.listbox.grid(row=4, column=0, padx=10, pady=10, columnspan=3, sticky="nsew")

        # Sample clients for demonstration
        if list(self.clients.keys())[0] == "-1":
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, self.error_message)
            return

        for client in self.clients.values():
            client_repr = f"{client['last_name']} {client['first_name']}"
            self.listbox.insert(tk.END, client_repr)

        scrollbar = tk.Scrollbar(self.root, command=self.listbox.yview)
        scrollbar.grid(row=4, column=3, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.listbox.bind('<ButtonRelease-1>', self.on_listbox_click)

    def update_listbox(self, data):
        # Update the listbox with new data
        if list(data.keys())[0] == "-1":
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, self.error_message)
        else:
            self.listbox.delete(0, tk.END)
            for client in data.values():
                client_repr = f"{client['last_name']} {client['first_name']}"
                self.listbox.insert(tk.END, client_repr)

    def open_add_user_window(self):
        # Open the "Add User" window
        additional_window = tk.Toplevel(self.root)
        window = AddUserWindow(additional_window, self.api,
                               lambda: (self.retrieve_clients(), self.update_listbox(self.clients)))
        window.show()

    def open_stats_window(self):
        # Open the "Stats" window
        additional_window = tk.Toplevel(self.root)
        data = self.get_stats()
        window = StatsWindow(additional_window, data)
        window.show()

    def on_listbox_click(self, event):
        # Handle click on the listbox
        selected_index = self.listbox.curselection()
        if selected_index:
            client_id = list(self.clients.keys())[selected_index[0]]
            selected_client = self.clients[client_id]
            additional_window = tk.Toplevel(self.root)
            window = UserWindow(additional_window, api=self.api,
                                callback=lambda: (self.retrieve_clients(), self.update_listbox(self.clients)),
                                client=selected_client)
            window.show()

    def search_by_id(self, id):
        # Perform search by client ID
        if id != '':
            data = self.api.search_by_id(int(id))
            self.filtered_clients = data["clients"]
            self.error_message = data["Error Message"]
            self.update_listbox(self.filtered_clients)
        else:
            self.update_listbox(self.clients)

    def search_by_last_name(self, last_name):
        # Perform search by client last name
        if last_name != '':
            data = self.api.search_by_last_name(last_name)
            self.filtered_clients = data["clients"]
            self.error_message = data["Error Message"]
            self.update_listbox(self.filtered_clients)
        else:
            self.update_listbox(self.clients)

    def handle_sort_option(self, event):
        # Handle selection of sorting option
        selected_option = event.widget.get()
        if selected_option == "Sort by A-Z":
            self.sort_by_last_name()
        elif selected_option == "Urgent client":
            self.sort_by_service_type("Emergency")
        elif selected_option == "Consultation client":
            self.sort_by_service_type("Consultation")

    def sort_by_last_name(self):
        # Sort clients by last name
        try:
            sorted_data = self.api.sort_clients_by_last_name()
            self.clients = sorted_data["clients"]
            self.error_message = sorted_data["Error Message"]
            self.update_listbox(self.clients)
        except Exception as e:
            print(f"Error retrieving client data: {e}")

    def sort_by_service_type(self, service_type):
        # Sort clients by service type
        try:
            sorted_data = self.api.sort_clients_by_service_type(service_type)
            self.clients = sorted_data["clients"]
            self.error_message = sorted_data["Error Message"]
            self.update_listbox(self.clients)
        except Exception as e:
            print(f"Error retrieving client data: {e}")

    def get_stats(self):
        # Calculate and return statistics
        stats = {
            "emergency_patients": 0,
            "consultation_patients": 0,
            "speciality": {
                "General": 0,
                "Gynecology": 0,
                "Radiology": 0,
                "Gastroenterology": 0,
                "Surgery": 0,
            }
        }
        for client in self.clients.values():
            if client["service_type"] == "Emergency":
                stats["emergency_patients"] += 1
            elif client["service_type"] == "Consultation":
                stats["consultation_patients"] += 1
            stats["speciality"][client["specialty"]] += 1

        return stats

    def configure(self):
        # Configure the main window
        self.root.title(self.label)
        self.root.geometry("600x400")
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.retrieve_clients()
        self.create_label()
        self.create_sorting_widget()
        self.create_search_inputs()
        self.create_clients_list()
        self.create_add_client_button()
        self.create_stats_button()

    def run(self):
        # Run the application
        self.configure()
        self.root.mainloop()

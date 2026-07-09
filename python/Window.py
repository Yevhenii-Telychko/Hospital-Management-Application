import tkinter as tk
from tkinter import ttk


# Validation functions for Entry widgets
def validate_str(data):
    return not data.isdigit()


def validate_num(data):
    return data.isdigit()


# Base Window class
class Window:
    def __init__(self, window_sample):
        self.window = window_sample
        self.entry_vars = []  # List to store Entry widget variables
        self.service = ""  # Variable to store selected service

    def configuration(self):
        # Basic window configuration
        self.window.geometry("600x400")
        self.window.grid_rowconfigure(12, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)

    def create_label(self, label, row=0):
        # Method to create labels
        label = tk.Label(self.window, text=label, font=("Helvetica", 16))
        label.grid(row=row, column=0, columnspan=3, pady=10)

    def create_button(self, text, func, row=12, column=0, columnspan=3):
        # Method to create buttons
        submit_button = tk.Button(self.window, text=text, command=func)
        submit_button.grid(row=row, column=column, columnspan=columnspan, pady=10)

    def create_entry_with_label(self, values=None):
        # Method to create Entry widgets with associated labels
        data = "Service type,First name,Last name,Address,Age,Sex,Illness,Room number,Specialty,Doctor,Date,Time,Nights"

        labels = data.split(',')

        for i in range(len(labels)):
            col_num = i % 3
            row_num = i // 3 * 2

            label = tk.Label(self.window, text=labels[i].capitalize())
            label.grid(row=row_num + 1, column=col_num, padx=10, pady=5, sticky="w")
            validate_num_func = self.window.register(validate_num)
            validate_str_func = self.window.register(validate_str)
            entry_var = tk.StringVar()
            if label.cget("text") in ["Age", "Room number", "Nights"]:
                entry = tk.Entry(self.window, textvariable=entry_var, validate="key",
                                 validatecommand=(validate_num_func, '%P'))
            elif label.cget("text") not in ["Address", "Date", "Time"]:
                entry = tk.Entry(self.window, textvariable=entry_var, validate="key",
                                 validatecommand=(validate_str_func, '%P'))
            else:
                entry = tk.Entry(self.window, textvariable=entry_var)

            if values:
                entry.insert(0, values[i + 1])
            entry.grid(row=row_num + 2, column=col_num, sticky="w", padx=10, pady=5)

            self.entry_vars.append(entry_var)

        label = tk.Label(self.window, text="Service")
        label.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        # Define a list of services, you can load this from a file or other source
        services = ["Childbirth", "Health check-up", "Carpal tunnel operation", "ENT", "Ultrasound", "Colonoscopy",
                    "MRI"]

        service_var = tk.StringVar()
        service_dropdown = ttk.Combobox(self.window, textvariable=service_var, values=services)
        if values and values[len(values) - 1] in services:
            service_dropdown.set(values[len(values) - 1])
        service_dropdown.bind("<<ComboboxSelected>>",
                              lambda event: self.on_combobox_change(service_var, service_dropdown))
        service_dropdown.grid(row=10, column=1, padx=10, pady=5, sticky="w")
        self.service = service_var.get()

    def is_not_empty(self):
        # Method to check if all Entry widgets are filled
        ready = False
        for i in range(len(self.entry_vars)):
            if type(self.entry_vars[i]) == tk.StringVar:
                data = self.entry_vars[i].get()
            else:
                data = self.entry_vars[i]

            if not bool(data):
                self.create_label("Fill all the inputs")
                ready = False
                break
            else:
                self.entry_vars[i] = data
            ready = True
        return ready

    def on_combobox_change(self, service_var, combobox):
        # Method to handle Combobox selection change
        service_var.set(combobox.get())
        self.service = combobox.get()

    def show(self):
        # Method to display the window configuration
        self.configuration()


# AddUserWindow class, inherits from Window
class AddUserWindow(Window):
    def __init__(self, window_sample, api, callback):
        super().__init__(window_sample)
        self.api = api
        self.callback = callback

    def configuration(self):
        # Additional configuration for AddUserWindow
        super().configuration()
        self.create_label("Add User")
        self.create_button("Submit", self.add_client)
        self.create_entry_with_label()

    def add_client(self):
        # Method to add a new client
        if self.is_not_empty():
            new_client = ','.join(self.entry_vars) + f',{self.service}'
            self.api.add_client(new_client)
            self.callback()
            self.window.destroy()


# UserWindow class, inherits from Window
class UserWindow(Window):
    def __init__(self, window_sample, api, callback, client):
        super().__init__(window_sample)
        self.api = api
        self.callback = callback
        self.client = client

    def configuration(self):
        # Additional configuration for UserWindow
        super().configuration()
        self.create_label(f"{self.client['first_name']} {self.client['last_name']}")
        self.create_button("Update", self.modify_client, column=0, columnspan=1)
        self.create_button("Delete", self.delete_client, column=2, columnspan=1)
        self.create_button("Finance", self.open_window, column=1, columnspan=1)
        self.create_entry_with_label(list(self.client.values()))

    def modify_client(self):
        # Method to modify client information
        if self.is_not_empty():
            new_client = ','.join(self.entry_vars) + f',{self.service}\n'
            self.api.modify_client(f"{self.client['id']},{new_client}")
            self.callback()
            self.window.destroy()

    def delete_client(self):
        # Method to delete a client
        self.api.delete_client(str(self.client["id"]))
        self.callback()
        self.window.destroy()

    def open_window(self):
        # Method to open a ServiceWindow
        additional_window = tk.Toplevel(self.window)
        window = ServiceWindow(additional_window, self.api, self.client)
        window.show()


# ServiceWindow class, inherits from Window
class ServiceWindow(Window):
    def __init__(self, window_sample, api, client):
        super().__init__(window_sample)
        self.api = api
        self.client = client

    def configuration(self):
        # Additional configuration for ServiceWindow
        self.window.geometry("600x400")
        self.window.grid_rowconfigure(4, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.create_label(f"{self.client['first_name']} {self.client['last_name']}", row=0)
        self.create_label(f"Doctor: {self.client['doctor']}", row=1)
        self.create_label(f"Service: {self.client['service']}", row=2)
        self.create_label(f"Stayed: {self.client['nights']}  nights", row=3)
        self.create_label(f"Has to pay: {self.api.count_bill(self.client['id'])} euros", row=4)


# StatsWindow class, inherits from Window
class StatsWindow(Window):
    def __init__(self, window_sample, data):
        super().__init__(window_sample)
        self.data = data

    def configuration(self):
        # Additional configuration for StatsWindow
        self.window.geometry("600x400")
        self.window.grid_rowconfigure(8, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.create_label(f"Stats", row=0)
        self.create_label(f"Emergency patients {self.data['emergency_patients']}", row=1)
        self.create_label(f"Consultation patients  {self.data['consultation_patients']}", row=2)
        self.create_label(f"General:  {self.data['speciality']['General']}", row=3)
        self.create_label(f"Gynecology:  {self.data['speciality']['Gynecology']}", row=4)
        self.create_label(f"Radiology:  {self.data['speciality']['Radiology']}", row=5)
        self.create_label(f"Gastroenterology:  {self.data['speciality']['Gastroenterology']}", row=6)
        self.create_label(f"Surgery:  {self.data['speciality']['Surgery']}", row=7)

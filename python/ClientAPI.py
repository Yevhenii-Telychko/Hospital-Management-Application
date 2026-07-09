from ctypes import CDLL, Structure, c_int, c_char, c_char_p, POINTER
import uuid

# Maximum length for string fields
MAX_LINE_LENGTH = 256


# Define the structure for the Client
class Client(Structure):
    _fields_ = [
        ("id", c_int),
        ("service_type", c_char * MAX_LINE_LENGTH),
        ("first_name", c_char * MAX_LINE_LENGTH),
        ("last_name", c_char * MAX_LINE_LENGTH),
        ("address", c_char * MAX_LINE_LENGTH),
        ("age", c_int),
        ("sex", c_char * MAX_LINE_LENGTH),
        ("illness", c_char * MAX_LINE_LENGTH),
        ("room_number", c_int),
        ("specialty", c_char * MAX_LINE_LENGTH),
        ("doctor", c_char * MAX_LINE_LENGTH),
        ("date", c_char * MAX_LINE_LENGTH),
        ("time", c_char * MAX_LINE_LENGTH),
        ("nights", c_int),
        ("service", c_char * MAX_LINE_LENGTH)
    ]


# Function to format a single client's data
def format_user(data):
    return {
        data.id: {
            'id': data.id,
            'service_type': data.service_type.decode('utf-8'),
            'first_name': data.first_name.decode('utf-8'),
            'last_name': data.last_name.decode('utf-8'),
            'address': data.address.decode('utf-8'),
            'age': data.age,
            'sex': data.sex.decode('utf-8'),
            'illness': data.illness.decode('utf-8'),
            'room_number': data.room_number,
            'specialty': data.specialty.decode('utf-8'),
            'doctor': data.doctor.decode('utf-8'),
            'date': data.date.decode('utf-8'),
            'time': data.time.decode('utf-8'),
            'nights': data.nights,
            'service': data.service.decode('utf-8')
        }
    }


# Function to format a list of clients' data
def format_clients(data, num_of_clients):
    client_dict = {}
    for i in range(num_of_clients):
        client = data[i]
        client_dict[client.id] = format_user(client)[client.id]
    return client_dict


# Class for interacting with the client data through an API
class ClientAPI:
    def __init__(self):
        # File paths for clients and history data
        self.file_path = {
            "clients": b"./db/clients.csv",
            "history": b"./db/deleted_clients.csv"
        }
        # Load the shared library for working with CSV files
        self.csv_file = CDLL("../c/lib_csvFile.dll")

    # Function to generate a unique ID for a new client
    def generate_id(self):
        # If there are no clients, start with ID 0
        if self.get_all_clients()["Error Message"]:
            ids = [0]
        else:
            # Get existing client IDs
            ids = [id for id in self.get_all_clients()["clients"].keys()]
        while True:
            # Generate a unique ID using the first 4 characters of a UUID
            unique_id = str(uuid.uuid4().int)[:4]
            if unique_id not in ids:
                return unique_id

    # Function to free the memory allocated for clients
    def free_clients_memory(self, clients_ptr):
        self.csv_file.freeClientsMemory.argtypes = [POINTER(Client)]
        self.csv_file.freeClientsMemory(clients_ptr)

    # CLIENT

    # Function to get the number of clients
    def get_num_of_clients(self):
        self.csv_file.countNewlines.restype = c_int
        self.csv_file.countNewlines.argtypes = [c_char_p]
        num_of_clients = self.csv_file.countNewlines(self.file_path["clients"])
        return num_of_clients

    # Function to get all clients
    def get_all_clients(self):
        response = {"clients": {}, "Error Message": ""}
        num_of_clients = self.get_num_of_clients()
        try:
            self.csv_file.getAllClients.argtypes = [c_char_p, c_int]
            self.csv_file.getAllClients.restype = POINTER(Client)
            data = self.csv_file.getAllClients(self.file_path["clients"], num_of_clients)
            if num_of_clients != 0:
                response["clients"] = format_clients(data, num_of_clients)
                self.free_clients_memory(data)
                response["Error Message"] = ""
                return response
            else:
                response['clients'] = {"-1": {}}
                response['Error Message'] = "No clients found"
                return response
        except UnicodeDecodeError as e:
            print(f"Error decoding: {e}")
            response['clients'] = {"-1": {}}
            response['Error Message'] = "No clients found"
            return response

    # Function to add a new client
    def add_client(self, client: str):
        self.csv_file.addClient.argtypes = [c_char_p, c_char_p]
        id = self.generate_id()
        client = f"{id}," + client
        self.csv_file.addClient(client.encode('utf-8'), self.file_path["clients"])

    # Function to delete a client
    def delete_client(self, id):
        self.csv_file.deleteClientFromFile.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.csv_file.deleteClientFromFile(self.file_path["clients"], b"./db/tempfile.csv", self.file_path["history"],
                                           id.encode("utf-8"))

    # Function to modify a client's information
    def modify_client(self, client):
        self.csv_file.updateLineInFile.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        id = client.split(',')[0]
        self.csv_file.updateLineInFile(self.file_path["clients"], b"./db/tempfile.csv", client.encode('utf-8'),
                                       id.encode('utf-8'))

    # Function to count the bill for a client
    def count_bill(self, id):
        self.csv_file.countBill.argtypes = [c_int, c_char_p]
        self.csv_file.countBill.restype = c_int
        return self.csv_file.countBill(id, self.file_path["clients"])

    # FILTER

    # Function to search for a client by ID
    def search_by_id(self, id):
        response = {"clients": {}, "Error Message": ""}
        try:
            self.csv_file.searchByID.restype = Client
            self.csv_file.searchByID.argtypes = [c_int, c_char_p]
            result = self.csv_file.searchByID(id, self.file_path["clients"])
            response['clients'] = format_user(result)
            response['Error Message'] = ""
            return response
        except UnicodeDecodeError as e:
            print(f"Error decoding: {e}")
            response['clients'] = {"-1": {}}
            response['Error Message'] = "No clients found"
            return response

    # Function to search for a client by last name
    def search_by_last_name(self, last_name):
        response = {"clients": {}, "Error Message": ""}
        try:
            self.csv_file.searchByLastName.restype = Client
            self.csv_file.searchByLastName.argtypes = [c_char_p, c_char_p]
            result = self.csv_file.searchByLastName(last_name.encode('utf-8'), self.file_path["clients"])
            response['clients'] = format_user(result)
            response['Error Message'] = ""
            return response
        except UnicodeDecodeError as e:
            print(f"Error decoding: {e}")
            response['clients'] = {"-1": {}}
            response['Error Message'] = "No clients found"
            return response

    # SORT

    # Function to sort clients by last name
    def sort_clients_by_last_name(self):
        response = {"clients": {}, "Error Message": ""}
        num_of_clients = self.get_num_of_clients()
        try:
            self.csv_file.sortClientsByName.argtypes = [c_char_p]
            self.csv_file.sortClientsByName.restype = POINTER(Client)
            data = self.csv_file.sortClientsByName(self.file_path["clients"], num_of_clients)
            response["clients"] = format_clients(data, num_of_clients)
            self.free_clients_memory(data)
            response["Error Message"] = ""
            return response
        except UnicodeDecodeError as e:
            print(f"Error decoding: {e}")
            response['clients'] = {"-1": {}}
            response['Error Message'] = "No clients found"
            return response

    # Function to filter clients by service type
    def sort_clients_by_service_type(self, service_type):
        response = {"clients": {}, "Error Message": ""}
        try:
            self.csv_file.filterClientsByServiceType.argtypes = [c_char_p, c_char_p, POINTER(c_int)]
            self.csv_file.filterClientsByServiceType.restype = POINTER(Client)
            filter_count = c_int()
            data = self.csv_file.filterClientsByServiceType(self.file_path["clients"], service_type.encode('utf-8'),
                                                            filter_count)
            response["clients"] = format_clients(data, filter_count.value)
            self.free_clients_memory(data)
            response["Error Message"] = ""
            return response
        except UnicodeDecodeError as e:
            print(f"Error decoding: {e}")
            response['clients'] = {"-1": {}}
            response['Error Message'] = "No clients found"
            return response

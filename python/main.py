from App import App
from ClientAPI import ClientAPI

api = ClientAPI()
app = App("Hospital", api)
app.run()

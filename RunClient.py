from Client import App, Client

if __name__ == '__main__':
    host = "192.168.0.123"
    port = 65432  # Server port

    c = Client.Client(host, port)
    app = App.App(c)
    app.mainloop()


from Client import App, Client

if __name__ == '__main__':
    host = "127.0.0.1"  # Server IP address
    port = 65432  # Server port

    c = Client.Client(host, port)
    app = App.App(c)
    app.mainloop()


from Server import server

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 65432
    serv = server.Server(host, port)
    serv.run()

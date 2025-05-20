from Server import server

if __name__ == '__main__':
    host = '10.0.0.5'
    port = 65432
    serv = server.Server(host, port)
    serv.run()

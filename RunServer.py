from Server import server

if __name__ == '__main__':
    host = '192.168.0.123'
    port = 65432
    serv = server.Server(host, port)
    serv.run()

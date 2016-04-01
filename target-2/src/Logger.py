import socket
import threading

class Logger(object):
    """
    Logs information to connections on port 6000. Simple way of accessing logs
    using netcat:
                    nc 192.168.7.2 6000
    """
    LOGGER_PORT = 6000

    def __init__(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conns = []
        self.thread = threading.Thread(target = self.accept_thread)
        self.thread.start()

    def accept_thread(self):
        """
        Simple thread that waits for connections and appends them to the list
        as they come in.
        """
        self.listen_socket.bind(('', Logger.LOGGER_PORT))
        self.listen_socket.listen(1)

        while True:
            try:
                conn, _ = self.listen_socket.accept()
                self.conns.append(conn)
            except:
                break

    def close(self):
        # forces accept() in accept_thread to raise an exception
        self.listen_socket.shutdown(socket.SHUT_RDWR)
        self.listen_socket.close()
        self.thread.join()

# Uhhhh what?
    def message(self, msg):
        bad_conns = []

        for conn in self.conns:
            try:
                conn.sendall(msg + "\n")
            except socket.error:
                bad_conns.append(conn)

        for bad_conn in bad_conns:
            self.conns.remove(bad_conn)

    def info(self, msg):
        self.message("INFO: " + msg)

    def error(self, msg):
        self.message("Error: " + msg)

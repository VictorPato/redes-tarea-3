import json
from json import JSONDecodeError
from random import choice
from threading import Timer
import datetime

from routing.router_port import RouterPort


class Router(object):
    def __init__(self, name, update_time, ports, logging=True):
        self.name = name
        self.update_time = update_time
        self.ports = dict()
        self.routing_table = dict()
        self.routing_table[name] = 0, 0
        self._init_ports(ports)
        self.timer = None
        self.logging = logging

    def _success(self, message):
        """
        Internal method called when a packet is successfully received.
        :param message:
        :return:
        """
        f = open('logs.txt', 'a+')
        f.write(str(datetime.datetime.now())[:-7] + " [{}] {}: {}".format(self.name, 'Success! Data', message) + "\n")
        f.close()

    def _log(self, message):
        """
        Internal method to log messages.
        :param message:
        :return: None
        """
        if self.logging:
            f = open('logs.txt', 'a+')
            f.write(str(datetime.datetime.now())[:-7] + " [{}] {}".format(self.name, message) + "\n")
            f.close()

    def _init_ports(self, ports):
        """
        Internal method to initialize the ports.
        :param ports:
        :return: None
        """
        for port in ports:
            input_port = port['input']
            output_port = port['output']

            router_port = RouterPort(
                input_port, output_port, lambda p: self._new_packet_received(p)
            )
            self.ports[output_port] = router_port

    def _new_packet_received(self, packet):
        """
        Internal method called as callback when a packet is received.
        :param packet:
        :return: None
        """
        self._log("Packet received")
        message = packet.decode()

        try:
            message = json.loads(message)
        except JSONDecodeError:
            self._log("Malformed packet")
            return

        if 'destination' in message and 'data' in message and 'type' in message:
            if message['type'] == 'd':
                if message['destination'] == self.name:
                    self._success(message['data'])
                else:
                    if message["destination"] not in self.routing_table:
                        self._log("No route known for {}".format(message["destination"]))
                    else:
                        port = self.routing_table[message["destination"]][1]
                        self.ports[port].send_packet(packet)
            elif message['type'] == 't':
                # todo: quizas no
                tabla_del_otro_router = json.loads(message['data'])
                for destino, val in tabla_del_otro_router.items():
                    distancia = val[0]
                    if not destino in self.routing_table:
                        self.routing_table[destino] = distancia + 1, message['destination']
                    elif self.routing_table[destino][0] > distancia + 1:
                        self.routing_table[destino] = distancia + 1, message['destination']
        else:
            self._log("Malformed packet")

    def _broadcast(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("Broadcasting")
        for output_port, router_port in self.ports.items():
            packet = dict()
            packet["data"] = json.dumps(self.routing_table)
            packet["type"] = 't'
            packet["destination"] = router_port.input_port
            binary_packet = json.dumps(packet).encode()
            router_port.send_packet(binary_packet)
        self.timer = Timer(self.update_time, lambda: self._broadcast())
        self.timer.start()

    def start(self):
        """
        Method to start the routing.
        :return: None
        """
        self._log("Starting")
        self._broadcast()
        for port in self.ports.values():
            port.start()

    def stop(self):
        """
        Method to stop the routing.
        Is in charge of stop the router ports threads.
        :return: None
        """
        self._log("Stopping")
        if self.timer:
            self.timer.cancel()

        for port in self.ports.values():
            port.stop_running()

        for port in self.ports.values():
            port.join()

        self._log("Stopped")

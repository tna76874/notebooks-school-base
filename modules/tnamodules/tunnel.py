#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opening cloudflared tunnel
"""
import re
import time
import os
import qrcode
from IPython.display import display, Image
import subprocess
import signal

class SimpleHTTPServer:
    def __init__(self, port=8080):
        self.port = port
        self.process = None
        self.home_directory = os.path.join(os.path.expanduser("~"), "http")


    def start(self):
        # Erstelle das Home-Verzeichnis, wenn es nicht existiert
        if not os.path.exists(self.home_directory):
            os.makedirs(self.home_directory)

        # Wechsle zum Home-Verzeichnis
        os.chdir(self.home_directory)
        
        # Baue den Befehl zusammen
        command = f"python -m http.server {self.port}"

        # Starte den Server im Hintergrund und erhalte die PID
        self.process = subprocess.Popen(command, shell=True)

        # Speichere die PID in einer Datei
        with open("/tmp/server.pid", "w") as pid_file:
            pid_file.write(str(self.process.pid))

    def stop(self):
        if self.process:
            # Lese die PID aus der Datei
            with open("/tmp/server.pid", "r") as pid_file:
                pid = int(pid_file.read().strip())

            # Beende den Prozess
            os.kill(pid, signal.SIGTERM)
            self.process = None

class CloudflaredTunnelManager:
    def __init__(self, file_path='/tmp/srv.txt', port=8080):
        self.file_path = file_path
        self.port = port
        self.http = SimpleHTTPServer(port=self.port)

    def check_srv(self):
        if not os.path.exists(self.file_path):
            return []   
        with open(self.file_path, "r") as file:
            text = file.read()
        return re.findall(r"https?://(?:\S+?\.)?trycloudflare\.com\S*", text)

    def show_qr(self,srv):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(srv[0])
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        display(img)
        
    def stop_tunnel(self):
        for i in range(2): os.system('pkill cloudflared')

    def start_tunnel(self):
        srv = self.check_srv()
        if not srv:
            self.stop_tunnel()
            time.sleep(4)
            os.system(f'tunnel {self.port}')
            time.sleep(4)
            srv = self.check_srv()

        if not srv:
            print('Error: No tunnel started')

        else:
            print(f'Tunnel started on {"; ".join(srv)}')
            self.show_qr(srv)


if __name__ == '__main__':
    tunnel_manager = CloudflaredTunnelManager()
    tunnel_manager.start_tunnel()
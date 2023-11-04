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
import psutil
import socket

class JupyterTokenParser:
    def __init__(self):
        self.token_pattern = re.compile(r'http://[0-9\.]+:\d+/\?token=([a-zA-Z0-9]+)')

    def get_jupyter_token(self):
        try:
            # Shell-Kommando ausführen und Ergebnis abrufen
            result = subprocess.run(["jupyter", "notebook", "list"], capture_output=True, text=True)
            output_string = result.stdout

            # Suche nach dem Token im String
            match = self.token_pattern.search(output_string)

            if match:
                # Extrahiere den Token aus dem Match-Objekt
                token = match.group(1)
                return token
            else:
                print("Token nicht gefunden.")
                return None
        except Exception as e:
            print(f"Fehler beim Abrufen des Tokens: {e}")
            return None

class QRCodePrinter:
    def __init__(self, url, version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4):
        self.url = url
        self.version = version
        self.error_correction = error_correction
        self.box_size = box_size
        self.border = border
        self.show_qr()

    def show_qr(self):
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        display(img)


class SimpleHTTPServer:
    def __init__(self, port=8080):
        self.port = port
        self.process = None
        self.home_directory = os.path.join(os.path.expanduser("~"), "http")

    def is_port_in_use(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.port)) == 0

    def start(self):
        try:
            # Überprüfe, ob der Port bereits in Verwendung ist
            if self.is_port_in_use():
                print(f"Port {self.port} is already in use.")
                return
            
            # Erstelle das Home-Verzeichnis, wenn es nicht existiert
            if not os.path.exists(self.home_directory):
                os.makedirs(self.home_directory)
            
            # Baue den Befehl zusammen
            command = f"python -m http.server {self.port} --directory {self.home_directory}"
    
            # Starte den Server im Hintergrund und erhalte die PID
            self.process = subprocess.Popen(command, shell=True)
    
            # Speichere die PID in einer Datei
            with open("/tmp/server.pid", "w") as pid_file:
                pid_file.write(str(self.process.pid))
        except:
            print("Error starting webserver.")

    def stop(self):
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = process.info['cmdline']
            if cmdline and 'http.server' in " ".join(cmdline):
                pid = process.info['pid']
                try:
                    os.kill(pid, signal.SIGTERM)
                    self.process = None
                except: pass

class CloudflaredTunnelManager:
    def __init__(self, file_path='/tmp/srv.txt', port=8080):
        self.file_path = file_path
        self.port = port
        self.http = SimpleHTTPServer(port=self.port)
        
        self.exe = 'tunnel'
        
        self.srv = None

    def check_srv(self):
        if not os.path.exists(self.file_path):
            return []   
        with open(self.file_path, "r") as file:
            text = file.read()
        srv = re.findall(r"https?://(?:\S+?\.)?trycloudflare\.com\S*", text)
        if srv:
            self.srv = srv[0]
        return srv

    def show_qr(self,srv):
        QRCodePrinter(srv[0])
        
    def stop_tunnel(self):
        for i in range(2):  os.system(f'{self.exe} -k')

    def start_tunnel(self, show=True):
        srv = self.check_srv()
    
        for _ in range(3):
            if srv:
                break
        
            if not srv:
                self.stop_tunnel()
                time.sleep(4)
                os.system(f'{self.exe} -p {self.port}')
                time.sleep(4)
                srv = self.check_srv()

        if show:
            if not srv:
                print('Error: No tunnel started')
    
            else:
                print(f'Tunnel started on {"; ".join(srv)}')
                self.show_qr(srv)

class JupyterTunnel(CloudflaredTunnelManager):
    def __init__(self, file_path='/tmp/srv.txt', port=8888):
        # Rufe den __init__ der Elternklasse auf
        super().__init__(file_path=file_path, port=port)
        
        self.start_tunnel(show=False)
        if not isinstance(self.srv,type(None)):
            token = JupyterTokenParser().get_jupyter_token()
            url = f'{self.srv}/?token={token}'
            QRCodePrinter(url)
            print(f'Jupyter Server share: {url}')
        else:
            print('Error starting tunnel')


if __name__ == '__main__':
    tunnel_manager = CloudflaredTunnelManager()
    # tunnel_manager.start_tunnel()
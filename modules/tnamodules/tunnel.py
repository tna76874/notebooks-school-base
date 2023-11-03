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


class CloudflaredTunnelManager:
    def __init__(self, file_path='/tmp/srv.txt', port=8080):
        self.file_path = file_path
        self.port = port

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

    def start_tunnel(self):
        srv = self.check_srv()
        if not srv:
            os.system('pkill cloudflared')
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
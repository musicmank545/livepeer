# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 17:34:19 2021

@author: jkuhnsman
"""

import requests
import json
import pandas as pd
import re
import socket
import folium
import ast
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO


def parse_ip(url):
    try:
        host = re.search("https://(.*?)\:", url).group(1)
        ip = socket.gethostbyname(host)
    except:
        ip = None    
    return ip

def get_ip_loc(ip,n):
    try:
        url = 'http://ipinfo.io/{}'.format(ip)
        response = requests.get(url)
        rjs = response.json()
        loc = rjs['loc'].split(',')
        
        d_loc = {'lat':float(loc[0]), 'lon':float(loc[1])}
        return d_loc[n]
    except:
        return None
    
def process_request():
    cli_request = requests.get("http://localhost:7935/registeredOrchestrators", verify=False)

    df = pd.DataFrame(cli_request.json())
    
    
    df['IP'] = df['ServiceURI'].apply(parse_ip)
    df['LAT'] = df['IP'].apply(get_ip_loc, args=('lat',))
    df['LON'] = df['IP'].apply(get_ip_loc, args=('lon',))
    
    return df

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        df = process_request()
        data = json.dumps(df.to_json(orient='records'))
        self.wfile.write(data.encode('utf-8'))
        
def http_server(mode = 'client'):
    
    if mode == 'client':
        httpd = HTTPServer(('', 6000), SimpleHTTPRequestHandler)

        while True:
            httpd.handle_request()

    if mode == 'server':
        
        df_list=[]
        df_list.append(process_request())
        
        get_chicago = requests.get('http://107.191.48.167:7935/registeredOrchestrators', verify=False)
        df_chicago = pd.DataFrame(json.loads(get_chicago.json()))
        df_list.append(df_chicago)
        
        get_frank = requests.get('http://frankfurt.ftkuhnsman.com:7935/registeredOrchestrators', verify=False)
        df_frank = pd.DataFrame(json.loads(get_frank.json()))
        df_list.append(df_frank)
        
        return pd.concat(df_list)
        
if __name__ == '__main__':
    df = http_server()
    

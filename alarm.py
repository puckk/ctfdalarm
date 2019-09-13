import yaml
import os
import requests
from bs4 import BeautifulSoup

base_path = os.path.dirname(os.path.abspath(__file__))
config_file = 'config.yml'

with open(os.path.join(base_path, config_file), 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

ctfs = cfg["ctfds"]
for ctf in ctfs:
    host = ctfs[ctf]["host"]
    user = ctfs[ctf]["user"]
    paswd = ctfs[ctf]["paswd"]
    s = requests.Session()
    res = s.get("https://ctf.forensia.linti.unlp.edu.ar/login").text
    bs = BeautifulSoup(res, "html.parser")
    nonce = res
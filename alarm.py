# requirements: gron
# go get -u github.com/tomnomnom/gron
import json
import yaml
import os
import requests
import re
from bs4 import BeautifulSoup
import smtplib
import subprocess

def sendmail(user, passwd, smtphost, to, ctf, host):
    SUBJECT = 'se actualizo {}'.format(ctf)
    server = smtplib.SMTP(smtphost, 587)
    server.ehlo()
    server.starttls()
    server.login(user, passwd)
    BODY = '\r\n'.join(['To: %s' % to,
                        'From: %s' % user,
                        'Subject: %s' % SUBJECT,
                        '', host])
    server.sendmail(user, [to], BODY)
    print('email sent')
    server.quit()


def send_telegram(bot_token, bot_chatID, ctf, host,resultado):
    print("Sending")
    msg = 'se actualizo {}\n{}\n\nDiferencias:\n{}'.format(ctf, host,resultado[:3000])
    #bot_token = ''
    #bot_chatID = ''
    send_text = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot_token, bot_chatID, msg)

    response = requests.get(send_text)

    return response.json()


base_path = os.path.dirname(os.path.abspath(__file__))
config_file = 'config.yml'

with open(os.path.join(base_path, config_file), 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

import subprocess
subprocess.check_output("echo test>test",shell=True)
ctfs = cfg["ctfds"]
for ctf in ctfs:
    host = ctfs[ctf]["host"]
    user = ctfs[ctf]["user"]
    paswd = ctfs[ctf]["paswd"]
    s = requests.Session()

    # GET to login
    res = s.get("{}/login".format(host)).text

    # Extract nonce
    bs = BeautifulSoup(res, "html.parser")
    pattern = re.compile(r"'csrfNonce': \"(.*?)\"", re.MULTILINE | re.DOTALL)
    script = bs.find("script", text=pattern)
    print(script)
    nonce = pattern.search(str(script)).group(1)
    print("nonce",nonce)
    # Post to login
    res = s.post("{}/login".format(host),
                 data={"nonce": nonce, "name": user, "password": paswd})

    # get challenges and check if diff
    dd = s.get("{}/api/v1/challenges".format(host))
    if dd.status_code == 200:
        data = dd.text
        #print(data)
        file1 = "db_{}".format(ctf)
        file2 = "db_{}DB".format(ctf)
    if not (os.path.exists(os.path.join(base_path, file2))):
        d = open(os.path.join(base_path, file2), "w")
        d.write("{}")
        d.close()

    d1 = open("{}".format(file1), "w")
    d1.write(data)
    d1.close()

    try:
          cmd="/usr/bin/diff <(gron {}) <(gron {})".format(file1,file2)
          print(cmd)
          resultado= subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, executable='/bin/bash').decode()
    except subprocess.CalledProcessError as e:
          resultado=e.output.decode()
    if len(resultado) > 2:
        print("Differences")
        if cfg["mail"]["enabled"]:
          sendmail(cfg["mail"]["from"], cfg["mail"]["from_pass"], cfg["mail"]["smtp_host"], cfg["mail"]["to"], ctf, host)
        if cfg["telegram"]["enabled"]:
          print(send_telegram(cfg["telegram"]["bot_token"], cfg["telegram"]["chat_id"], ctf, host,resultado))
    else:
        print("son iguales")

    cmd="cp {} {}".format(file1,file2)
    resultado= (subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, executable='/bin/bash').decode())

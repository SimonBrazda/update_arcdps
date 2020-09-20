#! python3

import os
import sys, logging, time, os.path
import hashlib
import subprocess

import requests, psutil
from requests.models import HTTPError

arc = 'https://www.deltaconnected.com/arcdps/x64/d3d9.dll'
arc_MD5 = 'https://www.deltaconnected.com/arcdps/x64/d3d9.dll.md5sum'
gw2_file = "Gw2-64.exe"
arc_file = "d3d9.dll"
arc_md5_file = "d3d9.dll.md5sum"
gw2_directory = os.path.join("F:/", "Program Files", "Guild Wars 2")
arc_directory = os.path.join(gw2_directory, "bin64")
filepath_to_check = os.path.join(arc_directory, arc_file)

class ArcUpdateError(Exception):
    pass

class NoFileToUpdateError(Exception):
    pass

class HashesDoNotMatchError(Exception):
    pass

def is_proc_running(name):
    """Return a list of processes matching 'name'.
    
        Parameters:
            name (str): A name of process

        Returns:
            bool: True if process is running else False"""

    for p in psutil.process_iter(['name']):
        if p.info['name'] == name:
            return True

    return False

def hashfile(file):
    BUF_SIZE = 65536    # Enables hashing large sized files
    md5 = hashlib.md5() 
   
    with open(file, 'rb') as f: 
          
        while True: 
            data = f.read(BUF_SIZE) 
   
            if not data: 
                break
            md5.update(data) 
    return md5.hexdigest() 

def hash_str(file):
    md5 = hashlib.md5(file) 
    return md5.hexdigest()

def update_dll():
    res = requests.get(arc)
    try:
        res.raise_for_status()
    except HTTPError as err:
        print(str(err))
        raise ArcUpdateError

    content = res.content

    with open(os.path.join(arc_directory, "d3d9.dll.temp.md5sum"), "r") as md5_temp:
        hash_res = hash_str(content)
        hash_compare = md5_temp.read()
        if hash_res != hash_compare:
            raise HashesDoNotMatchError
        else:
            if os.path.isfile(os.path.join(arc_directory, "d3d9.dll.md5sum")):
                os.remove(os.path.join(arc_directory, "d3d9.dll.md5sum"))
    
    os.rename(os.path.join(arc_directory, "d3d9.dll.temp.md5sum"), os.path.join(arc_directory, "d3d9.dll.md5sum"))
    
    if os.path.isfile(os.path.join(arc_directory, "d3d9_back.dll")):
        os.remove(os.path.join(arc_directory, "d3d9_back.dll"))
        os.rename(os.path.join(arc_directory, arc_file), os.path.join(arc_directory, "d3d9_back.dll"))
       
    with open(os.path.join(arc_directory, arc_file), "wb") as dll_file:
        dll_file.write(res.content)

    print("Arc has been succesfully updated!")
    launch_gw2()

def get_page(url):
    res = requests.get(url)
    try:
        res.raise_for_status()
    except HTTPError as exc:
        print("Excception: " + str(exc))
        # raise ArcUpdateFailure
    return str(res.content)

def parse_arc_md5(arc_md5):
    return arc_md5[2:arc_md5.find(" ")]

def is_update_needed():
    arc_md5 = parse_arc_md5(get_page(arc_MD5))
    try:
        with open(os.path.join(arc_directory, arc_md5_file), "r") as md5_file:
            if md5_file.read() == arc_md5:
                return False
            else:
                with open(os.path.join(arc_directory, "d3d9.dll.temp.md5sum"), "w") as file:
                    file.write(arc_md5)
                return True
    except FileNotFoundError as err:
        print(err)
        with open(os.path.join(arc_directory, "d3d9.dll.temp.md5sum"), "w") as file:
            file.write(arc_md5)
        return True

def check_for_update():
    is_update_needed_res = is_update_needed()

    if is_update_needed_res == False:
        print("ArcDps is up to date!")
        launch_gw2()
    else:
        try:
            update_dll()
        except HashesDoNotMatchError as err_1:
            print(err_1)
            raise ArcUpdateError

def launch_gw2():
    print(f"Launching {gw2_file}...")
    os.startfile(os.path.join(gw2_directory, gw2_file))
    subprocess.Popen([r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "get_gw2_pass.ps1"], shell=True)
    sys.exit()
   
if is_proc_running(gw2_file) == True:
    print("Guild Wars 2 is already running, please close it!")
    time.sleep(5)
    sys.exit()

try:  
    check_for_update()
except ArcUpdateError as err:
    print(err)
    launch_gw2()
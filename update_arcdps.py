#! python3

from distutils.spawn import find_executable
import os
import sys, logging, time, os.path
import hashlib
import subprocess

import requests, psutil

arc = 'https://www.deltaconnected.com/arcdps/x64/d3d9.dll'
arc_MD5 = 'https://www.deltaconnected.com/arcdps/x64/d3d9.dll.md5sum'
gw2_file = "Gw2-64.exe"
arc_file = "d3d9.dll"
gw2_directory = os.path.join("F:/", "Program Files", "Guild Wars 2")
arc_directory = os.path.join(gw2_directory, "bin64")

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
    BUF_SIZE = 65536 
    md5 = hashlib.md5() 
   
    with open(file, 'rb') as f: 
          
        while True: 
            data = f.read(BUF_SIZE) 
   
            if not data: 
                break
            md5.update(data) 
    return md5.hexdigest() 

def update_dll(new_md5):
    res = requests.get(arc)
    try:
        res.raise_for_status()
    except Exception as exc:
        print("Excception: " + str(exc))
        launch_gw2()

    if os.path.isfile(os.path.join(arc_directory, "d3d9_back.dll")):
        os.remove(os.path.join(arc_directory, "d3d9_back.dll"))
    try:
        os.rename(os.path.join(arc_directory, arc_file), os.path.join(arc_directory, "d3d9_back.dll"))
    except Exception as exc:
        print("Excception: " + str(exc))

    dll_file = open(os.path.join(arc_directory, arc_file), "wb")
    dll_file.write(res.content)
    dll_file.close()
    if new_md5 != hashfile(os.path.join(arc_directory, arc_file)):
        print("Error: Failed to download the dll. Hashes do not match.")
        os.remove(os.path.join(arc_directory, arc_file))
    print("Arc has been succesfully updated!")
    launch_gw2()

def check_for_update():
    filepath_to_check = os.path.join(arc_directory, arc_file)
    if os.path.isfile(filepath_to_check) == False:
        update_dll()
    else:
        current_md5 = hashfile(filepath_to_check)
        res = requests.get(arc_MD5)
        try:
            res.raise_for_status()
        except Exception as exc:
            print("Excception: " + str(exc))
            launch_gw2()

        new_md5 = str(res.content)
        new_md5 = new_md5[2:new_md5.find(" ")]
        if new_md5 == current_md5:
            print("ArcDps is up to date!")
            launch_gw2()
        else:
            update_dll(new_md5)

def launch_gw2():
    # subprocess.run([os.path.join(gw2_path, gw2), " -d"])
    # os.system(os.path.join(gw2_path, gw2) + " -d")
    
    os.startfile(os.path.join(gw2_directory, gw2_file))
    subprocess.Popen([r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "get_gw2_pass.ps1"], shell=True)
    # DETACHED_PROCESS = 8
    # subprocess.Popen([os.path.join(gw2_path, gw2)], creationflags=DETACHED_PROCESS, close_fds=True)
    sys.exit()
   
try:
    if is_proc_running(gw2_file) == True:
        print("Guild Wars 2 is already running, please close it!")
        time.sleep(5)
        sys.exit()
except Exception as err:
    print("Excception: " + str(err))
        
check_for_update()
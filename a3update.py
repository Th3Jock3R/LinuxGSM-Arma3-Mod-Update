#!/usr/bin/python3

import os
import os.path
import re
import shutil
import time
import getpass
from bs4 import BeautifulSoup

from datetime import datetime
from urllib import request

#region Configuration
A3_SERVER_FOLDER = "srv2"
A3_SERVER_ID = "233780"
A3_SERVER_DIR = "/home/gsm/games/gsm/arma/{}".format(A3_SERVER_FOLDER)
A3_WORKSHOP_ID = "107410"

STEAM_CMD = "{}/steamcmd/steamcmd.sh".format(A3_SERVER_DIR)
STEAM_USER = input("Steam Username: ")
STEAM_PASS = getpass.getpass(prompt="Steam Password ")

A3_WORKSHOP_DIR = "{}/steamapps/workshop/content/{}".format(A3_SERVER_DIR, A3_WORKSHOP_ID)
A3_MODS_DIR = "{}/serverfiles/mods".format(A3_SERVER_DIR)

print("")
print("Select Modlist Files Found")
f = []
for (dirpath, dirnames, filenames) in os.walk("{}/modlists".format(A3_SERVER_DIR)):
    f.extend(filenames)
    break
i = 1;
for file in f.sort():
    print("{}.) {}".format(i, file))
    i += 1
print("")

selected_file = int(input("Enter Number: ")) - 1
MOD_FILE = "{}/modlists/{}".format(A3_SERVER_DIR, f[selected_file])

if re.search("\.html$", MOD_FILE) == False:
    MOD_FILE = "{}.html".format(MOD_FILE)


if os.path.exists(MOD_FILE) == False:
    print ("Missing Mod File {}".format(MOD_FILE))
    sys.exit

soup = BeautifulSoup(open(MOD_FILE, "r").read(), features="lxml")

MODS = {}
for item in soup.findAll("tr", {"data-type" : "ModContainer"}):
    name_link   = item.find("a", {"data-type" : "Link"})
    name_object = item.find("td", {"data-type" : "DisplayName"})

    workshopId = re.search("id=(\d+)", name_link["href"])

    if id:
        mod_id = workshopId.group(1)
        mod_link = name_object.contents[0].lower().replace(" ", "_");
        MODS["@{}".format(mod_link)] = mod_id

PATTERN = re.compile(r"workshopAnnouncement.*?<p id=\"(\d+)\">", re.DOTALL)
WORKSHOP_CHANGELOG_URL = "https://steamcommunity.com/sharedfiles/filedetails/changelog"
#endregion

#region Functions
def log(msg):
    print("")
    print("{{0:=<{}}}".format(len(msg)).format(""))
    print(msg);
    print("{{0:=<{}}}".format(len(msg)).format(""))


def call_steamcmd(params):
    os.system("{} {}".format(STEAM_CMD, params))
    print("")


def update_server():
    os.system("cd {} && ./arma3server stop".format(A3_SERVER_DIR))
    os.system("cd {} && ./arma3server update-lgsm".format(A3_SERVER_DIR))
    os.system("cd {} && ./arma3server update".format(A3_SERVER_DIR))

def start_server():
    config_mods = "";
    for mod_name, mod_id in MODS.items():
        config_mods += "mods/{}\;".format(re.escape(mod_name))

    config_mods = "mods=\"{}\"".format(config_mods)

    replaced = False
    f = open("{}/lgsm/config-lgsm/arma3server/arma3server.cfg".format(A3_SERVER_DIR), "w+")
    for line in f:
        if re.search('mods\=\".*\"', line):
            newline = line.replace('.*', config_mods)
            replaced = True

    if replaced == False:
        f.write(config_mods)
    #todo set mods in lgsm config
    f.close()
    os.system("cd {} && ./arma3server start".format(A3_SERVER_DIR))


def mod_needs_update(mod_id, path):
    if os.path.isdir(path):
        response = request.urlopen("{}/{}".format(WORKSHOP_CHANGELOG_URL, mod_id)).read()
        response = response.decode("utf-8")
        match = PATTERN.search(response)

        if match:
            updated_at = datetime.fromtimestamp(int(match.group(1)))
            created_at = datetime.fromtimestamp(os.path.getctime(path))

            return (updated_at >= created_at)

    return False


def update_mods():
    steam_cmd_params  = " +login {} {}".format(STEAM_USER, STEAM_PASS)
    steam_cmd_params += " +force_install_dir {}".format(A3_SERVER_DIR)
    i = 0;
    for mod_name, mod_id in MODS.items():
        path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)

        # Check if mod needs to be updated
        if os.path.isdir(path):

            if mod_needs_update(mod_id, path):
                # Delete existing folder so that we can verify whether the
                # download succeeded
                shutil.rmtree(path)
            else:
                print("No update required for \"{}\" ({})... SKIPPING".format(mod_name, mod_id))
                continue

        # Keep trying until the download actually succeeded
        print("Updating \"{}\" ({})".format(mod_name, mod_id))

        steam_cmd_params += " +workshop_download_item {} {} validate ".format(
            A3_WORKSHOP_ID,
            mod_id
        )
        i = i + 1
    if i > 0:
       steam_cmd_params += " +quit"
       call_steamcmd(steam_cmd_params)
    else:
       print("All Mods are up to date!")
    return True;

def lowercase_workshop_dir():
    def rename_all( root, items):
        for name in items:
            try:
                os.rename(os.path.join(root, name),
                os.path.join(root, name.lower()))
            except OSError:
                pass # can't rename it, so what

    # starts from the bottom so paths further up remain valid after renaming
    for root, dirs, files in os.walk(A3_WORKSHOP_DIR, topdown=False):
        rename_all(root, dirs)
        rename_all(root, files)


def create_mod_symlinks():
    for mod_name, mod_id in MODS.items():
        link_path = "{}/{}".format(A3_MODS_DIR, mod_name)
        real_path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)

        if os.path.isdir(real_path):
            if not os.path.islink(link_path):
                os.symlink(real_path, link_path)
                print("Creating symlink '{}'...".format(link_path))
        else:
            print("Mod '{}' does not exist! ({})".format(mod_name, real_path))

#endregion

log("Updating A3 server ({})".format(A3_SERVER_ID))
update_server()

log("Updating mods")
update_mods()

log("Converting uppercase files/folders to lowercase...")
lowercase_workshop_dir()

log("Creating symlinks...")
create_mod_symlinks()

log("Start A3 server")
start_server()

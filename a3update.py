#!/usr/bin/python3

# MIT License
#
# Copyright (c) 2017 Marcel de Vries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import os.path
import re
import shutil
import time
import getpass 

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

MODS = {
    "@cba_a3":                                   "450814997",
    "@ace3":                                     "463939057",
    "@cup_terrains_core":                        "583496184",
    "@cup_terrains_maps":                        "583544987",
    "@cup_terrains_cwa":                         "853743366",
    "@cup_weapons":                              "497660133",
    "@cup_units":                                "497661914",
    "@cup_vehicles":                             "541888371",
    "@bwmod":                                    "1200127537",
    "@ace3_-_bwmod_compatibility":               "1200145989",
    "@task_force_arrowhead_radio":               "894678801",
    "@rhsusaf":                                  "843577117",
    "@rhsafrf":                                  "843425103",
    "@rhsgref":                                  "843593391",
    "@rhssaf":                                   "843632231",
    "@3cb_factions":                             "1673456286",
    "@3cb_baf_vehicles_(rhs_reskins)":           "1515851169",
    "@3cb_baf_weapons_(rhs_ammo_compatibility)": "1515845502",
    "@3cb_baf_vehicles_(servicing_extension)":   "1135543967",
    "@3cb_baf_units_(rhs_compatibility)":        "1135541175",
    "@3cb_baf_units_(ace_compatibility)":        "1135539579",
    "@3cb_baf_equipment_(acre_compatibility)":   "1135534951",
    "@3cb_baf_vehicles":                         "893349825",
    "@3cb_baf_units":                            "893346105",
    "@3cb_baf_weapons":                          "893339590",
    "@3cb_baf_equipment":                        "893328083"
}

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
    os.system("{}/arma3server {}".format(A3_SERVER_DIR, "update"))

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
    os.system("(cd {} && for i in $( ls | grep [A-Z] ); do mv -i '$i' '`echo $i | tr 'A-Z' 'a-z'`'; done)".format(A3_WORKSHOP_DIR, "{}"))


def create_mod_symlinks():
    for mod_name, mod_id in MODS.items():
        link_path = "{}/{}".format(A3_MODS_DIR, mod_name)
        real_path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)

        if os.path.isdir(real_path):
            if not os.path.islink(link_path):
                os.symlink(real_path, link_path)
#                os.system("ln -s {} {}".format(real_path, link_path))
                print("Creating symlink '{}'...".format(link_path))
        else:
            print("Mod '{}' does not exist! ({})".format(mod_name, real_path))
#endregion

#log("Updating A3 server ({})".format(A3_SERVER_ID))
#update_server()

log("Updating mods")
update_mods()

log("Converting uppercase files/folders to lowercase...")
lowercase_workshop_dir()

log("Creating symlinks...")
create_mod_symlinks()

# LinuxGSM Arma 3 Mod Update Script

This Script install Arma3 Workshop Mods from a given Modlist.


## Install

Create an folder "modlists" in the server root folder (the folder where the arma3server file is)

```bash
$ cd /path/to/arma3server
$ mkdir modlists
```
Copy the a3update.py in the root folder and edit the params:

- A3_SERVER_DIR
- A3_SERVER_FOLDER

## Use

You can start the Arma 3 Launcher, go to mods and create an modlist. Afterwards you export them like explained here [Arma3 Mods and the Arma3 Launcher](https://steamcommunity.com/sharedfiles/filedetails/?id=369395296). Now you upload them to your server and put them in the "modlists" folder.

You can now start the script with
```bash
$ ./a3update.py
```

Now you have to enter your Steam Name, Steam Password and the name of the Modlist.
The Script now update lgsm, arma and all mods inside the modlist.

## Troubleshooting

The Steam Account must own a legal copy of Arma 3, if not, the download of mods from the workshop will fail.


## Special Thanks
to [marceldev89](https://github.com/marceldev89) for create the basic [python script](https://gist.github.com/marceldev89/12da69b95d010c8a810fd384cca8d02a)

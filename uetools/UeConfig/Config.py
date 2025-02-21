# Reads/creates a config environment for UEDGE
from uetools.UeLookup.Lookup import Lookup

class Config(Lookup):
    def __init__(self):
        from os import path
        from yaml import safe_load
        from pathlib import Path
        from easygui import diropenbox
        from tkinter.filedialog import askdirectory
        from tkinter import Tk
        

        super().__init__()
        searchpath = path.expanduser('~')
        try:
            config = safe_load(Path('{}/.uedgerc'.format(searchpath)).read_text())
        except:
            if self.createuedgerc() is False:
                return
            else:
                config = safe_load(Path('{}/.uedgerc'.format(searchpath)).read_text())

        for dirpath in ['aphdir', 'apidir']:
            packobj = self.getpackobj(dirpath)
            try:
                strlen = len(packobj.getpyobject(dirpath)[0])
                packobj.getpyobject(dirpath)[0] = config[dirpath].ljust(strlen)
            except:
                print('Required path "{}" not found in .uedgerc. Aborting!'.format(\
                    dirpath))
                return
                self.configured = False
        # NOTE: what other information to write/store?
        self.configured = True

    def createuedgerc(self):
        from os import path
        from yaml import dump

        paths = {}
        searchpath = path.expanduser('~')
        yes = ['yes', 'y']
        no = ['no', 'n']
        print('UEDGE config file not found!')
        print('Create it here? [y/n]') 
        create = input()
        if (create.lower() in yes) or (len(create) == 0):
            for dirpath in ['aphdir', 'apidir']:
                defpath = 'x'
                while not path.exists(defpath):
                    print('Define path to "{}":'.format(dirpath))
                    defpath = input()
                    defpath = defpath.replace('~', searchpath)
                    if path.exists(defpath) is False:
                        print('Directory does not exist, please try again.')
                    else:
                        paths[dirpath] = path.abspath(defpath)
                        print('    Path defined successfully!')
        else:
            print('Please create .uedgerc manually in your home directory')
            print('Aborting!')
            self.configured = False
            return False
        with open("{}/.uedgerc".format(searchpath),"w") as file:
            dump(paths,file)
        print('UEDGE config file .uedgerc successfully created!')


    def configured(self):
        return self.configured


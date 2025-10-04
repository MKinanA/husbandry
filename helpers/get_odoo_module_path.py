from os import listdir, getcwd
from pathlib import Path
from ast import literal_eval

class NotInAnOdooModule(Exception): pass

def get_odoo_module_path(path: Path | str = Path(getcwd())) -> Path:
    def path_is_odoo_module(path: Path):
        if not path.exists(): return False
        if not '__init__.py' in listdir(path): return False
        if not (path/'__init__.py').is_file(): return False
        if not '__manifest__.py' in listdir(path): return False
        if not (path/'__manifest__.py').is_file(): return False
        try: manifest = literal_eval(open(path/'__manifest__.py').read())
        except: return False
        if not type(manifest) == dict: return False
        if not 'name' in manifest.keys(): return False
        if not type(manifest['name']) == str: return False
        return True
    def return_folder_name_if_its_an_odoo_module(path: Path) -> Path:
        if path == path.parent: raise NotInAnOdooModule('This script is not part of an Odoo module')
        return path if path_is_odoo_module(path) else return_folder_name_if_its_an_odoo_module(path.parent)
    return return_folder_name_if_its_an_odoo_module(Path(path) if not Path(path).is_file() else Path(path).parent).resolve()
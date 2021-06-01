import winreg, sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_reg(name):
    global REG_PATH
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def set_reg(name, value):
    global REG_PATH
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_BINARY, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False

def laptop_compatibility():
    global REG_PATH
    try: # Ver as settings do nvidia shadowplay que estão na registry
        REG_PATH = "SOFTWARE\\NVIDIA Corporation\\Global\\ShadowPlay\\NVSPCAPS"

        #Obter registry values sobre poder gravar o desktop (mesmo em portateis)
        DwmEnabled = get_reg('DwmEnabled')
        DwmEnabledUser = get_reg('DwmEnabledUser')
        #Se o valor for zero ou nao existir, meter 1, de modo a compor o problema do buffer parar while alt-tabbed
        if DwmEnabled == None or DwmEnabled == b'\x00\x00\x00\x00':
            set_reg("DwmEnabled",b'\x01\x00\x00\x00')
        if DwmEnabledUser == None or DwmEnabledUser == b'\x00\x00\x00\x00':
            set_reg("DwmEnabledUser",b'\x01\x00\x00\x00')

    except Exception as e:
        print(str(e))

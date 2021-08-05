import wx, webbrowser

TRAY_TOOLTIP = 'Fortnyce'
TRAY_ICON = 'headshot.png'


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon():
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        #self.set_icon(TRAY_ICON)
        #self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'highlightsCS by Fortnyce', self.redirect)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def redirect(self, event):
        webbrowser.open_new('https://github.com/zepedrotrigo/highlightsCS')

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)


def main():
    app = wx.App()
    TaskBarIcon()
    app.MainLoop()

def mainLoop():
    while True:
        print("HeLlO")


if __name__ == '__main__':
    main()
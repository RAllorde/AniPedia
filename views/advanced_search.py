from database import Genre, get_connection
from config import dbpath
import wx
import wx.lib.scrolledpanel
from math import ceil


class ThreeStateBtn(wx.Button):
    NEUTRAL = 0
    INCLUDE = 1
    EXCLUDE = 2

    def __init__(self, parent, state=NEUTRAL):
        super().__init__(parent, size=(20, 20))

        self._state = state

        self.build_ui()

    def build_ui(self):
        self.SetBackgroundColour('gray')
        self.SetWindowStyleFlag(wx.NO_BORDER)

        self.Bind(wx.EVT_BUTTON, self.toggle_state)

    @property
    def state(self):
        return self._state

    def on_neutral(self, _):
        self.SetBackgroundColour('gray')

    def on_include(self, _):
        self.SetBackgroundColour('green')

    def on_exclude(self, _):
        self.SetBackgroundColour('red')

    def toggle_state(self, event):
        self._state = (self._state + 1) % 3
        [self.on_neutral, self.on_include, self.on_exclude][self._state](event)
        event.Skip()


class Option(wx.Panel):
    def __init__(self, parent, genre=Genre('')):
        super().__init__(parent, size=(-1, 30))
        self.genre = genre

        self.build_ui()

    def build_ui(self):
        self.SetBackgroundColour('blue')
        self.SetSizer(hbox := wx.BoxSizer(wx.HORIZONTAL))

        hbox.Add(btn := ThreeStateBtn(self), 0, wx.ALIGN_CENTER)
        hbox.Add(txt := wx.StaticText(self, label=self.genre.name),
                 1, wx.ALIGN_CENTER | wx.LEFT, 5)

        txt.SetForegroundColour('white')

        self.Bind(wx.EVT_LEFT_DOWN, btn.toggle_state)
        txt.Bind(wx.EVT_LEFT_DOWN, btn.toggle_state)


class AdvancedSearch(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent)

        self.build_ui()

    def build_ui(self):
        self.SetBackgroundColour('#1D1F21')
        self.SetSizer(vbox := wx.BoxSizer(wx.VERTICAL))

        vbox.Add(header := wx.Panel(self, size=(-1, 80)), 0, wx.EXPAND)
        header.SetSizer(header_hbox := wx.BoxSizer(wx.HORIZONTAL))
        header.SetBackgroundColour('#ededed')

        header_hbox.Add(search_box := wx.TextCtrl(header))
        search_box.SetHint('Enter Anime Name')

        header_hbox.Add(search_btn := wx.Button(header, label='Search'))
        vbox.Add(body := wx.Panel(self, size=(100, -1)), 0,
                 wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)
        body.SetSizer(
            body_gs := wx.GridSizer(rows=0, cols=7, vgap=10, hgap=10))
        body.SetBackgroundColour('purple')

        self.SetupScrolling()
        self.search_box = search_box
        self.search_btn = search_btn
        self.body = body
        self.body_gs = body_gs
        self.load_genres()

    def load_genres(self):
        conn = get_connection(dbpath)
        genres = [(Option(self.body, g), 0, wx.EXPAND)
                  for g in sorted(Genre.all(conn), key=lambda g: g.name)]

        self.body_gs.SetRows(ceil(len(genres) / self.body_gs.GetCols()))
        self.body_gs.AddMany(genres)


if __name__ == '__main__':
    title = 'Advanced Search'
    size = (1280, 720)
    style = wx.CAPTION | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX

    app = wx.App()
    frame = wx.Frame(None, title=title, size=size, style=style)
    AdvancedSearch(frame)
    frame.Center()
    frame.Show()
    app.MainLoop()

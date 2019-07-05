import wx

class DoodleWindow(wx.Window):
    menuColours = { 100 : 'Black',
                    101 : 'Yellow',
                    102 : 'Red',
                    103 : 'Green',
                    104 : 'Blue',
                    105 : 'Purple',
                    106 : 'Brown',
                    107 : 'Aquamarine',
                    108 : 'Forest Green',
                    109 : 'Light Blue',
                    110 : 'Goldenrod',
                    111 : 'Cyan',
                    112 : 'Orange',
                    113 : 'Navy',
                    114 : 'Dark Grey',
                    115 : 'Light Grey',
                    }
    maxThickness = 16

    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour("Forest Green")
        self.listeners = []
        self.thickness = 1
        self.SetColour("White")
        self.lines = []
        self.pos = wx.Point(0,0)
        self.MakeMenu()

        self.InitBuffer()

        self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)


    def Cleanup(self, evt):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu


    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(max(1,size.width), max(1,size.height))
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.reInitBuffer = False


    def SetColour(self, colour):
        self.colour = colour
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def SetThickness(self, num):
        self.thickness = num
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def GetLinesData(self):
        return self.lines[:]


    def SetLinesData(self, lines):
        self.lines = lines[:]
        self.InitBuffer()
        self.Refresh()


    def MakeMenu(self):
        menu = wx.Menu()
        keys = list(self.menuColours.keys())
        keys.sort()
        for k in keys:
            text = self.menuColours[k]
            menu.Append(k, text, kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuSetColour, id=100, id2=200)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnCheckMenuColours, id=100, id2=200)
        menu.Break()

        for x in range(1, self.maxThickness+1):
            menu.Append(x, str(x), kind=wx.ITEM_CHECK)

        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuSetThickness, id=1, id2=self.maxThickness)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnCheckMenuThickness, id=1, id2=self.maxThickness)
        self.menu = menu

    def OnCheckMenuColours(self, event):
        text = self.menuColours[event.GetId()]
        if text == self.colour:
            event.Check(True)
            event.SetText(text.upper())
        else:
            event.Check(False)
            event.SetText(text)

    def OnCheckMenuThickness(self, event):
        if event.GetId() == self.thickness:
            event.Check(True)
        else:
            event.Check(False)


    def OnLeftDown(self, event):
        self.curLine = []
        self.pos = event.GetPosition()
        self.CaptureMouse()


    def OnLeftUp(self, event):
        if self.HasCapture():
            self.lines.append( (self.colour, self.thickness, self.curLine) )
            self.curLine = []
            self.ReleaseMouse()


    def OnRightUp(self, event):
        pt = event.GetPosition()
        self.PopupMenu(self.menu, pt)

    def OnMotion(self, event):
        
        if event.Dragging() and event.LeftIsDown():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(self.pen)
            pos = event.GetPosition()
            coords = (self.pos.x, self.pos.y, pos.x, pos.y)
            self.curLine.append(coords)
            dc.DrawLine(*coords)
            self.pos = pos


    def OnSize(self, event):
        self.reInitBuffer = True


    def OnIdle(self, event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)


    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)


    def DrawLines(self, dc):
        for colour, thickness, line in self.lines:
            pen = wx.Pen(colour, thickness, wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                dc.DrawLine(*coords)

    def OnMenuSetColour(self, event):
        self.SetColour(self.menuColours[event.GetId()])

    def OnMenuSetThickness(self, event):
        self.SetThickness(event.GetId())

    def AddListener(self, listener):
        self.listeners.append(listener)

    def Notify(self):
        for other in self.listeners:
            other.Update(self.colour, self.thickness)


class DoodleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Python Drawing", size=(1024,768),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        doodle = DoodleWindow(self, -1)

if __name__ == '__main__':
    app = wx.App()
    frame = DoodleFrame(None)
    frame.Show(True)
    frame.Maximize(True)
    app.MainLoop()
    

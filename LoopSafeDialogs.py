# (c) Copyright 2008, Synapse


import wx
from apy import PostThread


class LoopSafeModal(object):
    """
    Base class to use when creating loop safe dialogs
    """
    def ShowModal(self, closeCallback=None):
        assert True #Your supposed to override this

    def _onShowModalComplete(self, *args, **kwargs):
        """Will callback the function passed on ShowModal with result of original blocking ShowModal"""
        if callable(self._closeCallback):
            self._closeCallback(*args, **kwargs)
        elif __debug__ and self._closeCallback is not None:
            assert False
        self.Destroy()
        return False


class TestDialog(wx.Dialog, LoopSafeModal):
    def ShowModal(self, closeCallback=None):
        """
        Intercept ShowModal and run it in a different thread and call the callback when done

        closeCallback -- The callback to use when dialog is closed
        """
        self._closeCallback = closeCallback
        PostThread.PostThread().post(wx.GetApp().evScheduler, wx.Dialog.ShowModal, [self]).addCallbacks(self._onShowModalComplete)


class FileDialog(wx.FileDialog):
    def ShowModal(self, closeCallback=None):
        """
        Intercept ShowModal and run it in a different thread and call the callback when done

        closeCallback -- The callback to use when dialog is closed
        """
        self._closeCallback = closeCallback
        PostThread.PostThread().post(wx.GetApp().evScheduler, wx.FileDialog.ShowModal, [self]).addCallbacks(self._onShowModalComplete)

    def _onShowModalComplete(self, *args, **kwargs):
        """Will callback the function passed on ShowModal with result of original blocking ShowModal"""
        if callable(self._closeCallback):
            self._closeCallback(self, *args, **kwargs)
        elif __debug__ and self._closeCallback is not None:
            assert False
        self.Destroy()
        return False


class MessageDialog(wx.MessageDialog, LoopSafeModal):
    def ShowModal(self, closeCallback=None):
        """
        Intercept ShowModal and run it in a different thread and call the callback when done

        closeCallback -- The callback to use when dialog is closed
        """
        self._closeCallback = closeCallback
        PostThread.PostThread().post(wx.GetApp().evScheduler, wx.MessageDialog.ShowModal, [self]).addCallbacks(self._onShowModalComplete)


class TextEntryDialog(wx.TextEntryDialog):
    def __init__(self, *args, **kwargs):
        wx.TextEntryDialog.__init__(self, *args, **kwargs)

        #Override normal button event handlers
        for child in self.GetChildren():
            if isinstance(child, wx.Button):
                self.Bind(wx.EVT_BUTTON, self._onButton, child)

    def ShowModal(self, closeCallback=None):
        """
        Intercept ShowModal and run it in a different thread and call the callback when done

        closeCallback -- The callback to use when dialog is closed
        """
        self._closeCallback = closeCallback
        self.CenterOnParent()
        self.GetParent().Enable(False)
        wx.Dialog.Show(self)
        self.Raise()

    def _onButton(self, event):
        """Will callback the function passed on ShowModal with result of original blocking ShowModal"""
        event.StopPropagation()

        #If OK was pressed set the dialogs value to the text ctrl value
        if event.Id == wx.ID_OK:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    self.SetValue(child.GetValue())
                    break

        self.GetParent().Enable(True)
        self.GetParent().Raise()
        if callable(self._closeCallback):
            self._closeCallback(self, event.Id)
        elif __debug__ and self._closeCallback is not None:
            assert False
        self.Destroy()
        return False


class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Test Frame", size=(500,500))
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn1 = wx.Button(self, label="MessageDialog")
        self.Bind(wx.EVT_BUTTON, self.showMessageDialog, btn1)
        sizer.Add(btn1)

        btn2 = wx.Button(self, label="FileDialog")
        self.Bind(wx.EVT_BUTTON, self.showFileDialog, btn2)
        sizer.Add(btn2)

        btn3 = wx.Button(self, label="TextEntryDialog")
        self.Bind(wx.EVT_BUTTON, self.showTextEntryDialog, btn3)
        sizer.Add(btn3)

        self.SetSizerAndFit(sizer)
        self.CenterOnScreen()

    def showMessageDialog(self, event):
        dlg = MessageDialog(self, 'The value enter was invalid', 'Invalid Value', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal(self.onMessageDialogClose)
        #dlg2 = wx.MessageDialog(self, 'The value enter was invalid', 'Invalid Value', wx.OK | wx.ICON_ERROR)
        #dlg2.ShowModal()

    def showFileDialog(self, event):
        dlg = FileDialog(self)
        dlg.ShowModal(self.onFileDialogClose)
        #import os
        #dlg2 = wx.FileDialog(
                #self, message="Choose a file",
                #defaultDir=os.getcwd(), 
                #defaultFile="",
                #wildcard="All files (*.*)|*.*",
                #style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
                #)
        #dlg2.ShowModal()

    def showTextEntryDialog(self, event):
        dlg = TextEntryDialog(self, "tesT")
        dlg.ShowModal(self.onTextEntryDialogClose)
        #dlg = wx.TextEntryDialog(self, "Test")
        #dlg.ShowModal()
        #dlg.Destroy()

    def onMessageDialogClose(self, result):
        print "Message Dialog closed: %s" % str(result)

    def onFileDialogClose(self, dlg, result):
        print "Message Dialog closed: %s" % str(result)

    def onTextEntryDialogClose(self, dlg, result):
        print "Text Entry Dialog closed: %s - %s" % (str(result), dlg.GetValue())


if __name__ == '__main__':
    from apy import EventSchedulerApp

    app = EventSchedulerApp.EventSchedulerApp()
    app.RestoreStdio()
    app.frame = TestFrame(None)
    app.frame.Show()
    app.MainLoop()

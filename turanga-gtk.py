#!/usr/bin/env python
# -*- coding: utf-8 -*-
from turanga import TurangaTextCryp
from turanga import TurangaImageCryp
from gi.repository import Gtk


class GUI:

    def __init__(self):
        #data
        self.CTdata = {
            "TXT_REAL_CHARS": ""
        }
        self.CIdata = {
            "OR_IMG_PATH": "",
            "RE_IMG_PATH": ""
        }

        #Load xml
        self.gui = Gtk.Builder()
        self.gui.add_from_file("gui/TRG-Gui.xml")

        #Events
        events = {
            "on_quit": Gtk.main_quit,
            "on_ct": self.InvokeCT,
            "on_ci": self.InvokeCI,
            "on_es": self.InvokeESTEG,
            "on_open_textfile": self.open_textfile,
            "on_btn_ct_click": self.crypt_text,
            "on_btn_dt_click": self.decrypt_text,
            "on_save_ct_click": self.save_ct,
            "on_ci_open_click": self.open_image,
            "on_ci_click": self.crypt_img,
            "on_ci_save_click": self.save_ci,
            "on_ct_destroy": self.HideCT,
            "on_ci_destroy": self.HideCI
        }

        self.gui.connect_signals(events)

        #set textview in wrap word mode
        text_content = self.gui.get_object("txt_CTContent")
        text_content.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        #Text Crypt Window
        self.CryptTextWindow = self.gui.get_object("CryptTextWindow")

        #Image Crypt Window
        self.CryptImageWindow = self.gui.get_object("CryptImageWindow")

        #Main Window
        window = self.gui.get_object("MainWindow")
        window.show_all()

    def save_ct(self, widget):
        #add filter to get only text files
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        _file = self.save_file_dialog(widget, filter_text)

        if _file:
            content = self.CTdata["TXT_REAL_CHARS"]
            f = open(_file, "w")
            f.write(content)
            f.close()

    def save_ci(self, widget):
        #add filter to get only text files
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Image files")
        filter_text.add_mime_type("image/png")
        _file = self.save_file_dialog(widget, filter_text)

        if _file:
            #set png type
            if "." in _file:
                t = _file.split(".")
                if not t[-1] == "png":
                    _file += ".png"
            else:
                _file += ".png"
            #img files
            f = open(self.CIdata["RE_IMG_PATH"] + ".png")
            nf = open(_file, "w")
            #key files
            kf = open(self.CIdata["RE_IMG_PATH"] + ".crg")
            nkf = open(_file[0:-4] + ".crg", "w")

            #write img
            data = f.read()
            nf.write(data)
            #write
            data = kf.read()
            nkf.write(data)
            #close files
            kf.close()
            nkf.close()
            f.close()
            nf.close()

    def open_textfile(self, widget):
        #add filter to get only text files
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        #invoke file chooser dialog and get path
        _file = self.open_file_dialog(widget, filter_text)

        if _file:
            #get text path object and text content object
            text_path = self.gui.get_object("txt_CTPath")
            text_content = self.gui.get_object("txt_CTContent")
            #read content
            file_content = open(_file)
            content = file_content.read()
            self.CTdata["TXT_REAL_CHARS"] = content
            #set text in controls
            text_path.set_text(_file)
            #create buffer to textview
            bf_content = Gtk.TextBuffer()
            bf_content.set_text(unicode(content, errors='replace'))
            #set text buffer
            text_content.set_buffer(bf_content)

    def open_image(self, widget):
        #add filter to get only text files
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Image files")
        filter_text.add_mime_type("image/jpg")
        filter_text.add_mime_type("image/jpeg")
        filter_text.add_mime_type("image/bmp")
        #invoke file chooser dialog and get path
        _file = self.open_file_dialog(widget, filter_text)
        if _file:
            self.CIdata["OR_IMG_PATH"] = _file
            #set image in window
            img = self.gui.get_object("img_CIOriginal")
            img.set_from_file(_file)

    def decrypt_text(self, widget):
        text_path_obj = self.gui.get_object("txt_CTPath")
        text_pass_obj = self.gui.get_object("txt_CTPass")
        text_content = self.gui.get_object("txt_CTContent")

        path = text_path_obj.get_text()
        passw = text_pass_obj.get_text()
        tbuffer = text_content.get_buffer()

        content = tbuffer.get_text(
            tbuffer.get_start_iter(),
            tbuffer.get_end_iter(),
            True
        )

        if (path or content):
            if passw:
                if path:
                    trg = TurangaTextCryp(path, passw)

                elif content:
                    f = open(".temp-file", "w")
                    f.write(self.CTdata["TXT_REAL_CHARS"])
                    f.close()
                    trg = TurangaTextCryp(".temp-file", passw)

                result = trg.decryp()
                if result:
                    self.CTdata["TXT_REAL_CHARS"] = result
                    txt_buf = Gtk.TextBuffer()
                    txt_buf.set_text(unicode(result, errors='replace'))
                    text_content.set_buffer(txt_buf)
                else:
                    self.msg(
                        self.CryptTextWindow,
                        "El archivo no es un cifrado turanga!"
                    )
            else:
                self.msg(
                    self.CryptTextWindow,
                    "Password!?"
                )
        else:
            self.msg(
                self.CryptTextWindow,
                "Nothing to decrypt!"
            )

    def crypt_text(self, widget):
        text_path_obj = self.gui.get_object("txt_CTPath")
        text_pass_obj = self.gui.get_object("txt_CTPass")
        text_content = self.gui.get_object("txt_CTContent")

        path = text_path_obj.get_text()
        passw = text_pass_obj.get_text()
        tbuffer = text_content.get_buffer()

        content = tbuffer.get_text(
            tbuffer.get_start_iter(),
            tbuffer.get_end_iter(),
            True
        )

        if (path or content) and passw:
            if path:
                trg = TurangaTextCryp(path, passw)
                fcryp = True

            elif content:
                temp = open(".temp_file", "w")
                temp.write(content)
                temp.close()

                trg = TurangaTextCryp(".temp_file", passw)
                fcryp = True
            else:
                fcryp = False

            if fcryp:
                result = trg.cryp()
                self.CTdata["TXT_REAL_CHARS"] = result
                #create text buffer
                text = Gtk.TextBuffer()
                text.set_text(unicode(result, errors='replace'))
                #set result in textview
                text_content.set_buffer(text)

        elif not (path or content):
            self.msg(self.CryptTextWindow, "Nothing to crypt!")

        elif not passw:
            self.msg(self.CryptTextWindow, "Type any password!")

    def crypt_img(self, widget):
        txtpass_obj = self.gui.get_object("txt_CIPass")
        state = self.gui.get_object("lbl_CIState")

        passw = txtpass_obj.get_text()
        imgpath = self.CIdata["OR_IMG_PATH"]

        if imgpath:
            if passw:
                advise = "Se cifrara " + imgpath
                advise += " toma en cuenta que puede tardar dependiendo"
                advise += " la resolucion de la imagen."
                #change status to working
                state.set_markup(
                    "<span color='red'>[*] Working, please wait ...</span>"
                )

                self.info(
                    self.CryptImageWindow,
                    advise
                )

                while Gtk.events_pending():
                    Gtk.main_iteration_do(False)

                trg = TurangaImageCryp(imgpath, ".temp_ci_img", passw)
                trg.cryp()
                #change status to nothing
                state.set_text("")
                #set new img
                imgres = self.gui.get_object("img_CIResult")
                imgres.set_from_file(".temp_ci_img.png")

                self.CIdata["RE_IMG_PATH"] = ".temp_ci_img"

            else:
                self.msg(self.CryptImageWindow, "Password?!")

        else:
            self.msg(self.CryptImageWindow, "Open any image!")

    def InvokeCT(self, widget):
        #Get crypt text window and show
        self.CryptTextWindow.show_all()

    def HideCT(self, widget=None, *data):
        #Se oculta pero no se destruye
        self.CryptTextWindow.hide()
        return True

    def InvokeCI(self, widget):
        #get img crypt window and show
        self.CryptImageWindow.show_all()

    def HideCI(self, widget=None, *data):
        #Se oculta pero no se destruye
        self.CryptImageWindow.hide()
        return True

    def InvokeESTEG(self, widget):
        print(" [*] Esteganographi")

    # To Show File chooser dialog
    # return path of file
    def open_file_dialog(self, widget, filters):
        dialog = Gtk.FileChooserDialog(
            "Please choose a file",
             widget.get_toplevel(),
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK
            )
        )

        dialog.add_filter(filters)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            _file = dialog.get_filename()
            dialog.destroy()
            return _file
        else:
            dialog.destroy()
            return False

    def save_file_dialog(self, widget, filters):
        dialog = Gtk.FileChooserDialog(
            "Save file",
             widget.get_toplevel(),
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.OK
            )
        )

        dialog.add_filter(filters)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            _file = dialog.get_filename()
            dialog.destroy()
            return _file
        else:
            dialog.destroy()
            return False

    def msg(self, widget, mensaje):
        dialogo = Gtk.MessageDialog(
            widget,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            mensaje
        )
        dialogo.run()
        dialogo.destroy()

    def info(self, widget, mensaje):
        dialogo = Gtk.MessageDialog(
            widget,
            0,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            mensaje
        )
        dialogo.run()
        dialogo.destroy()

GUI()
Gtk.main()
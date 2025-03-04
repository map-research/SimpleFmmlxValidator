from xml.dom import minidom
from xml.dom.minidom import Document

import customtkinter as ctk
from tkinter import filedialog, messagebox
import shutil
import os

from FmmlxValidator import easyFmmlxValidator
from SimpleFmmlxTransformer import SimpleFmmlxTransformer
from StandardFmmlxTransformer import StandardFmmlxTransformer

class FMMLxValidatorApp():

    def __init__(self, root):
        self.is_standard = None
        self.root = root
        self.root.title("FMMLx Transformer and Validator")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        #icon_path = os.path.join(os.path.dirname(__file__), "mosaic32.ico")
        #self.root.iconbitmap(icon_path)

        width = 720
        height = 400
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.configure(bg="#DFE4F2")

        self.label_title = ctk.CTkLabel(root, text="FMMLx Transformer and Validator",
                                        font=("Arial", 18, "bold"), text_color="#203864")
        self.label_title.pack(pady=10)

        self.btn_select_file = ctk.CTkButton(root, text="Select XML File", command=self.select_file,
                                             corner_radius=20, fg_color="#203864", hover_color="#4B6EA9")
        self.btn_select_file.pack(pady=5)

        self.label_file_name = ctk.CTkLabel(root, text="No file selected", text_color="#203864")
        self.label_file_name.pack(pady=5)

        button_frame = ctk.CTkFrame(root, fg_color="transparent")
        button_frame.pack(pady=10)

        self.btn_transform = ctk.CTkButton(button_frame, text="Transform FMMLx", command=self.transform_file,
                                           state="disabled", corner_radius=20, fg_color="#D3D3D3",
                                           text_color_disabled="gray")
        self.btn_transform.pack(side="left", padx=5)

        self.btn_validate = ctk.CTkButton(button_frame, text="Validate FMMLx", command=self.validate_file,
                                          state="disabled", corner_radius=20, fg_color="#D3D3D3",
                                          text_color_disabled="gray")
        self.btn_validate.pack(side="left", padx=5)

        self.text_validation = ctk.CTkTextbox(root, height=120, width=680, state="disabled", border_width=1,
                                              border_color="#203864")
        self.text_validation.pack(pady=10)

        self.btn_copy = ctk.CTkButton(root, text="Copy Validation Message", command=self.copy_message, state="disabled",
                                      corner_radius=20, fg_color="#D3D3D3", text_color_disabled="gray")
        self.btn_copy.pack(pady=5)

        self.label_version = ctk.CTkLabel(root, text="version 1.0, build date: Feb 26, 2025", font=("Arial", 8),
                                          text_color="#203864")
        self.label_version.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.file_path = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if self.file_path:
            self.label_file_name.configure(text=os.path.basename(self.file_path) + " ["
                                                + self._determine_fmmlx_type(minidom.parse(self.file_path)) + "]")
            self.clear_message()

    def _determine_fmmlx_type(self, xml_doc: Document) -> str:
        if xml_doc.documentElement.tagName == "XModelerPackage":
            self.is_standard = True
            self._activate_buttons()
            return "Standard FMMLx"
        elif xml_doc.documentElement.tagName == "MultiLevelModel":
            self.is_standard = False
            self._activate_buttons()
            return "Simple FMMLx"
        elif xml_doc.documentElement.tagName == "XModeler":
            return "Outdated FMMLx"
        else:
            return "No FMMLx file detected"

    def _activate_buttons(self):
        self.btn_transform.configure(state="normal", fg_color="#203864",
                                     text=f"Transform to {"Simple" if self.is_standard else "Standard"} FMMLx")
        self.btn_validate.configure(state="normal", fg_color="#203864",
                                    text=f"Validate {"Standard" if self.is_standard else "Simple"} FMMLx")

    def transform_file(self):
        if self.file_path:
            save_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
            if save_path:
                if self.is_standard:
                    SimpleFmmlxTransformer(self.file_path).write_simple_fmmlx(save_path)
                else:
                    StandardFmmlxTransformer(self.file_path).write_standard_fmmlx(save_path)
                #shutil.copy(self.file_path, save_path)
                messagebox.showinfo("Success", "File transformed and saved successfully!")

    def validate_file(self):
        if self.file_path:
            self.text_validation.configure(state="normal")
            self.text_validation.delete("1.0", "end")
            self.text_validation.insert("1.0", self._get_validation_message())
            self.text_validation.configure(state="disabled")
            self.btn_copy.configure(state="normal", fg_color="#203864")

    def _get_validation_message(self) -> str:
        validator = easyFmmlxValidator(self.is_standard, self.file_path)
        return (f"The multi-level model is {validator.get_is_valid_message()} \n"
                f"{validator.get_error_messages()}")

    def copy_message(self):
        message = self.text_validation.get("1.0", "end").strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.root.update()
            messagebox.showinfo("Copied", "Validation message copied to clipboard")

    def clear_message(self):
        self.text_validation.configure(state="normal")
        self.text_validation.delete("1.0", "end")
        self.text_validation.configure(state="disabled")
        self.btn_copy.configure(state="disabled", fg_color="#D3D3D3")


if __name__ == "__main__":
    root = ctk.CTk()
    app = FMMLxValidatorApp(root)
    root.mainloop()

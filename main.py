import tkinter as tk
from numbers import Number
from random import seed, randint, choice
from tkinter import filedialog, ttk, Frame
from tkinter.messagebox import showerror, showinfo

from PIL import Image


class PictureSizeException(Exception):
    def __init__(self, text):
        self.txt = text


class Steganography:

    @staticmethod
    def int_to_bin(rgb):
        r, g, b = rgb[0:3]
        return (f'{r:08b}',
                f'{g:08b}',
                f'{b:08b}')

    @staticmethod
    def bin_to_int(rgb):
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def merge_rgb(rgb1, rgb2):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise PictureSizeException(
                'Image 2 should not be larger than Image 1!')
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()
        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography().int_to_bin(pixel_map1[i, j])
                rgb2 = Steganography().int_to_bin((0, 0, 0))
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography().int_to_bin(pixel_map2[i, j])
                rgb = Steganography().merge_rgb(rgb1, rgb2)
                pixels_new[i, j] = Steganography().bin_to_int(rgb)
        return new_image

    @staticmethod
    def unmerge(img):
        pixel_map = img.load()
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()
        original_size = img.size
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = Steganography().int_to_bin(pixel_map[i, j])
                rgb = (r[4:] + '0000',
                       g[4:] + '0000',
                       b[4:] + '0000')
                pixels_new[i, j] = Steganography().bin_to_int(rgb)
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))
        return new_image


EXC_MESSAGE = "Inappropriate key type"


class AbstractCipher:
    seed()

    def __init__(self):
        self.generated_key = ""

    def __key_gen__(self, key, length):
        raise NotImplementedError("Abstract")

    def __encrypt_func__(self, input_text, generated_key) -> str:
        raise NotImplementedError("Abstract")

    def __decrypt_func__(self, input_text, generated_key) -> str:
        raise NotImplementedError("Abstract")

    def encrypt(self, input_path, output_path, key=None):
        with open(input_path, "r") as open_file:
            input_text = open_file.read()
        self.generated_key = self.__key_gen__(key, len(input_text))
        with open(output_path, "w") as write_file:
            write_file.write(self.__encrypt_func__(input_text,
                                                   self.generated_key))

    def decrypt(self, input_path, output_path, key):
        with open(input_path, "r") as open_file:
            input_text = open_file.read()
        with open(output_path, "w") as write_file:
            write_file.write(self.__decrypt_func__(input_text,
                                                   key))


def __shift__(text, shift):
    result_str = ""
    for line in text:
        for char in line:
            if char.isalpha():
                if char == char.lower():
                    result_str += chr((ord(char) - 97 + shift) % 26 + 97)
                else:
                    result_str += chr((ord(char) - 65 + shift) % 26 + 65)
            else:
                result_str += char
    return result_str


class Caesar(AbstractCipher):
    __KEngLetterDistribution__ = [0.082, 0.015, 0.028, 0.043, 0.130, 0.022,
                                  0.020, 0.061, 0.070, 0.0015, 0.0077, 0.040,
                                  0.024, 0.067, 0.075, 0.019, 0.00095, 0.060,
                                  0.063, 0.091, 0.028, 0.0098, 0.024, 0.0015,
                                  0.020, 0.00074]

    def __key_gen__(self, key, length=None):
        if key and not isinstance(key, Number):
            raise ValueError("Inappropriate key type")
        elif key:
            return key
        return randint(1, 25)

    def __encrypt_func__(self, input_text, generated_key) -> str:
        result_str = ""
        for line in input_text:
            for char in line:
                if char.isalpha():
                    if char == char.lower():
                        result_str += chr(
                            (ord(char) - 97 + generated_key) % 26 + 97)
                    elif char == char.upper():
                        result_str += chr(
                            (ord(char) - 65 + generated_key) % 26 + 65)
                else:
                    result_str += char
        return result_str

    def __decrypt_func__(self, input_text, generated_key) -> str:
        decrypt_key = 26 - generated_key
        result_str = self.__encrypt_func__(input_text, decrypt_key)
        return result_str

    def __variance_sum__(self, text, shift):
        quantity_of_letter = [0 for _ in range(26)]
        for char in text:
            quantity_of_letter[(ord(char) - 97 + shift) % 26] += 1
        return sum((quantity_of_letter[i] / len(text) -
                    self.__KEngLetterDistribution__[i]) ** 2 for i in range(26))

    def __auto_decrypt_func__(self, text):
        just_letter_text = ""
        for line in text:
            for char in line:
                if char.isalpha():
                    just_letter_text += char.lower()
        list_of_probabilities = [self.__variance_sum__(just_letter_text,
                                                       i) for i in range(26)]
        return __shift__(text, list_of_probabilities.index(min(
            list_of_probabilities)))

    def auto_decrypt(self, input_path, output_path):
        with open(input_path, "r") as open_file:
            input_text = open_file.read()
        with open(output_path, "w") as write_file:
            write_file.write(self.__auto_decrypt_func__(input_text))


class Vigener(AbstractCipher):
    def __key_gen__(self, key, length=None):
        if key and (False in ((i.isalpha()) for i in key)):
            raise ValueError(EXC_MESSAGE)
        elif key:
            # making key sizeof input str by cycling it
            generated_key = key.lower()
            return (generated_key * (length // len(key) + 1))[:length]
        alphabet = "".join(chr(i) for i in range(97, 123))
        return "".join(choice(alphabet) for _ in range(length))

    def __encrypt_func__(self, input_text, generated_key):
        result_str = ""
        for line in input_text:
            for char in line:
                if char.isalpha():
                    if char == char.lower():
                        new_char_num = (ord(char) - 97 + ord(generated_key[len(
                            result_str)]) - 97)
                        result_str += chr(new_char_num % 26 + 97)
                    elif char == char.upper():
                        new_char_num = (ord(char) - 65 + ord(generated_key[len(
                            result_str)]) - 97)
                        result_str += chr(new_char_num % 26 + 65)
                    else:
                        result_str += char
                else:
                    result_str += char
        return result_str

    def __decrypt_func__(self, input_text, generated_key):
        if not generated_key:
            raise ValueError(EXC_MESSAGE)
        decrypt_key = "".join(
            chr(220 - ord(i)) for i in
            self.__key_gen__(generated_key, len(input_text)))
        result_str = self.__encrypt_func__(input_text, decrypt_key)
        return result_str


class Vernam(AbstractCipher):
    def __key_gen__(self, key, length=None):
        if key and (
                (False in ((i.isalpha()) for i in key)) or len(key) < length
                - 1):
            raise ValueError(EXC_MESSAGE)
        elif key:
            return (key + "a")[:length].lower()
        alphabet = "".join(chr(i) for i in range(97, 123))
        return "".join(choice(alphabet) for _ in range(length))

    def __encrypt_func__(self, input_text, generated_key):
        result_string = ""
        for line in input_text:
            for char in line:
                xor_num = ord(generated_key[len(result_string)]) - 97
                if char == "\n":
                    result_string += char
                elif char == char.lower():
                    result_string += chr(((ord(char) - 97) ^ xor_num) + 97)
                else:
                    result_string += chr(((ord(char) - 65) ^ xor_num) + 65)
        return result_string

    def __decrypt_func__(self, input_text, generated_key):
        if not generated_key:
            raise ValueError(EXC_MESSAGE)
        return self.__encrypt_func__(input_text, generated_key)


class UploadOutputFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.initUI()
        self.input_path_first = ""
        self.input_path_second = ""
        self.input_key = ""
        self.output_path = ""

    def callback_func(self, event):
        self.btn_upload_text_file.grid_forget()
        self.btn_upload_image_first.grid_forget()
        self.btn_upload_image_second.grid_forget()
        self.key_enter.delete(0, "end")
        self.key_enter.grid_forget()
        self.path_lbl_first.config(text="")
        self.path_lbl_second.config(text="")
        self.key_lbl.config(text="")
        self.path_lbl_first.grid_forget()
        self.path_lbl_second.grid_forget()
        self.key_lbl.grid_forget()
        option = self.combo_options.get()
        if option == "Steganography encrypt" or \
                option == "Steganography decrypt":
            self.btn_upload_image_first.grid(column=3, row=1)
            self.path_lbl_first.grid(column=4, row=1)
            if option == "Steganography encrypt":
                self.btn_upload_image_second.grid(column=3, row=2)
                self.path_lbl_second.grid(column=4, row=2)
        elif option == "Caesar auto-decrypt":
            self.btn_upload_text_file.grid(column=3, row=1)
            self.path_lbl_first.grid(column=4, row=1)
        else:
            self.btn_upload_text_file.grid(column=3, row=1)
            self.path_lbl_first.grid(column=4, row=1)
            self.key_enter.grid(column=3, row=2)
            self.key_lbl.grid(column=3, row=3)

    def initUI(self):
        self.parent.title("Decoдёр")
        self.combo_options = ttk.Combobox(self.parent,
                                          values=["Steganography encrypt",
                                                  "Steganography decrypt",
                                                  "Caesar encrypt",
                                                  "Caesar decrypt",
                                                  "Caesar auto-decrypt",
                                                  "Vigener encrypt",
                                                  "Vigener decrypt",
                                                  "Vernam encrypt",
                                                  "Vernam decrypt"],
                                          state="readonly")
        self.combo_options.grid(column=0, row=1)
        self.combo_options.SeclectedIndex = -1
        self.combo_options.bind("<<ComboboxSelected>>", self.callback_func)
        self.btn_upload_text_file = ttk.Button(text="загрузить текст",
                                               width=25,
                                               command=self.text_upload)
        self.btn_upload_image_first = ttk.Button(text="загрузить изображение",
                                                 width=25,
                                                 command=self.first_image_upload
                                                 )
        self.btn_upload_image_second = ttk.Button(
            text="загрузить изображение",
            width=25,
            command=self.second_image_upload
        )
        self.key_enter = ttk.Entry(width=25)
        self.transfrom_button = ttk.Button(text="DONE", width=20,
                                           command=self.transform_command)
        self.transfrom_button.grid(column=0, row=2)
        self.path_lbl_first = ttk.Label()
        self.path_lbl_second = ttk.Label()
        self.key_lbl = ttk.Label()

    def text_upload(self):
        self.input_path_first = filedialog.askopenfilename(filetypes=[
            ("Text files", "*.txt"), ("HTML files", "*.html"),
            ("All files", "*.*")])
        self.path_lbl_first.config(text=self.input_path_first)

    IMG_FILETYPES = [
        ("Jpeg files", "*.jpeg"), ("JPG files", "*.jpg"),
        ("PNG files", "*.png"), ("BMP files", "*.bmp"),
        ("All files", "*.*")]

    def first_image_upload(self):
        self.input_path_first = filedialog.askopenfilename(
            filetypes=self.IMG_FILETYPES)
        self.path_lbl_first.config(text=self.input_path_first)

    def second_image_upload(self):
        self.input_path_second = filedialog.askopenfilename(
            filetypes=self.IMG_FILETYPES)
        self.path_lbl_second.config(text=self.input_path_second)

    def transform_command(self):
        option = self.combo_options.get()
        try:
            if option == "Steganography encrypt":
                result = ""
                result = Steganography().merge(Image.open(
                    self.input_path_first),
                    Image.open(
                        self.input_path_second)).convert("RGB")
                result.save(filedialog.asksaveasfilename())
            elif option == "Steganography decrypt":
                Steganography().unmerge(Image.open(
                    self.input_path_first)).convert("RGB").save(
                    filedialog.asksaveasfilename())
            elif option == "Caesar encrypt":
                if self.key_enter.get().isdigit():
                    Caesar().encrypt(self.input_path_first,
                                     filedialog.asksaveasfilename(),
                                     int(self.key_enter.get()))
                elif not self.key_enter.get():
                    ces = Caesar()
                    ces.encrypt(self.input_path_first,
                                filedialog.asksaveasfilename())
                    self.key_lbl.config(text="Сгенерированный "
                                             "ключ:" + str(ces.generated_key))
                else:
                    raise ValueError("Введённый ключ не число")
            elif option == "Caesar decrypt":
                if self.key_enter.get().isdigit or not self.key_enter.get():
                    Caesar().decrypt(self.input_path_first,
                                     filedialog.asksaveasfilename(),
                                     int(self.key_enter.get()))
                else:
                    raise ValueError("Введённый ключ не число")
            elif option == "Caesar auto-decrypt":
                Caesar().auto_decrypt(self.input_path_first,
                                      filedialog.asksaveasfilename())
            elif option == "Vigener encrypt":
                vig = Vigener()
                vig.encrypt(self.input_path_first,
                            filedialog.asksaveasfilename(),
                            self.key_enter.get())
                if not self.key_enter.get():
                    self.key_lbl.config(text="Сгенерированный "
                                             "ключ:" + vig.generated_key)
            elif option == "Vigener decrypt":
                Vigener().decrypt(self.input_path_first,
                                  filedialog.asksaveasfilename(),
                                  self.key_enter.get())
            elif option == "Vernam encrypt":
                ver = Vernam()
                ver.encrypt(self.input_path_first,
                            filedialog.asksaveasfilename(),
                            self.key_enter.get())
                if not self.key_enter.get():
                    self.key_lbl.config(text="Сгенерированный "
                                             "ключ:" + ver.generated_key)
            elif option == "Vernam decrypt":
                Vernam().decrypt(self.input_path_first,
                                 filedialog.asksaveasfilename(),
                                 self.key_enter.get())
        except PictureSizeException:
            showerror("Ошибка", "Размер первого изображения превышает размер "
                                "второго")
        except ValueError:
            showerror("Ошибка", "Введённый ключ некорректен")
        except Exception:
            showerror("Ошибка", "Непредвиденная ошибка")
        else:
            showinfo("Успех", "Операция выполнена")


window = tk.Tk()

window.geometry('960x180')
ex = UploadOutputFrame(window)
window.mainloop()

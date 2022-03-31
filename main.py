import io
from xml.dom import minidom

from tkinter import messagebox as mb, scrolledtext
from tkinter import *

from tkinter import Tk, Label, Button, Entry, END, Frame, NO, W, WORD, Text
import tkinter.ttk as ttk
from pymorphy2 import MorphAnalyzer
from tkinter.filedialog import askopenfilename, asksaveasfile

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

main_dictionary = []


cases = {
    "им": "nomn",
    "рд": "gent",
    "дт": "datv",
    "вн": "accs",
    "тв": "ablt",
    "пр": "loct",
    "ед": "sing",
    "мн": "plur",
    "од": "anim",
    "неод": "inan",
    "мр": "masc",
    "жр": "femn",
    "ср": "neut",
    "сов": "perf",
    "несов": "impf",
    "перех": "tran",
    "неперех": "intr",
    "1л": "1per",
    "2л": "2per",
    "3л": "3per",
    "изъяв": "indc",
    "повел": "impr",
    "действ": "actv",
    "страд": "pssv",
    "наст": "pres",
    "прош": "past",
    "буд": "futr"
}


class Word:
    # само слово
    lexeme = ''
    # основа слова
    normal_form = ''
    # падеж
    case = ''
    # часть речи
    POS = ''
    # остальная информация
    info = []

    def __init__(self):
        self.lexeme = ''
        self.normal_form = ''
        self.case = ''
        self.POS = ''
        self.info = []


def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text


def save_dictionary():
    file = asksaveasfile(filetypes=(("dict file", "*.dict"),), defaultextension=("dict file", "*.dict"))
    if file is None:
        return
    doc = minidom.Document()
    root_el = doc.createElement('root')

    words = main_dictionary

    words.sort(key=lambda x: x.lexeme, reverse=True)

    for i in words:
        word = doc.createElement('word')
        lexeme = doc.createElement('lexeme')
        normalized = doc.createElement('normalized')
        pos = doc.createElement('POS')
        info = doc.createElement('info')

        text1 = doc.createTextNode(i.lexeme)
        text2 = doc.createTextNode(i.normal_form)
        text3 = doc.createTextNode(i.POS)

        lexeme.appendChild(text1)
        normalized.appendChild(text2)
        pos.appendChild(text3)
        for j in i.info:
            info.appendChild(doc.createTextNode(j))

        word.appendChild(lexeme)
        word.appendChild(normalized)
        word.appendChild(pos)
        word.appendChild(info)

        root_el.appendChild(word)
    doc.appendChild(root_el)

    xml_str = doc.toprettyxml(indent="  ", encoding='UTF-8')

    file.write(str(xml_str, 'UTF-8'))
    file.close()


def open_file_to_read():
    filename = askopenfilename(filetypes=[("pdf file", "*.pdf")],
                               defaultextension=("pdf file", "*.pdf"))
    if filename is None:
        return

    elif filename.endswith(".pdf"):
        file_str = extract_text_from_pdf(filename)
    else:
        return

    parse_from_text_field(file_str[0:(len(file_str)-1)])
    update_vocabulary()


def load_dictionary():
    filename = askopenfilename(filetypes=(("dict file", "*.dict"),), defaultextension=("dict file", "*.dict"))
    if filename is None:
        return
    file_str = ''
    with open(filename) as file:
        file.readline()
        for line in file:
            file_str = file_str + line
    doc = minidom.parseString(file_str).documentElement
    word_elements = doc.getElementsByTagName("word")

    main_dictionary.clear()
    vocabularyTree.delete(*vocabularyTree.get_children())
    for i in word_elements:
        word = Word()
        word.lexeme = i.getElementsByTagName("lexeme")[0].childNodes[0].nodeValue
        word.normal_form = i.getElementsByTagName("normalized")[0].childNodes[0].nodeValue
        word.POS = i.getElementsByTagName("POS")[0].childNodes[0].nodeValue
        text = i.getElementsByTagName("info")[0].childNodes[0].nodeValue.replace('\n', '')
        text = text.split(' ')
        while text.__contains__(''):
            text.remove('')
        word.info = text
        main_dictionary.append(word)

    update_vocabulary()


def create_vocabulary_from_text_field():
    text = inputText.get(1.0, END).replace('\n', '')
    parse_from_text_field(text)
    update_vocabulary()


# разбор слов
def parse_from_text_field(string: str):
    ignore_symbols = [',', ':', ';', '{', '}']
    for i in ignore_symbols:
        string = string.replace(i, ' ')
    text = string.split(' ')
    while text.__contains__(''):
        text.remove('')
    morph = MorphAnalyzer()
    words = []
    for lex in text:
        w = Word()
        temp = morph.parse(lex)[0]
        w.lexeme = lex
        w.normal_form = morph.normal_forms(lex)[0]
        w.POS = morph.lat2cyr(temp.tag.POS)
        if temp.tag.animacy is not None:
            w.info.append(morph.lat2cyr(temp.tag.animacy))

        if temp.tag.aspect is not None:
            w.info.append(morph.lat2cyr(temp.tag.aspect))

        if temp.tag.case is not None:
            w.info.append(morph.lat2cyr(temp.tag.case))

        if temp.tag.gender is not None:
            w.info.append(morph.lat2cyr(temp.tag.gender))

        if temp.tag.mood is not None:
            w.info.append(morph.lat2cyr(temp.tag.mood))

        if temp.tag.number is not None:
            w.info.append(morph.lat2cyr(temp.tag.number))

        if temp.tag.person is not None:
            w.info.append(morph.lat2cyr(temp.tag.person))

        if temp.tag.tense is not None:
            w.info.append(morph.lat2cyr(temp.tag.tense))

        if temp.tag.transitivity is not None:
            w.info.append(morph.lat2cyr(temp.tag.transitivity))

        if temp.tag.voice is not None:
            w.info.append(morph.lat2cyr(temp.tag.voice))

        words.append(w)

    words.sort(key=lambda x: x.lexeme, reverse=True)

    for lex in words:
        add_flag = True
        for j in main_dictionary:
            if lex is j:
                add_flag = False
        if add_flag:
            main_dictionary.append(lex)


# поиск по определенному правилу
def get_search_result():
    search_req = searchEntry.get()
    if search_req == "":
        mb.showerror(title="Empty field error",
                     message="Search field is empty! You are supposed to enter something before clicking that button.")
        return
    search_req = search_req.replace(',', ' ')
    request = search_req.split(' ')
    normalized = request[0]
    flag = False
    for w in main_dictionary:
        if w.normal_form == normalized:
            flag = True
    if not flag:
        mb.showerror(title="Word doesn't exist",
                     message="There is no such a word in this dictionary.")
        return
    params = []
    for i in range(1, len(request)):
        params.append(request[i])
    for j in range(0, len(params)):
        for i in cases.keys():
            if params[j] == i:
                params[j] = cases[i]

    morph = MorphAnalyzer()
    t = morph.parse(normalized)[0]
    t = t.inflect(set(params))
    mb.showinfo(title="Результат", message=t.word)
    update_vocabulary()


# удаление выбранного элемента
def delete_item():
    try:
        selected = vocabularyTree.focus()
        temp = vocabularyTree.item(selected, 'values')

        for word in main_dictionary:
            if word.lexeme == temp[0]:
                main_dictionary.remove(word)

        vocabularyTree.delete(selected)
    except Exception:
        mb.showerror(title="Error", message="Have you selected any item before clicking that button?..")
        return


# обновление содержимого таблицы
def update_vocabulary():
    vocabularyTree.delete(*vocabularyTree.get_children())

    global main_dictionary
    main_dictionary.sort(key=lambda x: x.lexeme, reverse=False)

    for word in main_dictionary:
        vocabularyTree.insert('', 'end', values=(word.lexeme, word.normal_form,
                                                 word.POS, word.info))


# очистка словаря
def clear_vocabulary():
    vocabularyTree.delete(*vocabularyTree.get_children())
    main_dictionary.clear()


if __name__ == '__main__':
    print(extract_text_from_pdf('sample.pdf'))


def show_help():
    mb.showinfo(title="Помощь", message=HELPTEXT)


def show_help_request():
    mb.showinfo(title="Помощь", message=HELPTEXT2)


HELPTEXT2 = '''                    

Правила тегов
    "им": "nomn",
    "рд": "gent",
    "дт": "datv",
    "вн": "accs",
    "тв": "ablt",
    "пр": "loct",
    "ед": "sing",
    "мн": "plur",
    "од": "anim",
    "неод": "inan",
    "мр": "masc",
    "жр": "femn",
    "ср": "neut",
    "сов": "perf",
    "несов": "impf",
    "перех": "tran",
    "неперех": "intr",
    "1л": "1per",
    "2л": "2per",
    "3л": "3per",
    "изъяв": "indc",
    "повел": "impr",
    "действ": "actv",
    "страд": "pssv",
    "наст": "pres",
    "прош": "past",
    "буд": "futr"

'''


HELPTEXT = '''                    

    Программа предназначена для для обработки текстов на руском языке.

    Проверяет слова в файле, определяет их характеристики и на их основе
может выводить словоформы.

    Для сортировки по значениям в отдельных столбцах таблицы нажимать на названия 
столбцов.

    Поддерживаемые форматы входных текстовых файлов - pdf.

    Для хранения данных словаря используется формат .dict (переименованный .xml).

    При считывании данных из текстового файла и из текстового поля данные добавляются 
в активный словарь. При загрузке имеющегося словаря активный словарь очищается и 
перезаполняется данными из загружаемого

'''


root = Tk()
main_menu = Menu(root)
main_menu.add_command(label='Сохранить имеющийся словарь в файл', command=save_dictionary)
main_menu.add_command(label='Загрузить имеющийся словарь из файла', command=load_dictionary)
main_menu.add_command(label='Помощь', command=show_help)
root.config(menu=main_menu)

space0 = Label(root)
inputFrame = Frame(root, bd=2)
inputText = Text(inputFrame, height=10, width=130, wrap=WORD)

createVocabularyButton_textField = Button(inputFrame, text='Создать словарь по тексту', width=30, height=2, bg='grey')
createVocabularyButton_textFile = Button(inputFrame, text='Создать словарь из текстового файла pdf', width=50,
                                         height=2, bg='grey')
clearVocabularyButton = Button(inputFrame, text='Очистить словарь', width=30, height=2, bg='grey')

deleteElementButton = Button(inputFrame, text='Удалить элемент', width=30, height=2, bg='grey')

space1 = Label(root)
vocabularyFrame = Frame(root, bd=2)
vocabularyTree = ttk.Treeview(vocabularyFrame,
                              columns=("Словоформа", "Лексема", "Часть речи", "Информация"),
                              selectmode='browse', height=11)
vocabularyTree.heading('Словоформа', text="Словоформа", anchor=W)
vocabularyTree.heading('Лексема', text="Лексема", anchor=W)
vocabularyTree.heading('Часть речи', text="Часть речи", anchor=W)
vocabularyTree.heading('Информация', text="Информация", anchor=W)
vocabularyTree.column('#0', stretch=NO, minwidth=0, width=0)
vocabularyTree.column('#1', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#2', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#3', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#4', stretch=NO, minwidth=347, width=400)

space4 = Label(root, text='\n')
searchFrame = Frame(root, bg='grey', bd=5)
searchLabel = Label(searchFrame, text=' Запрос: ', width=14, height=2, bg='grey', fg='white')
searchEntry = Entry(searchFrame, width=23)
space41 = Label(searchFrame, text='      ', bg='grey')
searchButton = Button(searchFrame, text='Найти', width=8, height=2, bg='grey')
clearSearchButton = Button(searchFrame, text='Помощь', width=8, height=2, bg='grey')

createVocabularyButton_textFile.config(command=open_file_to_read)
createVocabularyButton_textField.config(command=create_vocabulary_from_text_field)
clearVocabularyButton.config(command=clear_vocabulary)
deleteElementButton.config(command=delete_item)
searchButton.config(command=get_search_result)
clearSearchButton.config(command=show_help_request)

space0.pack()
inputFrame.pack()
inputText.pack()

createVocabularyButton_textFile.pack(side='left')
createVocabularyButton_textField.pack(side='left')
clearVocabularyButton.pack(side='left')
deleteElementButton.pack(side='left')

space1.pack()
vocabularyFrame.pack()
vocabularyTree.pack()

# searching block
space4.pack()
searchFrame.pack()
searchLabel.pack(side='left')
searchEntry.pack(side='left')
space41.pack(side='left')
searchButton.pack(side='left')
clearSearchButton.pack(side='left')

root.mainloop()

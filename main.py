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
    "мн": "plur"

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
    # род
    gender = ''
    # число
    number = ''


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
        gender = doc.createElement('gender')
        case = doc.createElement('case')
        number = doc.createElement('number')

        text1 = doc.createTextNode(i.lexeme)
        text2 = doc.createTextNode(i.normal_form)
        text3 = doc.createTextNode(i.POS)
        text4 = doc.createTextNode(i.gender)
        text5 = doc.createTextNode(i.case)
        text6 = doc.createTextNode(i.number)

        lexeme.appendChild(text1)
        normalized.appendChild(text2)
        pos.appendChild(text3)
        gender.appendChild(text4)
        case.appendChild(text5)
        number.appendChild(text6)

        word.appendChild(lexeme)
        word.appendChild(normalized)
        word.appendChild(pos)
        word.appendChild(gender)
        word.appendChild(case)
        word.appendChild(number)

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

    parse_text_from_file(file_str)
    update_vocabulary()


def parse_text_from_file(string: str):
    ignore_symbols = [',', ':', ';', '{', '}']
    string = string[0:(len(string)-2)]
    for i in ignore_symbols:
        string = string.replace(i, ' ')
    text = string.split(' ')
    while text.__contains__(''):
        text.remove('')
    words = []
    counter = 0
    while counter < (len(text) - 1):
        w = Word()
        w.lexeme = text[counter]
        counter = counter + 1
        w.normal_form = text[counter]
        counter = counter + 1
        w.POS = text[counter]
        counter = counter + 1
        w.case = text[counter]
        counter = counter + 1
        w.gender = text[counter]
        counter = counter + 1
        w.number = text[counter]
        counter = counter + 1
        words.append(w)

    words.sort(key=lambda x: x.lexeme, reverse=True)

    for lex in words:
        add_flag = True
        for j in main_dictionary:
            if lex is j:
                add_flag = False
        if add_flag:
            main_dictionary.append(lex)


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
        word.case = i.getElementsByTagName("case")[0].childNodes[0].nodeValue
        word.gender = i.getElementsByTagName("gender")[0].childNodes[0].nodeValue
        word.number = i.getElementsByTagName("number")[0].childNodes[0].nodeValue
        main_dictionary.append(word)

    update_vocabulary()


def create_vocabulary_from_text_field():
    text = inputText.get(1.0, END).replace('\n', '')
    parse_from_text_field(text)
    update_vocabulary()


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
        w.case = morph.lat2cyr(temp.tag.case)
        w.gender = morph.lat2cyr(temp.tag.gender)
        w.number = morph.lat2cyr(temp.tag.number)
        words.append(w)

    words.sort(key=lambda x: x.lexeme, reverse=True)

    for lex in words:
        add_flag = True
        for j in main_dictionary:
            if lex is j:
                add_flag = False
        if add_flag:
            main_dictionary.append(lex)


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
                                                 word.POS, word.gender, word.case, word.number))


def clear_vocabulary():
    vocabularyTree.delete(*vocabularyTree.get_children())
    main_dictionary.clear()


if __name__ == '__main__':
    print(extract_text_from_pdf('sample.pdf'))


HELPTEXT = '''                    

    Программа предназначена для для обработки текстов на руском языке.

    Проверяет текст на наличие слов, определяет их характеристики и на их основе
делает вывод о возможной роли конкретного слова в составе предложения (если
существительное в именительномо падеже, то возм. подлежащее).

    Для сортировки по значениям в отдельных столбцах таблицы нажимать на названия 
столбцов.

    Поддерживаемые форматы входных текстовых файлов - pdf.

    Для хранения данных словаря используется формат .dict (переименованный .xml).

    При считывании данных из текстового файла и из текстового поля данные добавляются 
в активный словарь.При загрузке имеющегося словаря активный словарь очищается и 
перезаполняется данными из загружаемого

'''


def show_help():
    mb.showinfo(title="Помощь", message=HELPTEXT)


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
                              columns=("Лексема", "Основа", "Часть речи", "Род", "Падеж", "Число"),
                              selectmode='browse', height=11)
vocabularyTree.heading('Лексема', text="Лексема", anchor=W)
vocabularyTree.heading('Основа', text="Основа", anchor=W)
vocabularyTree.heading('Часть речи', text="Часть речи", anchor=W)
vocabularyTree.heading('Род', text="Род", anchor=W)
vocabularyTree.heading('Падеж', text="Падеж", anchor=W)
vocabularyTree.heading('Число', text="Число", anchor=W)
vocabularyTree.column('#0', stretch=NO, minwidth=0, width=0)
vocabularyTree.column('#1', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#2', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#3', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#4', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#5', stretch=NO, minwidth=347, width=200)
vocabularyTree.column('#6', stretch=NO, minwidth=347, width=200)

# space2 = Label(root, text='\n')
# editingFrame = Frame(root, bg='grey', bd=5)
# tagEditingLabel = Label(editingFrame, text=' Тэги: ', width=14, height=2, bg='grey', fg='white')
# tagEditingEntry = Entry(editingFrame, width=23)
# roleEditingLabel = Label(editingFrame, text=' Роль: ', width=10, height=2, bg='grey', fg='white')
# roleEditingEntry = Entry(editingFrame, width=23)
# space21 = Label(editingFrame, text='      ', bg='grey')
# editButton = Button(editingFrame, text='Изменить', width=8, height=2, bg='grey')

space3 = Label(root, text='\n')
addingFrame = Frame(root, bg='grey', bd=5)
lexAddingLabel = Label(addingFrame, text=' Лексема: ', width=14, height=2, bg='grey', fg='white')
lexAddingEntry = Entry(addingFrame, width=23)
tagAddingLabel = Label(addingFrame, text=' Тэги: ', width=14, height=2, bg='grey', fg='white')
tagAddingEntry = Entry(addingFrame, width=23)
roleAddingLabel = Label(addingFrame, text=' Роль: ', width=10, height=2, bg='grey', fg='white')
roleAddingEntry = Entry(addingFrame, width=23)
space31 = Label(addingFrame, text='      ', bg='grey')
addButton = Button(addingFrame, text='Добавить', width=8, height=2, bg='grey')

space4 = Label(root, text='\n')
searchFrame = Frame(root, bg='grey', bd=5)
searchLabel = Label(searchFrame, text=' Запрос: ', width=14, height=2, bg='grey', fg='white')
searchEntry = Entry(searchFrame, width=23)
space41 = Label(searchFrame, text='      ', bg='grey')
searchButton = Button(searchFrame, text='Найти', width=8, height=2, bg='grey')
clearSearchButton = Button(searchFrame, text='Сброс', width=8, height=2, bg='grey')

createVocabularyButton_textFile.config(command=open_file_to_read)
createVocabularyButton_textField.config(command=create_vocabulary_from_text_field)
clearVocabularyButton.config(command=clear_vocabulary)
deleteElementButton.config(command=delete_item)
searchButton.config(command=get_search_result)
clearSearchButton.config(command=update_vocabulary)
#
# editButton.config(command=update_item)
# addButton.config(command=add_item)

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

# editing block
# space2.pack()
# editingFrame.pack()
# tagEditingLabel.pack(side='left')
# tagEditingEntry.pack(side='left')
# roleEditingLabel.pack(side='left')
# roleEditingEntry.pack(side='left')
# space21.pack(side='left')
# editButton.pack(side='left')

# adding block
space3.pack()
addingFrame.pack()
lexAddingLabel.pack(side='left')
lexAddingEntry.pack(side='left')
tagAddingLabel.pack(side='left')
tagAddingEntry.pack(side='left')
roleAddingLabel.pack(side='left')
roleAddingEntry.pack(side='left')
space31.pack(side='left')
addButton.pack(side='left')

# searching block
space4.pack()
searchFrame.pack()
searchLabel.pack(side='left')
searchEntry.pack(side='left')
space41.pack(side='left')
searchButton.pack(side='left')
clearSearchButton.pack(side='left')

root.mainloop()

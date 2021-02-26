#https://opensource.com/sites/default/files/ebooks/pythonscriptingwithscribus.pdf

import fileinput
import os

os.system('yes | cp -rf poster/templates/template.sla poster/template.sla')

your_title=input("Write here your title (or press enter):\n")
your_text=input("Write here your description of your poster (or press enter):\n")

with fileinput.FileInput("poster/template.sla", inplace=True) as file:
    for line in file:
        print(line.replace('template_text', your_text), end='')

with fileinput.FileInput("poster/template.sla", inplace=True) as file:
    for line in file:
        print(line.replace('title_template', your_title), end='')

try:
    os.system('scribus --python-script poster/scripts/sla_to_pdf.py')
except:
    print("You need Scribus version 1.5 or higher to convert the .sla file to .pdf \n"
          "see for example: "
          "https://sourceforge.net/projects/scribus/files/scribus-devel/1.5.5/scribus-1.5.5-windows-x64.exe/download")
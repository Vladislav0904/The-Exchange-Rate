import pandas as pd
import csv
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

data = pd.read_html("https://www.finanz.ru/indeksi/diagramma-realnogo-vremeni/micex", header=0, encoding='utf-8')
string = str(data[3]).strip()
string = 'Наименование Курс Изменение Время' + '\n' + string
string = string.split('\n')

for i in range(len(string)):
    if i == 0:
        pass
    elif i == 1:
        string[i] = string[i][:len(string[i]) - 24]
    else:
        string[i] = string[i][:len(string[i]) - 24][2:].lstrip()
data = []
for i in range(len(string)):
    data.append(string[i].split())
for i in data:
    if data.index(i) != 0:
        if i[1] != '500' and i[1].isdigit():
            pass
        else:
            i[0] = f'{i[0]} {i[1]}'
            del i[1]
        if i[1].isdigit() and (',' in i[2] and '%' not in i[2]):
            i[1] = f'{i[1]} {i[2]}'
            del i[2]
        if i[1].isdigit():
            i[1] = i[1][:2] + ',' + i[1][2:]


with open('price.csv', 'w', newline='', encoding='Windows-1251') as csvfile:
    writer = csv.writer(
        csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in range(len(data)):
        writer.writerow(data[i])

for i in range(len(data)):
    data[i] = '    '.join(data[i])
print('\n'.join(data))


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ExchangeRate.ui', self)
        self.loadTable('price.csv')

    def loadTable(self, table_name):
        with open(table_name, encoding="Windows-1251") as csvfile:
            reader = csv.reader(csvfile,
                                delimiter=';', quotechar='"')
            title = next(reader)
            self.table1.setColumnCount(len(title))
            self.table1.setHorizontalHeaderLabels(title)
            self.table1.setRowCount(0)
            for i, row in enumerate(reader):
                self.table1.setRowCount(
                    self.table1.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.table1.setItem(
                        i, j, QTableWidgetItem(elem))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
import pandas as pd
import csv
import sys
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


def scrap_the_data():
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
            if ('EUR/' in i[0] or 'USD/' in i[0] or 'CHF/' in i[0]) and i[1].isdigit():
                i[1] = i[1][:2] + ',' + i[1][2:]
            elif i[1].isdigit() and len(i[1]) <= 4:
                i[1] = i[1][:2] + ',' + i[1][2:]
            elif i[1].isdigit() and len(i[1]) >= 5:
                i[1] = i[1][:3] + ',' + i[1][3:]
    return data


def get_csv(data):
    with open('price.csv', 'w', newline='', encoding='Windows-1251') as csvfile:
        writer = csv.writer(
            csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(data)):
            writer.writerow(data[i])


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        uic.loadUi('ExchangeRate.ui', self)
        self.loadTable()
        self.loadTable2()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.loadTable)

    def loadTable(self):
        self.timer.start()
        data = scrap_the_data()
        title = data[0]
        del data[0]
        self.table1.setColumnCount(len(title))
        self.table1.setHorizontalHeaderLabels(title)
        self.table1.setRowCount(0)
        for i, row in enumerate(data):
            self.table1.setRowCount(
                self.table1.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table1.setItem(
                    i, j, QTableWidgetItem(elem))

    def loadTable2(self):
        data1 = scrap_cb_data()
        title1 = data1[0]
        del data1[0]
        self.table2.setColumnCount(len(title1))
        self.table2.setHorizontalHeaderLabels(title1)
        self.table2.setRowCount(0)
        for i, row in enumerate(data1):
            self.table2.setRowCount(
                self.table2.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table2.setItem(
                    i, j, QTableWidgetItem(elem))
        self.table2.resizeColumnsToContents()


def scrap_cb_data():
    data1 = pd.read_html("https://www.cbr.ru/currency_base/daily/", header=0, encoding='utf-8')
    string = str(data1[0]).strip()
    string = string.split('\n')
    for i in range(len(string)):
        string[i] = string[i].split()
    del string[-2:]
    for i in range(len(string)):
        if i == 0:
            del string[0][4]
        else:
            del string[i][3]
    string[0][0] = f'{string[0][0]} {string[0][1]}'
    string[0][1] = f'{string[0][2]} {string[0][3]}'
    del string[0][2]
    del string[0][2]
    for i in range(len(string)):
        if i != 0:
            if string[i][3].isalpha() and string[i][4].isalpha() and len(string[i]) <= 6:
                string[i][3] = f'{string[i][3]} {string[i][4]}'
                del string[i][4]
            elif 6 < len(string[i]) < 8:
                string[i][3] = f'{string[i][3]} {string[i][4]} {string[i][5]}'
                del string[i][4]
                del string[i][4]
            elif len(string[i]) == 8:
                string[i][3] = f'{string[i][3]} {string[i][4]} {string[i][5]} {string[i][6]}'
                del string[i][4], string[i][5]
                del string[i][4]

            if len(string[i][4]) > 6:
                string[i][4] = string[i][4][:3] + ',' + string[i][4][3:]
            else:
                string[i][4] = string[i][4][:2] + ',' + string[i][4][2:]
    for i in range(len(string)):
        if i != 0:
            del string[i][0]
    return string


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())

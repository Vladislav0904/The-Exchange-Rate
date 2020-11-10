import pandas as pd
import csv
import sys
from urllib import error
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPixmap, QBrush
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QErrorMessage, QLabel
import datetime
import sqlite3

CUR_KOT = {'USD': 'ЗОЛОТО' 'СЕРЕБРО' 'МЕДЬ' 'НЕФТЬ' 'BTC' 'BCC',
           'Index': 'Индекс ММВБ' 'Индекс PTC' 'DOW.J' 'NAS100' 'S&P 500' 'NIKKEI' 'DAX' 'ESTX50'}


def scrap_the_data():
    try:
        data = pd.read_html("https://www.finanz.ru/indeksi/diagramma-realnogo-vremeni/micex", header=0,
                            encoding='utf-8')
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
        data_cur = data[9:15]
        data_in = data[1:8]
        data_met = data[16:]
        title = data[0]
        return data_cur, data_in, data_met, title
    except error.URLError:
        return 1


def scrap_cb_data():
    try:
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
    except error.URLError:
        e = QErrorMessage()
        e.showMessage('Не удалось подключиться к ресурсам. Проверьте подключение к интернету.')
        return 1


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        uic.loadUi('ExchangeRate.ui', self)
        self.loadTable()
        self.loadTable2()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.loadTable)
        self.saveCB.clicked.connect(self.get_csv_cb)
        self.saveRT.clicked.connect(self.get_csv)
        self.checkBox.stateChanged.connect(self.clickBox1)
        self.checkBox_2.stateChanged.connect(self.clickBox1)
        self.checkBox_3.stateChanged.connect(self.clickBox1)
        self.pixmap = QPixmap('calculate.png')
        self.image = QLabel(self)
        self.image.move(475, 30)
        self.image.resize(250, 150)
        self.image.setPixmap(self.pixmap)
        self.result1.clicked.connect(self.calc_clicked)
        self.result1_2.clicked.connect(self.calc_clicked_cb)
        self.bd_add.clicked.connect(self.save_bd)
        self.bd_add_2.clicked.connect(self.save_bd_2)

    def loadTable(self):
        self.timer.start()
        data = []
        unready_data = scrap_the_data()
        if unready_data != 1:
            if self.checkBox.isChecked():
                for i in unready_data[0]:
                    data.append(i)
            if self.checkBox_2.isChecked():
                for i in unready_data[2]:
                    data.append(i)
            if self.checkBox_3.isChecked():
                for i in unready_data[1]:
                    data.append(i)
            title = unready_data[3]
            self.table1.setColumnCount(len(title))
            self.table1.setHorizontalHeaderLabels(title)
            self.table1.setRowCount(0)
            for i, row in enumerate(data):
                self.table1.setRowCount(
                    self.table1.rowCount() + 1)
                for j, elem in enumerate(row):
                    item1 = QTableWidgetItem(elem)
                    if '-' in elem and '%' in elem:
                        item1.setForeground(QBrush(QColor(255, 0, 0)))
                    elif '%' in elem:
                        item1.setForeground(QBrush(QColor(23, 200, 69)))
                    self.table1.setItem(
                        i, j, item1)

    def loadTable2(self):
        data1 = scrap_cb_data()
        if data1 != 1:
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

    def get_csv(self):
        with open(f'Exchange rate {datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.csv',
                  'w', newline='', encoding='Windows-1251') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [self.table1.horizontalHeaderItem(i).text()
                 for i in range(self.table1.columnCount())])
            for i in range(self.table1.rowCount()):
                row = []
                for j in range(self.table1.columnCount()):
                    item = self.table1.item(i, j)
                    if item is not None:
                        row.append(item.text())
                writer.writerow(row)

    def get_csv_cb(self):
        with open(f'CB Exchange Rate {datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.csv',
                  'w', newline='', encoding='Windows-1251') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [self.table2.horizontalHeaderItem(i).text()
                 for i in range(self.table2.columnCount())])
            for i in range(self.table2.rowCount()):
                row = []
                for j in range(self.table2.columnCount()):
                    item = self.table2.item(i, j)
                    if item is not None:
                        row.append(item.text())
                writer.writerow(row)

    def clickBox1(self, state):
        self.loadTable()

    def calc_clicked(self):
        try:
            budget = self.lineEdit.text()
            currency = self.lineEdit_2.text()
            if currency in CUR_KOT.get('Index') and currency != '':
                raise TypeError
            info_cur = scrap_the_data()[0]
            info_met = scrap_the_data()[2]
            for i in info_cur:
                if currency.upper() in i[0].upper():
                    multiplier = i[1].replace(',', '.').replace(' ', '')
            for i in info_met:
                if currency.upper() in i[0].upper():
                    multiplier = i[1].replace(',', '.').replace(' ', '')
            if currency.upper() in CUR_KOT.get('USD'):
                USD = info_cur[0][1].replace(',', '.')
                multiplier = eval(f'{multiplier} * {USD}')
            result = float(budget) // float(multiplier)
            self.lineEdit_3.setText(f'{str(result)}')
        except TypeError:
            self.lineEdit_3.setText('Вы ввели биржевой индекс.')
        except Exception:
            self.lineEdit_3.setText('Некорректный формат данных')

    def calc_clicked_cb(self):
        try:
            amount = self.lineEdit_5.text()
            currency = self.lineEdit_6.text()
            info_cur = scrap_cb_data()
            for i in info_cur:
                if currency.upper() in i[1].upper() or currency.upper() in i[2].upper():
                    multiplier = i[3].replace(',', '.').replace(' ', '')
            self.lineEdit_4.setText(f'{eval(f"{amount} * {multiplier}")}')
        except Exception:
            self.lineEdit_4.setText('Некорректный формат данных')

    def save_bd(self):
        csv_row = self.bd.text()
        for i in range(self.table1.rowCount()):
            if i == int(csv_row) - 1:
                row = []
                for j in range(self.table1.columnCount()):
                    item = self.table1.item(i, j)
                    if item is not None:
                        row.append(item.text())

        con = sqlite3.connect('exchange_rate.sqlite')
        cur = con.cursor()
        result = cur.execute(f'''
          INSERT INTO realtime_kot(currency, rate, change_time)
            VALUES((select id from realtime_currencies where name = '{row[0]}'),
            '{row[1]}', '{row[3]}') ''').fetchall()
        con.commit()
        con.close()

    def save_bd_2(self):
        csv_row = self.bd_2.text()
        for i in range(self.table2.rowCount()):
            if i == int(csv_row) - 1:
                row = []
                for j in range(self.table2.columnCount()):
                    item = self.table2.item(i, j)
                    if item is not None:
                        row.append(item.text())
        con = sqlite3.connect('exchange_rate.sqlite')
        cur = con.cursor()
        result = cur.execute(f'''
          INSERT INTO cb_rates(currency, rate, change_time)
            VALUES((select id from cb_currencies where name = '{row[2]}'),
            '{row[3]}', '{datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}') ''').fetchall()
        con.commit()
        con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    if scrap_the_data() == 1:
        e = QErrorMessage()
        e.setWindowTitle('Network Error')
        e.showMessage('Не удалось подключиться к ресурсам. Проверьте подключение к интернету.')
    else:
        ex.show()
    sys.exit(app.exec())

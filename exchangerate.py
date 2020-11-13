import pandas as pd
import csv
import sys
from urllib import error
from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPixmap, QBrush
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QErrorMessage, QLabel
import datetime
import sqlite3

CUR_KOT = {'USD': 'ЗОЛОТО' 'СЕРЕБРО' 'МЕДЬ' 'НЕФТЬ' 'BTC' 'BCC',
           'Index': 'Индекс ММВБ' 'Индекс PTC' 'DOW.J' 'NAS100' 'S&P 500' 'NIKKEI' 'DAX' 'ESTX50'}


def scrap_the_data():  # Функция для парсинга таблицы с сайта биржи
    try:
        data = pd.read_html("https://www.finanz.ru/indeksi/diagramma-realnogo-vremeni/micex", header=0,
                            encoding='utf-8')
        string = str(data[3]).strip()
        string = 'Наименование Курс Изменение Время' + '\n' + string
        string = string.split('\n')  # Получаем сырой материал

        for i in range(len(string)):  # избавляемся от лишних символов
            if i == 0:
                pass
            elif i == 1:
                string[i] = string[i][:len(string[i]) - 24]
            else:
                string[i] = string[i][:len(string[i]) - 24][2:].lstrip()
        data = []
        for i in range(len(string)):
            data.append(string[i].split())
        for i in data:  # обработка значений и возвращение потерянных запятых
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
        return data_cur, data_in, data_met, title  # возвращаем данные, поделенные на фильтры и заголовки столбцов
    except error.URLError:  # если нет подключения возвращаем сигнал о том, что нужно вывести ошибку
        return 1


def scrap_cb_data():  # Функция для парсинга таблицы с сайта центрального банка
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
    except error.URLError:  # если нет подключения возвращаем сигнал о том, что нужно вывести ошибку
        return 1


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        uic.loadUi('ExchangeRate.ui', self)  # Подргружаем дизайн
        self.pixmap = QPixmap('calculate.png')  # Загружаем картинку
        self.pixmap.scaled(235, 100, Qt.KeepAspectRatio)
        self.image = QLabel(self)
        self.image.move(690, 75)
        self.image.resize(235, 100)
        self.image.setPixmap(self.pixmap)
        self.loadTable()  # Подгружаем таблицу с биржевыми котировками
        self.loadTable2()  # Подгружаем таблицу с курсами ЦБ
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.loadTable)
        self.saveCB.clicked.connect(self.get_csv_cb)
        self.saveRT.clicked.connect(self.get_csv)
        self.checkBox.stateChanged.connect(self.refresh_table)
        self.checkBox_2.stateChanged.connect(self.clickBox1)
        self.checkBox_3.stateChanged.connect(self.clickBox1)
        self.result1.clicked.connect(self.calc_clicked)
        self.result1_2.clicked.connect(self.calc_clicked_cb)
        self.bd_add.clicked.connect(self.save_bd)
        self.bd_add_2.clicked.connect(self.save_bd_2)

    def loadTable(self):
        self.timer.start()  # запускаем таймер
        data = []
        unready_data = scrap_the_data()  # получаем данные
        if unready_data != 1:  # с помощью проверок фильтруем информацию
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
            for i, row in enumerate(data):  # загружаем готовую информацию в таблицу
                self.table1.setRowCount(
                    self.table1.rowCount() + 1)
                for j, elem in enumerate(row):
                    item1 = QTableWidgetItem(elem)
                    if '-' in elem and '%' in elem:  # выделяем изменения цветом
                        item1.setForeground(QBrush(QColor(255, 0, 0)))
                    elif '%' in elem:
                        item1.setForeground(QBrush(QColor(23, 200, 69)))
                    self.table1.setItem(
                        i, j, item1)

    def loadTable_cb(self):
        data1 = scrap_cb_data()  # получаем данные
        if data1 != 1:
            title1 = data1[0]
            del data1[0]
            self.table2.setColumnCount(len(title1))  # сбор таблицы
            self.table2.setHorizontalHeaderLabels(title1)
            self.table2.setRowCount(0)
            for i, row in enumerate(data1):
                self.table2.setRowCount(
                    self.table2.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.table2.setItem(
                        i, j, QTableWidgetItem(elem))
            self.table2.resizeColumnsToContents()

    def get_csv(self):  # функция для сохранения таблицы с котировками в .csv файл
        with open(f'Exchange rate {datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.csv',  # добавляем время
                  'w', newline='', encoding='Windows-1251') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  # Пишем данные в файл
                [self.table1.horizontalHeaderItem(i).text()
                 for i in range(self.table1.columnCount())])
            for i in range(self.table1.rowCount()):
                row = []
                for j in range(self.table1.columnCount()):
                    item = self.table1.item(i, j)
                    if item is not None:
                        row.append(item.text())
                writer.writerow(row)

    def get_csv_cb(self):  # функция для сохранения таблицы с курсом ЦБ в .csv файл
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

    def refresh_table(self, state):  # Функция, которая обновляет данные при выборе фильтра
        self.loadTable()

    def calc_clicked(self):  # Функция для рассчетов связанных с котировками
        try:
            budget = self.lineEdit.text()
            currency = self.lineEdit_2.text()
            if currency in CUR_KOT.get('Index') and currency != '':  # Если пользователь ввел индекс выдаем ошибку
                raise TypeError
            info_cur = scrap_the_data()[0]
            info_met = scrap_the_data()[2]
            for i in info_cur:
                if currency.upper() == i[0].upper()[:3]:
                    multiplier = i[1].replace(',', '.').replace(' ', '')
            for i in info_met:
                if currency.upper() in i[0].upper():
                    multiplier = i[1].replace(',', '.').replace(' ', '')
            if currency.upper() in CUR_KOT.get('USD'):  # Если курс в долларах, переводим все в рубли
                USD = info_cur[0][1].replace(',', '.')
                multiplier = eval(f'{multiplier} * {USD}')
            result = float(budget) // float(multiplier)
            self.lineEdit_3.setText(f'{str(result)}')
        except TypeError:
            self.lineEdit_3.setText('Вы ввели биржевой индекс.')
        except Exception:  # Если пользователь вводит неподходящие данные выдаем ошибку
            self.lineEdit_3.setText('Некорректный формат данных')

    def calc_clicked_cb(self):  # Функция для рассчетов связанных с курсами ЦБ
        try:
            amount = self.lineEdit_5.text()
            currency = self.lineEdit_6.text()
            info_cur = scrap_cb_data()
            for i in info_cur:
                if currency.upper() in i[1].upper() or currency.upper() in i[2].upper():
                    multiplier = i[3].replace(',', '.').replace(' ', '')
            self.lineEdit_4.setText(f'{eval(f"{amount} * {multiplier}")}')
        except Exception:  # Если пользователь вводит неподходящие данные выдаем ошибку
            self.lineEdit_4.setText('Некорректный формат данных')

    def save_bd(self):  # Функция для записи котировок в базу данных
        try:
            csv_row = self.bd.text()
            if int(csv_row) > self.table1.rowCount():
                raise ValueError
            else:
                for i in range(self.table1.rowCount()):  # ищем нужную запись в таблице
                    if i == int(csv_row) - 1:
                        row = []
                        for j in range(self.table1.columnCount()):
                            item = self.table1.item(i, j)
                            if item is not None:
                                row.append(item.text())
                con = sqlite3.connect('exchange_rate.sqlite')  # подключаемся к БД
                cur = con.cursor()
                result = cur.execute(f'''
                  INSERT INTO realtime_kot(currency, rate, change_time)
                    VALUES((select id from realtime_currencies where name = '{row[0]}'),
                    '{row[1]}', '{row[3]}') ''').fetchall()
                con.commit()
                con.close()
        except ValueError:  # Если пользователь вводит неподходящие данные выдаем ошибку
            self.bd.setText('Некорректные данные')

    def save_bd_cb(self):  # Функция для записи курсов ЦБ в базу данных
        try:
            csv_row_cb = self.bd_2.text()
            if int(csv_row_cb) > self.table2.rowCount():
                raise ValueError
            else:
                for i in range(self.table2.rowCount()):  # ищем нужную запись в таблице
                    if i == int(csv_row_cb) - 1:
                        row = []
                        for j in range(self.table2.columnCount()):
                            item = self.table2.item(i, j)
                            if item is not None:
                                row.append(item.text())
            con = sqlite3.connect('exchange_rate.sqlite')  # подключаемся к БД
            cur = con.cursor()
            result = cur.execute(f'''
              INSERT INTO cb_rates(currency, rate, change_time)
                VALUES((select id from cb_currencies where name = '{row[2]}'),
                '{row[3]}', '{datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}') ''').fetchall()
            con.commit()
            con.close()
        except ValueError:  # Если пользователь вводит неподходящие данные выдаем ошибку
            self.bd_2.setText('Некорректные данные')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    if scrap_the_data() == 1:  # если все таки подключиться не удалось, показываем ошибку вместо окна
        e = QErrorMessage()
        e.setWindowTitle('Network Error')
        e.showMessage('Не удалось подключиться к ресурсам. Проверьте подключение к интернету.')
    else:
        ex.show()
    sys.exit(app.exec())

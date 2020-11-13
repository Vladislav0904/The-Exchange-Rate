﻿# Пояснительная записка к проекту "The Exchange Rate" 

Автор проекта: Карасев Владислав


## Идея проекта
 **Главная идея и цель проекта**  - создать приложение-компаньон, которое представляет в наглядном виде основные биржевые котировки и курс валют, установленный центральным банком, а также помогать в анализе и хранении полученных данных.

## Описание технологий

 - **Функции** scrap_the_data и scrap_cb_data отвечают за парсинг данных посредствам pandas
 
 - **Методы**
      - loadTable и loadTable2 отвечают за подгрузку csv таблиц в каждую из    вкладок приложения
	 - get_csv и get_csv_cb позволяют предоставить пользователю возможность сохранить любую из csv таблиц с указанием времени.


 - **События UI**
    - clickBox1 обновляет таблицу после применения фильтров
    - calc_clicked и calc_clicked_cb производят вычисления 
    *(расчет того, сколько  можно купить валюты по курсу в реальном времени на определенный бюджет и расчет суммы, требуемой для покупки n единиц валюты по курсу ЦБ )*
    - save_bd и save_bd_2 сохраняют запись, выбранную пользователем по номеру строки в таблице в базу данных  с помощью запроса
 ## Библиотеки
 
 1. **pandas** - высокоуровневая библиотека для анализа данных. В проекте используется для упрощенного парсинга данных.   
 **Составляющие, нужные для работы библиотеки:**
 
	 - beautifulsoup4, html5lib, lxml - библиотеки для парсинга данных
	 - click  - библиотека для удобного представления информации в терминале
	-  soupsieve - доп. пакет для beautifulsoup4
	- six - библиотека, требуемая для работы pandas
	- numpy - основа pandas, математическая библиотека
	- webencodings - питон-реализация стандарта кодирования WHATWG
2. **PyQt5** - библиотека для создания графического интерфейса и взаимодействия с ним.
**Дополнительные библиотеки QT:**
	- PyQt5-sip
	 - pyqt5-tools  - библиотека, позволяющая создавать свои .ui файлы
3. Встроенные библиотеки **datetime, csv** и **sqlite3**
>**Note**: Все библиотеки можно установить с помощью файла requirements.txt из репозитория проекта.

## Описание реализации
Для реализации основной задачи - наглядного отображения курсов используем библиотеку **pandas**. Обрабатываем данные с помощью нашей функции и приводим их к нужному виду. Если же ресурсы недоступны или отсутствует подключение к интернету, программа отобразит GUI окно с ошибкой. 
После этого мы заносим в таблицу результат, а также наглядно показываем изменения. С помощью заранее подготовленной в **QT5 Designer** ui формы предоставляем пользователю возможность работать с данными. 
Во-первых, так как человеку, интересующемуся торгами на бирже почти всегда не нужен контроль над всеми котировки были введены простейшие фильтры по типу котировок, выбор которых происходит с помощью **чек-боксов** .
Во-вторых, с помощью элементов **lineEdit** и **pushButton**, а также объекта **QPixmap** были созданы свои мини-калькуляторы для каждой из вкладов, в соответствии с предназначением каждой из вкладок.
Также, пользователь может сохранить любую из таблиц в csv файл, благодаря модулю **csv** , а программа сама подпишет дату и время в название.
Если полная таблица пользователю не нужна, то благодаря модулю **sqlite3** после ввода всего лишь одного введенного номера в поле, программа с помощью запроса в базу данных сохранит всю нужную информацию. 
## Скриншоты приложения

 
![Котировки в реальном времени](https://imgur.com/HuHB0uA.png)

![Курс ЦБ](https://imgur.com/Ec7clSA.png)

![Error](https://imgur.com/uyyzYqt.png)


import pandas as pd
import csv

data = pd.read_html("https://www.finanz.ru/indeksi/diagramma-realnogo-vremeni/micex", header=0, encoding='utf-8')
string = str(data[3]).strip()
string = string.split('\n')
for i in range(len(string)):
    if i == 0:
        string[i] = string[i][:len(string[i]) - 24]
    else:
        string[i] = string[i][:len(string[i]) - 24][2:].lstrip()
data = []
for i in range(len(string)):
    data.append(string[i].split())
for i in data:
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
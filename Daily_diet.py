import sys

from PyQt6.QtGui import QFont
from googletrans import Translator  # импорт модуля для перевода
import requests  # импорт модуля для совершения запросов в веб-базу данных
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
import sqlite3
import random


class DailyDiet(QWidget):
    def __init__(self):  # инициализация
        super().__init__()
        uic.loadUi('Qt_ui.ui', self)  #
        self.a = 0  # переменная для проверки правильности вводимых данных
        self.cre.clicked.connect(self.check)
        self.names = [self.proteins, self.fats, self.carbs]  # список названий текстовых табличек виджета
        self.values = [self.first, self.second, self.third]  # список полей куда вводятся данные
        self.bre = []  # список еды на завтрак
        self.lu = []  # список еды на обед
        self.din = []  # список еды на ужин
        self.pr = 0  # создаю переменную для подсчета белков
        self.f = 0  # создаю переменную для подсчета жиров
        self.ca = 0  # создаю переменную для подсчета углеводов

    def bd(self, req):  # функция для создания запроса в базу данных
        lst = []  # пока что пустой список подходящих по условию блюд
        table = sqlite3.connect('food.sqlite')  # соединение с базой данных
        cur = table.cursor()  # создание курсора
        result = cur.execute(req).fetchall()  # выполнение запроса и создание списка результатов
        for el in result:
            lst.append(el)  # добавление блюд в список
        return lst  # возврат списка блюд

    def get_protein(self, name):  # функция получает блюда с высоким содержанием белка
        c = f'SELECT * FROM {name} WHERE name IN (SELECT name FROM high_protein_products)'  # sql запрос
        return sorted(self.bd(c), key=lambda x: x[2])[::-1]  # возврат списка блюд,
        # отсортированного по содержанию белка по убыванию

    def get_fat(self, name):  # функция получает блюда с высоким содержанием жиров
        c = f'SELECT * FROM {name} WHERE name IN (SELECT name FROM high_fat_products)'  # sql запрос
        return sorted(self.bd(c), key=lambda x: x[2])[::-1]  # возврат списка блюд,
        # отсортированного по содержанию жиров по убыванию

    def get_carb(self, name):  # функция получает блюда с высоким содержанием углеводов
        c = f'SELECT * FROM {name} WHERE name IN (SELECT name FROM high_carb_products)'  # sql запрос
        return sorted(self.bd(c), key=lambda x: x[2])[::-1]  # возврат списка блюд,
        # отсортированного по содержанию углеводов по убыванию

    def count_calories(self):  # функция для подсчета калорий
        try:
            self.protein = int(self.first.toPlainText())  # получение количества белка
            self.fat = int(self.second.toPlainText())  # получение количества жиров
            self.carb = int(self.third.toPlainText())  # получение количества углеводов
            self.calories = self.protein * 4 + self.fat * 9 + self.carb * 4  # подсчет калорий
            self.proteins.setText('Блюдо на завтрак (Ваш выбор)')  # обновление текстового поля
            self.fats.setText('Блюдо на обед (Ваш выбор)')  # обновление текстового поля
            self.carbs.setText('Блюдо на ужин (Ваш выбор)')  # обновление текстового поля
            self.label.setText('Введите (по желанию):')
            for el in self.values:
                el.setPlainText('')  # поля для ввода становятся пустыми
            self.cre.setText('Составить рацион')  # меняется текст кнопки
            self.hello.setText('') # удаление надписи "Здравствуйте"
            self.a = 1  # маркер того, что данные введены верно

        except ValueError:  # проверка на то, что в поле для ввода вводится число
            for el in self.values:
                if el.toPlainText().isdigit() is False:  # проверка на число
                    el.setPlainText('Введите число')  # обновление поля, с введенным не числовым значением

    def translate(self, word):  # функция для перевода текста
        translator = Translator()  # переменная класса Translator
        translated = translator.translate(word, src='ru', dest='en')  # переведенное значение
        return translated.text  # возврат переведенного текста

    def request(self, name):  # функция для создания запроса в веб базу данных
        query = self.translate(name)  # блюдо, которое надо найти
        my_api = '77efcd09'  # мой api-ключ
        serv_api = '26bbc3baa1c704c2014548eb7aee5807'  # api-ключ сервера
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"  # ссылка, куда будет отправлен запрос

        headers = {  # заголовки
            "Content-Type": "application/json",  # формат данных
            "x-app-id": my_api,  # мой ключ
            "x-app-key": serv_api  # ключ сервера
        }

        body = {  # тело запроса
            "query": query,
            "timezone": "US/Eastern"  # оставляем US время, т.к. хостинг сайта находиться в США
        }

        response = requests.post(url, json=body, headers=headers)  # сам запрос

        if response.status_code == 200:  # если запрос успешен, то
            data = response.json()  # распаковываем файл
            nutr = data['foods']  # создаю переменную для данных о блюде
            proteins = nutr[0]['nf_protein']  # получаю информация о белках в этом блюде
            carbs = nutr[0]['nf_total_carbohydrate']  # получаю информацию об углеводах в этом блюде
            fats = nutr[0]['nf_total_fat']  # получаю информацию о жирах в этом блюде
            kal = proteins * 4 + carbs * 4 + fats * 9  # подсчет калорий этого блюда
            self.carb -= carbs  # обновление количества углеводов, которые нужно съесть
            self.ca += carbs  # подсчет всех углеводов
            self.protein -= proteins  # обновление количества белков, которые нужно съесть
            self.pr += proteins  # подсчет всех белков
            self.fat -= fats  # обновление количества жиров, которые нужно съесть
            self.f += fats  # подсчет всех жиров
            self.calories -= kal  # обновление количества калорий, которые нужно съесть
            weight = nutr[0]['serving_weight_grams']  # получение веса продукта
            return f'{name} - {weight} г'  # возвращает строку в виде: название продукта - его вес
        else:  # если не удалось найти такое блюдо, то возвращает соответствующую строку
            return f'Не удалось найти блюдо {name}, поэтому расчеты были сделаны без его учета'  # вывод строки

    def sub_carb(self, c, p, f, name):  # функция для вычитания углеводов какого-то блюда из текущего их количества
        lst = self.get_carb(name)  # список блюд с высоким содержанием углеводов
        dish = random.choice(lst)  # выбор случайного блюда
        if c > 0 and (
                self.ca <= self.carb or self.pr <= self.protein or self.f <= self.fat):  # если сейчас углеводов > 0, то
            a = c / dish[4]  # происходит подсчет коэффицента, на который нужно умножить вес блюда,
            # для того чтобы съесть нужное количество углеводов
            self.ca += c  # подсчет всех углеводов
            p -= round(dish[2] * a)  # вычитание белков, содержащихся в этом блюде
            self.pr += round(dish[2] * a)  # подсчет всех белков

            f -= round(dish[3] * a)  # вычитание жиров, содержащихся в этом блюде
            self.f += round(dish[3] * a)  # подсчет всех жиров
            val = round(a * int(dish[1]))  # вес блюда
            if val != 0:  # если он не равен нулю, то
                return f'{dish[0]} - {round(a * int(dish[1]))} г'  # возвращается строка в формате: название - вес
        return ''  # иначе возврат пустой строки

    def sub_prot(self, c, p, f, name):  # функция для вычитания белков какого-то блюда из текущего их количества
        lst = self.get_protein(name)  # список блюд с высоким содержанием белков
        dish = random.choice(lst)  # выбор случайного блюда
        if p > 0 and (
                self.ca <= self.carb or self.pr <= self.protein or self.f <= self.fat):  # если сейчас белков > 0, то
            a = p / dish[2]  # происходит подсчет коэффицента, на который нужно умножить вес блюда,
            # для того чтобы съесть нужное количество белков
            self.pr += p  # подсчет всех белков
            c -= round(dish[4] * a)  # вычитание углеводов, содержащихся в этом блюде
            self.ca += round(dish[4] * a)  # подсчет всех углеводов
            f -= round(dish[3] * a)  # вычитание жиров, содержащихся в этом блюде
            self.f += round(dish[3] * a)  # подсчет всех жиров
            val = round(a * int(dish[1]))  # вес блюда
            if val != 0:  # если он не равен нулю, то
                return f'{dish[0]} - {round(a * int(dish[1]))} г'  # возвращается строка в формате: название - вес
        return ''  # иначе возврат пустой строки

    def sub_fat(self, c, p, f, name):  # функция для вычитания жиров какого-то блюда из текущего их количества
        lst = self.get_fat(name)  # список блюд с высоким содержанием жиров
        dish = random.choice(lst)  # выбор случайного блюда
        if f > 0 and (
                self.ca <= self.carb or self.pr <= self.protein or self.f <= self.fat):  # если сейчас жиров > 0, то
            a = f / dish[3]  # происходит подсчет коэффицента, на который нужно умножить вес блюда,
            # для того чтобы съесть нужное количество жиров
            self.f += f  # подсчет всех жиров
            p -= round(dish[2] * a)  # вычитание белков, содержащихся в этом блюде
            self.pr += round(dish[2] * a)  # подсчет всех белков
            c -= round(dish[4] * a)  # вычитание углеводов, содержащихся в этом блюде
            self.ca += round(dish[4] * a)  # подсчет всех углеводов
            val = round(a * int(dish[1]))  # вес блюда
            if val != 0:  # если он не равен нулю, то
                return f'{dish[0]} - {round(a * int(dish[1]))} г'  # возвращается строка в формате: название - вес
        return ''  # иначе возврат пустой строки

    def breakfast(self):  # функция заполняет список еды на завтрак
        name = 'breakfast'  # маркер, того, что это завтрак для других функций
        c = self.sub_carb(self.carb_b, self.prot_b, self.fat_b, name)  # вычитание углеводов и возврат нужного блюда
        p = self.sub_prot(self.carb_l, self.prot_b, self.fat_b, name)  # вычитание белков и возврат нужного блюда
        f = self.sub_fat(self.carb_l, self.prot_l, self.fat_b, name)  # вычитание жиров и возврат нужного блюда
        lst = [c, p, f]  # список дополнительных блюд
        for el in lst:
            self.bre.append(el)  # заполнение списка еды на завтрак

    def lunch(self):  # функция заполняет список еды на обед
        name = 'lunch'  # маркер того, что это обед
        f = self.sub_fat(self.carb_l, self.prot_l, self.fat_l, name)  # вычитание белков и возврат нужного блюда
        c = self.sub_carb(self.carb_l, self.prot_l, self.fat_d, name)  # вычитание углеводов и возврат нужного блюда
        p = self.sub_prot(self.carb_d, self.prot_l, self.fat_d, name)  # вычитание жиров и возврат нужного блюда
        lst = [c, p, f]  # список блюд
        for el in lst:
            self.lu.append(el)  # заполнение списка еды

    def dinner(self):  # функция заполняет список еды на ужин
        name = 'dinner'  # маркер того, что это ужин
        p = self.sub_prot(self.carb_d, self.prot_d, self.fat_d, name)  # вычитание белков и возврат нужного блюда
        f = self.sub_fat(self.carb_d, self.prot_d, self.fat_d, name)  # вычитание углеводов и возврат нужного блюда
        c = self.sub_carb(self.carb_d, self.prot_d, self.fat_d, name)  # вычитание жиров и возврат нужного блюда
        lst = [c, p, f]  # список блюд
        for el in lst:
            self.din.append(el)  # заполнение еды на ужин

    def output(self):  # функция вывода блюд
        self.racio.setText('Ваш рацион на день:')  # вывод надписи над полями для ввода
        self.proteins.setText('Блюда на завтрак:')  # обновление текстового поля
        self.fats.setText('Блюда на обед:')  # обновление текстового поля
        self.carbs.setText('Блюда на ужин:')  # обновление текстового поля
        zavtrak = ''  # создание пустой строки
        for el in self.bre:
            if el != '':  # проверка на пустую строку
                zavtrak += f'{el}\n'  # заполнение строки блюдами из списка еды на завтрак
        self.first.setPlainText(zavtrak)  # обновление 1-го поля для ввода
        obed = ''  # создание пустой строки
        for el in self.lu:
            if el != '':  # проверка на пустую строку
                obed += f'{el}\n'  # заполнение строки блюдами из списка еды на обед
        self.second.setPlainText(obed)  # обновление 2-го поля для ввода
        uzhin = ''  # создание пустой строки
        for el in self.din:
            if el != '':  # проверка на пустую строку
                uzhin += f'{el}\n'  # заполнение строки блюдами из списка еды на ужин
        self.third.setPlainText(uzhin)  # обновление 3-го поля для ввода
        self.label.setText('')  # удаление надписи слева вверху
        self.cre.deleteLater()  # удаление кнопки, освобждает место под вывод кбжу
        self.ca = int(self.ca)
        self.pr = int(self.pr)
        self.f = int(self.f)
        self.out = QLabel(self)  # создаю лэйбл
        self.out.setFixedSize(651, 200)  # задаю размер для него
        self.out.move(330, 580)  # задаю координаты
        font = QFont('MS Shell Dlg 2', 18)  # выбираю шрифт
        self.out.setFont(font)  # задаю лэйблу выбранный шрифт
        calories = self.ca * 4 + self.f * 9 + self.pr * 4  # считаю калории
        self.out.setText(
            f'   Итого:\n\tКалории - {calories}\n \tБелки - {self.pr}\n \tЖиры - {self.f}\n \tУглеводы - {self.ca}'
        )  # вывожу тест в лэйбл
        self.out.setVisible(True)  # делаю текст видимым

    def create_diet(self):  # функция составляет итоговый рацион на день
        lst = [self.first.toPlainText(), self.second.toPlainText(), self.third.toPlainText()]  # список введенных блюд
        try:
            for el in lst:
                if el.isdigit():  # если введена пустая строка или число
                    raise ValueError  # вызов ошибки
            for i, el in enumerate(lst):
                if el != '':
                    a = self.request(el)  # результат запроса по введенному блюду
                    if i == 0:  # если блюдо введено на завтрак
                        self.bre.append(a)  # добавление в список еды на завтрак
                    elif i == 1:  # если блюдо введено на обед
                        self.lu.append(a)  # добавление в список еды на обед
                    else:  # если блюдо введено на ужин
                        self.din.append(a)  # добавление в список еды на ужин
            self.carb_b, self.fat_b, self.prot_b = (
                self.carb * 0.35, self.fat * 0.2, self.protein * 0.2
            )  # бжу на завтрак
            self.carb_l, self.fat_l, self.prot_l = (
                self.carb * 0.3, self.fat * 0.18, self.protein * 0.2
            )  # бжу на обед
            self.carb_d, self.fat_d, self.prot_d = (
                self.carb * 0.15, self.fat * 0.1, self.protein * 0.3
            )  # бжу на ужин
            self.breakfast()  # заполнение списка еды на завтрак
            self.lunch()  # заполнение списка еды на обед
            self.dinner()  # заполнение списка еды на ужин
            self.output()  # вывод рациона на экран


        except ValueError:  # Установка сообщения об ошибке в текстовые поля
            for el in self.values:
                if el.toPlainText().isdigit():
                    el.setPlainText('Введите название блюда в формате строки')

    def check(self):
        if self.a == 1:  # если данные введены правильно, то создается рацион
            self.create_diet()
        elif self.a == 0:  # если данные введены неверно, они вводятся повторно
            self.count_calories()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DailyDiet()
    ex.show()
    sys.exit(app.exec())

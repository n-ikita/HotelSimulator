import pandas as pd
from random import random


class Date:
    """
    Makes object of date from string
    """
    months_len = {1: 31, 2: 28, 3: 31,
                  4: 30, 5: 31, 6: 30,
                  7: 31, 8: 31, 9: 30,
                  10: 31, 11: 30, 12: 31}

    def __init__(self, date_str='0.0.0'):
        """
        Makes an instance of date
        :param date_str: str date in format 'x.x.xx' or 'xx.xx.xx'
        """
        self.day, self.month, self.year = map(int, date_str.split('.'))

    def __repr__(self):
        return f'{("0" + str(self.day))[-2:]}.{("0" + str(self.month))[-2:]}.{("0" + str(self.year))[-2:]}'

    def __add__(self, other: int):
        """
        Makes available adding a few days to date
        :param other:
        :return: Date
        """
        if isinstance(other, int) and other >= 0:
            return Date(f'{self.day + other}.{self.month}.{self.year}')
        else:
            raise TypeError('Type of second element must be int')

    def __lt__(self, other):
        return self.day + self.month * 30 + self.year * 365 < \
            other.day + other.month * 30 + other.year * 365

    def __gt__(self, other):
        return self.day + self.month * 30 + self.year * 365 > \
            other.day + other.month * 30 + other.year * 365

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

    def get_dates(self, num: int) -> list:
        return [self + i for i in range(num)]


class Customer:
    """
    Makes customers and has a list of all customers
    """
    arrive_date: Date
    all_customers = []
    first_date = Date()
    dates = set()

    def __init__(self, booking_date, last_name, first_name, middle_name, quantity, arrive_date, days, max_sum):
        self.booking_date = Date(booking_date)
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.quantity = quantity
        self.arrive_date = Date(arrive_date)
        self.days = int(days)
        self.max_sum = int(max_sum)
        Customer.all_customers.append(self)
        Customer.dates.add(str(self.booking_date))
        for i in range(self.days):
            Customer.dates.add(str(self.arrive_date + i))
        if Customer.first_date > self.booking_date or str(Customer.first_date) == '00.00.00':
            Customer.first_date = self.booking_date

    def __repr__(self):
        return f'{self.booking_date} {self.last_name} {self.first_name} {self.middle_name} ' \
               f'{self.quantity} {self.arrive_date} {self.days} {self.max_sum}'


class Room:
    """
    Makes a room and has a list of all rooms
    """
    rooms = []

    def __init__(self, number, type_room, max_people, comfort):
        self.number = number
        self.type_ = type_room
        self.max_people = max_people
        self.comfort = comfort
        Room.rooms.append(self)

    def __repr__(self):
        return f'{self.number} {self.max_people}-местный {self.type_} {self.comfort}'


class Hotel:
    """
    Class of hotel, that includes all rooms, data and numbers accorded to hotel,
    and can make a calendar of occupancy of rooms
    """

    prices = {'одноместный': 2900,
              'двухместный': 2300,
              'полулюкс': 3200,
              'люкс': 4100}

    coefficients = {'стандарт': 1.0,
                    'стандарт_улучшенный': 1.2,
                    'апартамент': 1.5}

    foods = {0: 'без питания', 280: 'завтрак', 1000: 'полупансион'}

    discount = 0.7

    fail_probability = 0.25

    def __init__(self, rooms: list):
        self.rooms = rooms
        self.calendar = pd.DataFrame([{
            'max people': room.max_people,
            'basic cost': self.prices[room.type_],
            'multiplier': self.coefficients[room.comfort],
            'total cost': int(room.max_people) * self.prices[room.type_] * self.coefficients[room.comfort]}
            for room in self.rooms], index=[room.number for room in self.rooms])

    def create_calendar(self, first_date: Date):
        """
        Makes calendar from all rooms and dates of customers staying
        :param first_date: first day of hotel model working
        :return: None
        """

        self.calendar = pd.DataFrame([{
            'max people': room.max_people,
            'basic cost': self.prices[room.type_],
            'multiplier': self.coefficients[room.comfort],
            'total cost': int(room.max_people) * self.prices[room.type_] * self.coefficients[room.comfort]}
            for room in self.rooms], index=[room.number for room in self.rooms])
        date = first_date
        for day in range(Date.months_len[first_date.month]):
            if str(date) in Customer.dates:
                self.calendar[str(date)] = 0
            date += 1

    def add_customer(self, customer: Customer, print_info=False):
        """
        Makes fields of customer's staying occupied in calendar
        :param customer: customer adding to calendar
        :param print_info: True if you want to print the info of customer's addition
        :return: revenue from customer (positive) or lost revenue (negative)
        """
        cost = 0
        number = 0
        food_type = ''
        sorted_calendar = self.calendar.sort_values(['max people', 'total cost'])

        for row in sorted_calendar[sorted_calendar['max people'] == customer.quantity].iterrows():
            empty = True
            for day in customer.arrive_date.get_dates(int(customer.days)):
                if row[1][str(day)] != 0:
                    empty = False
                    break

            for food in self.foods.keys():
                if cost < row[1]['total cost'] + food <= int(customer.max_sum) and empty:
                    cost = row[1]['total cost'] + food
                    number = row[0]
                    food_type = self.foods[food]

        if not number:

            for row in sorted_calendar[sorted_calendar['max people'] == str(int(customer.quantity) + 1)].iterrows():
                empty = True
                for day in customer.arrive_date.get_dates(int(customer.days)):
                    if row[1][str(day)] != 0:
                        empty = False
                        break

                for food in self.foods.keys():
                    if cost < row[1]['total cost'] * self.discount + food <= int(customer.max_sum) and empty:
                        cost = row[1]['total cost'] * self.discount + food
                        number = row[0]
                        food_type = Hotel.foods[food]

        if number:
            if random() >= self.fail_probability:
                if print_info:
                    print(f'{customer} заселился в номер:\n', *[room for room in self.rooms if room.number == number],
                          f'\nза {cost}р. в варианте {food_type}')
                for day in customer.arrive_date.get_dates(int(customer.days)):
                    self.calendar.at[number, str(day)] = 1
                return cost

            if print_info:
                print(f'{customer} отказался от предложения:\n', *[room for room in self.rooms
                                                                   if room.number == number],
                      f'\nза {cost}р. в варианте {food_type}')
            return -customer.max_sum

        if print_info:
            print(f'для посетителя: \n{customer} \nне удалось найти подходящий номер')
        return -customer.max_sum

    def to_csv(self):
        """
        Makes csv file from hotel's calendar
        :return: None
        """
        self.calendar.to_csv('hotel_calendar.csv')

    def to_excel(self):
        """
        Makes xlsx file from hotel's calendar
        :return: None
        """
        self.calendar.to_excel('hotel_calendar.xlsx')

    def run_day(self, current_day: Date, print_info=True):
        """
        Adds a group of customers by their date of booking and counts metrics
        :param current_day: customers' date of booking
        :param print_info: True if you want to print metrics
        :return: revenue and lost revenue per day
        """
        customers = [cust for cust in Customer.all_customers if cust.booking_date == current_day]
        revenue = 0
        lost_revenue = 0

        for customer in customers:
            finance_addition = self.add_customer(customer)
            if finance_addition > 0:
                revenue += finance_addition
            else:
                lost_revenue -= finance_addition

        full_rooms_count = len(self.calendar[self.calendar[str(current_day)] != 0])
        empty_rooms_count = len(self.calendar[self.calendar[str(current_day)] == 0])
        all_rooms_percent = len(self.calendar[self.calendar[str(current_day)] != 0]) / len(self.calendar) * 100
        p1_calendar = self.calendar[self.calendar['basic cost'] == 2900]
        p2_calendar = self.calendar[self.calendar['basic cost'] == 2300]
        half_lux_calendar = self.calendar[self.calendar['basic cost'] == 3200]
        lux_calendar = self.calendar[self.calendar['basic cost'] == 4100]
        one_place_rooms_percent = \
            len(p1_calendar[p1_calendar[str(current_day)] != 0]) / len(p1_calendar) * 100
        two_place_rooms_percent = \
            len(p2_calendar[p2_calendar[str(current_day)] != 0]) / len(p2_calendar) * 100
        half_lux_rooms_percent = \
            len(half_lux_calendar[half_lux_calendar[str(current_day)] != 0]) / len(half_lux_calendar) * 100
        lux_rooms_percent = \
            len(lux_calendar[lux_calendar[str(current_day)] != 0]) / len(lux_calendar) * 100

        if print_info:
            print(f'Отчет на {current_day}:\n'
                  f'Занятых номеров: {full_rooms_count}; Свободных номеров: {empty_rooms_count}\n'
                  f'Процент загруженности:\n'
                  f'Одноместные: {round(one_place_rooms_percent, 1)}%\t'
                  f'Двухместные: {round(two_place_rooms_percent, 1)}%\t'
                  f'Полулюкс: {round(half_lux_rooms_percent, 1)}%\t'
                  f'Люкс: {round(lux_rooms_percent, 1)}%\n'
                  f'Всего: {round(all_rooms_percent, 1)}%\n'
                  f'Доход: {revenue}\t'
                  f'Упущено: {lost_revenue}\n'
                  )

        return revenue, lost_revenue

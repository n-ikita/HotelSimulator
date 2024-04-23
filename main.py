import hotel_model as hm
import matplotlib.pyplot as plt
import numpy as np

with open('booking.txt', encoding='utf8') as booking_file:
    customers = booking_file.readlines()

with open('fund.txt', encoding='utf8') as rooms_file:
    rooms = rooms_file.readlines()

for room in rooms:
    hm.Room(*room.split())

for customer in customers:
    hm.Customer(*customer.split())

hotel = hm.Hotel(hm.Room.rooms)

hotel.create_calendar(hm.Customer.first_date)

all_dates = sorted(list(hm.Customer.dates))

print('Единственная переменная, на которую мы можем влиять в условиях данной модели - \n'
      'размер скидки на бронирование номера большей комфортности.\n'
      'Максимизируем доход исходя из нее\n\n'
      'Также выяснилось, что высокая вероятность отказа (25%) сильно искажает данные,\n'
      'поэтому было решено найти оптимальный размер скидки без учета этой вероятности\n\n')

discounts_giving_max_revenue = {0: 0.7, 0.25: 0.7}
optimal_discount = {}

checking_depth = input('Введите глубину проверки (Enter для значения по умолчанию: 20): ')
if not checking_depth:
    checking_depth = 20
else:
    checking_depth = int(checking_depth)

span = input('Введите диапазон проверки через пробел '
             '(Enter для значения по умолчанию: [0:100]% от общей цены): ')

if not span:
    minimal, maximal = 0, 100
else:
    minimal, maximal = map(int, span.split())

for probability in (0.25, 0):
    print('-' * 40)
    print(f'При вероятности отказа равной {probability}:\n')
    hotel.fail_probability = probability
    discounts = []
    revenues = []
    for discount in np.arange(minimal, maximal + 1, (maximal - minimal) / checking_depth):
        total_revenue, total_lost_revenue = 0, 0
        hotel.create_calendar(hm.Customer.first_date)
        hotel.discount = discount / 100
        for date in all_dates:
            day_income = hotel.run_day(date, print_info=False)
            total_revenue += day_income[0]
            total_lost_revenue += day_income[1]

        print(
            f'Предложение цены равно {round(100 * hotel.discount)}% от общей\t\t'
            f'Общий доход: {round(total_revenue, 1)}')

        discounts.append(hotel.discount)
        revenues.append(total_revenue)

    plt.plot(discounts, revenues,
             color={0.25: 'red', 0: 'blue'}[probability], label=f'при вероятности отказа {probability}')

    optimal_discount[probability] = discounts[revenues.index(max(revenues))]
    plt.scatter(optimal_discount[probability], max(revenues),
                color={0.25: 'red', 0: 'blue'}[probability])

    print(f'При вероятности отказа {probability} оптимальная цена предложения '
          f'{round(optimal_discount[probability] * 100)}% от общей')
    print(f'Отчет для цены предложения {round(optimal_discount[probability] * 100)}% от общей:')
    print('*' * 40)
    total_revenue, total_lost_revenue = 0, 0
    hotel.create_calendar(hm.Customer.first_date)
    hotel.discount = optimal_discount[probability]
    hotel.fail_probability = 0.25
    for date in all_dates:
        day_income = hotel.run_day(date)
        total_revenue += day_income[0]
        total_lost_revenue += day_income[1]

    print(f'Общий доход за период: {round(total_revenue, 1)}\n'
          f'Упущенный доход за период: {round(total_lost_revenue, 1)}\n')
    print('*' * 40)
    print('\n' * 5)

if optimal_discount[0] == optimal_discount[0.25]:
    print(f'Оптимальные множители цены для разных вероятностей отказа совпали и равны '
          f'{round(optimal_discount[0] * 100)}%\n'
          f'Следовательно, именно этот коэффициент и следует выбрать')
else:
    print(f'Оптимальный множитель цены для вероятности отказа 0.25 равен '
          f'{round(optimal_discount[0.25] * 100)}%\n'
          f'И общий доход при нем больше, чем при коэффициенте '
          f'{round(optimal_discount[0] * 100)}% для вероятности отказа 0\n'
          f'Однако, следует выбрать именно коэффициент '
          f'{round(optimal_discount[0] * 100)}%, так как в общем случае '
          f'без искажения данных он выигрышнее')

hotel.create_calendar(hm.Customer.first_date)
hotel.discount = optimal_discount[0.25]
for date in all_dates:
    hotel.run_day(date, print_info=False)

hotel.to_csv()
hotel.to_excel()
plt.xlabel('Доля цены от общей')
plt.ylabel('Доход за период')
plt.legend()
plt.show()

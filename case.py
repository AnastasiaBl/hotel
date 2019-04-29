from enum import Enum
import random


class RoomType(Enum):
    Single = 1
    Double = 2
    SemiLux = 3
    Lux = 4


class RoomComfort(Enum):
    Standart = 1
    Improved = 2
    Apartment = 3


class FoodType(Enum):
    No = 1
    Breakfast = 2
    Full = 3


types = {
    RoomType.Single: 2900,
    RoomType.Double: 2300,
    RoomType.SemiLux: 3200,
    RoomType.Lux: 4100
}

comforts = {
    RoomComfort.Standart: 1,
    RoomComfort.Improved: 1.2,
    RoomComfort.Apartment: 1.5
}

food_types = {
    FoodType.No: 0,
    FoodType.Breakfast: 280,
    FoodType.Full: 1000
}


class Room:
    def __init__(self, number, room_type, capacity, comfort):
        self.number = number
        self.room_type = room_type
        self.capacity = capacity
        self.comfort = comfort
        self.booked = [False] * 32

    def getPrice(self):
        return types[self.room_type] * comforts[self.comfort] * self.capacity

    def __str__(self):
        if self.room_type == RoomType.Single:
            type_str = "одноместный"
        elif self.room_type == RoomType.Double:
            type_str = "двухместный"
        elif self.room_type == RoomType.SemiLux:
            type_str = "полулюкс"
        elif self.room_type == RoomType.Lux:
            type_str = "люкс"

        if self.comfort == RoomComfort.Standart:
            comf_str = "стандарт"
        elif self.comfort == RoomComfort.Improved:
            comf_str = "стандарт улучшеный"
        elif self.comfort == RoomComfort.Apartment:
            comf_str = "апартамент"

        return "номер {0} {1} {2} раcсчитан на {3} чел.".format(self.number, type_str, comf_str, self.capacity)


class Order:
    def __init__(self, name, persons, day_from, day_to, budget):
        self.name = name
        self.persons = persons
        self.day_from = day_from
        self.day_to = day_to
        self.budget = budget


class Variant:
    def __init__(self, order, room):
        self.room = room
        self.food = 0
        self.price = room.getPrice()
        self.discounted = False
        total_budget = order.budget * order.persons
        if self.price > total_budget and (room.comfort != RoomComfort.Standart or room.room_type != RoomType.Single):
            self.price *= 0.7
            self.discounted = True
        self.working_variant = self.price <= total_budget

        for x in range(day_from, order.day_to):

            if room.booked[x]:
                self.working_variant = False
                return

        for food_type, food_price in sorted(food_types.items(), key=lambda x:x[1], reverse=True):

            if self.price + food_price * order.persons <= total_budget:
                self.price += food_price * order.persons
                self.food = food_type
                break

#       if self.working_variant:
#           print(room.number, "номер, цена:", self.price, "(-30%)" if self.discounted else "")


def betterVariant(a, b):


    if a is None:
        return b
    if b is None:
        return a


    if a.discounted and not b.discounted:
        return b
    elif b.discounted and not a.discounted:
        return a


    if a.room.capacity < b.room.capacity:
        return a
    elif b.room.capacity < a.room.capacity:
        return b


    if a.price < b.price:
        return b
    elif b.price < a.price:
        return a

    if a.food.value < b.food.value:
        return b
    else:
        return a


def printRoomsCount(room_type, day, prefix):
    total = 0
    free = 0

    for r in rooms:
        if r.room_type == room_type:
            total += 1
            if not r.booked[day]:
                free += 1

    print(prefix, free, "из", total)
    print()


def printDaySummary(revenue, lost_revenue, day):
    day_index = int(day[0:2])
    print("====================================================================================")
    print()
    print("Итог за", day)
    print()

    taken = 0
    free = 0
    for r in rooms:
        if r.booked[day_index]:
            taken += 1
        else:
            free += 1
    print("Количество занятых номеров:", taken)
    print()
    print("Количество свободных номеров:", free)
    print()

    print("Занятость по категориям:")
    print()
    printRoomsCount(RoomType.Single, day_index, "Одноместных:")
    printRoomsCount(RoomType.Double, day_index, "Двухместных:")
    printRoomsCount(RoomType.SemiLux, day_index, "Полулюкс:")
    printRoomsCount(RoomType.Lux, day_index, "Люкс:")

    print("Процент загруженности гостиницы:", str(round(100 * taken / len(rooms), 2)) + "%")
    print()

    print("Доход за день:", round(revenue, 2), "руб.")
    print()
    print("Упущенный доход:", round(lost_revenue, 2), "руб.")
    print()



rooms = []
with open("fund.txt", encoding="utf8") as f:
    for line in f:
        fields = line.split(" ")

        if fields[1] == "одноместный":
            room_type = RoomType.Single
        elif fields[1] == "двухместный":
            room_type = RoomType.Double
        elif fields[1] == "полулюкс":
            room_type = RoomType.SemiLux
        else:
            room_type = RoomType.Lux

        if fields[3].rstrip() == "стандарт":
            comfort = RoomComfort.Standart
        elif fields[3].rstrip() == "стандарт_улучшенный":
            comfort = RoomComfort.Improved
        else:
            comfort = RoomComfort.Apartment

        rooms.append(Room(int(fields[0]), room_type, int(fields[2]), comfort))


revenue = 0
lost_revenue = 0
previous_day = -1
with open("booking.txt", encoding="utf8") as f:
    for line in f:
        fields = line.split(" ")

        if previous_day != -1 and previous_day != fields[0]:
            printDaySummary(revenue, lost_revenue, previous_day)
            revenue = 0
            lost_revenue = 0
        previous_day = fields[0]

        day = int(fields[0][0:2])
        name = fields[1] + " " + fields[2] + " " + fields[3]
        day_from = int(fields[5][0:2])
        days = int(fields[6])

        print("------------------------------------------------------------------------------------")
        print()
        print("Поступила заявка на бронирование:")
        print()
        print(line)

        order = Order(name, int(fields[4]), day_from, day_from + days, int(fields[7]))
        best_variant = None


        for r in rooms:
            if r.capacity < order.persons:
                continue
            variant = Variant(order, r)
            if not variant.working_variant:
                continue
            best_variant = betterVariant(best_variant, variant)

        if best_variant is None:
            print("Предложений по данному запросу нет. В бронировании отказано.")
            lost_revenue += order.persons * order.budget * days
        else:
            print("Найден:")
            print()

            if best_variant.food == FoodType.No:
                food = "без питания"
            elif best_variant.food == FoodType.Breakfast:
                food = "завтрак"
            elif best_variant.food == FoodType.Full:
                food = "полупансион"
            print("{0} фактически {1} чел. {2} стоимость {3} руб./сутки".format(best_variant.room, order.persons, food, round(best_variant.price,2)))
            print()

            if random.randrange(4) == 0:
                print("Клиент отказался от варианта.")
                lost_revenue += order.persons * best_variant.price * days
            else:
                print("Клиент согласен. Номер забронирован.")
                revenue += best_variant.price * days
                for x in range(day_from, day_from + days):
                    best_variant.room.booked[x] = True

        print()


printDaySummary(revenue, lost_revenue, previous_day)

# -*- coding: utf-8 -*-


L_HOUSE = 4
L_HOTEL = 4
P_INCREASE = 200


class edification(object):

    def __init__(self, price):
        self.price = price


class service(object):

    def __init__(self, owner, price):
        self.owner = owner
        self.price = price


class water(service):
    group = 'water'


class electricity(service):
    group = 'water'


class train(service):
    group = 'train'


class ground(object):

    def __init__(self, price, p_h, p_H, l_h=L_HOUSE, l_H=L_HOTEL):
        self.owner = None
        self.price = price
        self.p_house = p_h
        self.p_hotel = p_H
        self.l_house = l_h
        self.l_hotel = l_H
        self.hotel = []
        self.house = []

    def heritage(self):
        return self.price + self.h_houses() + self.h_hotels()

    def h_hotels(self):
        return self.p_hotel * self.t_hotels()

    def h_houses(self):
        return self.p_house * self.t_houses()

    def t_hotels(self):
        return len(self.hotel)

    def t_houses(self):
        return len(self.house)

    def rent(self):
        return int(self.heritage() * P_INCREASE / 100)

    def _price_house(self, n):
        return int((self.p_house * n) * P_INCREASE / 100)

    def _price_hotel(self, n):
        return int((self.p_hotel * n) * P_INCREASE / 100)

    def price_house(self):
        return self._price_house(self.t_houses()+1 if self.t_houses() > 0 else 1)

    def price_hotel(self):
        return self._price_house(self.t_hotels()+1 if self.t_hotels() > 0 else 1)



from random import randint


class Card:
    def __init__(self, card_number=None):
        self._number = card_number if card_number else randint(1, 6)
        self._suit = self._suit()

    def _suit(self):
        if self._number == 1:
            suit = "\N{CLOUD}\N{VARIATION SELECTOR-16}"
        elif self._number == 2:
            suit = "\N{MUSHROOM}"
        elif self._number == 3:
            suit = "\N{SUNFLOWER}"
        elif self._number == 4:
            suit = "\N{LARGE GREEN SQUARE}"
        elif self._number == 5:
            suit = "\N{LARGE RED SQUARE}"
        elif self._number == 6:
            suit = "\N{WHITE MEDIUM STAR}"
        else:
            suit = "Error!"

        return suit

    def __repr__(self):
        return f"{self._suit}"

    def num(self):
        return self._number

    def suit(self):
        return self._suit


class Deck:
    def __init__(self):
        self._length = 5
        self._deck = self._create_deck()
        self.first_pair = 0
        self.second_pair = 0
        self.new_deck()

    def _create_deck(self):
        temp = [Card() for x in range(0, self._length)]
        return temp

    def _new_card(self, i):
        self._deck[i] = Card()

    def _sort_deck(self):
        self._deck.sort(key=lambda x: x.num(), reverse=True)

    def new_deck(self):
        self._deck = self._create_deck()
        self._sort_deck()

    def deck(self):
        return self._deck

    def num(self, i):
        return self._deck[i].num()

    def swap(self, i):
        for x in i:
            self._new_card(int(x) - 1)
        self._sort_deck()

    def suit(self, i):
        return self._deck[i].suit()

    def len(self):
        return self._length

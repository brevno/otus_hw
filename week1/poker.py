#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------
import itertools


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


scores = {str(i): i for i in xrange(10)}
scores.update({'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14})


def card_score(card):
    return scores[card[0]]


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    ranks = [card_score(card) for card in hand]
    return sorted(ranks, reverse=True)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits = [card[1] for card in hand]
    return len(set(suits)) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    for index, rank in list(enumerate(ranks))[1:]:
        if ranks[index-1] - rank != 1:
            return False
    return True


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    counts = {r: 0 for r in ranks}
    for rank in ranks:
        counts[rank] += 1

    valid_ranks = [rank for (rank, cnt) in counts.items() if cnt == n]

    return max(valid_ranks) if valid_ranks else None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    first_pair_rank = kind(2, ranks)
    if not first_pair_rank:
        return None
    leftover = [rank for rank in ranks if rank != first_pair_rank]
    second_pair_rank = kind(2, leftover)
    if not second_pair_rank:
        return None
    return first_pair_rank, second_pair_rank


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    all_hand_ranks = []
    for hand_5 in itertools.combinations(hand, 5):
        all_hand_ranks.append((hand_rank(hand_5), hand_5))

    return max(all_hand_ranks)[1]


def joker_expanded(joker):
    """
    Joker values generator

    :param joker: str, '?R' or '?B'
    :yield: all cards a joker can substitute
    """
    suits = 'SC' if joker[1] == 'B' else 'DH'
    for suit in suits:
        for value in '23456789TJQKA':
            yield '{}{}'.format(value, suit)


def try_all_joker_values(hand):
    jokers = [card for card in hand if card[0] == '?']
    other_cards = [card for card in hand if card[0] != '?']

    if not jokers:
        yield other_cards

    joker_generators = map(joker_expanded, jokers)
    all_joker_combinations = itertools.product(*joker_generators)
    for combination in all_joker_combinations:
        yield other_cards + list(combination)


def short_hand_from_full_hand(full_hand):
    for unwilded_hand in try_all_joker_values(full_hand):
        for hand_5 in itertools.combinations(unwilded_hand, 5):
            yield hand_5


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    ranks_for_hands = (
        (hand_rank(hand_5), hand_5)
        for hand_5 in short_hand_from_full_hand(hand)
    )
    best_rank_and_hand = max(ranks_for_hands)
    return best_rank_and_hand[1]


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'

if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()

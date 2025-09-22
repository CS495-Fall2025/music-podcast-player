from app.logic import math


def test_sum_of_zeros() -> None:
    assert 0 == math.get_sum([0, 0, 0])


def test_sum_of_none() -> None:
    assert 0 == math.get_sum([])


def test_sum_of_single_number() -> None:
    assert 3 == math.get_sum([3])


def test_sum_of_multiple_numbers() -> None:
    assert 14 == math.get_sum([7, 2, 5])


def test_product_of_none() -> None:
    assert 1 == math.get_product([])


def test_product_of_some_and_zero() -> None:
    assert 0 == math.get_product([-5, 3, 1, 4, 10, 0])


def test_product_of_single_number() -> None:
    assert 9 == math.get_product([9])


def test_product_of_multiple_numbers() -> None:
    assert 5372 == math.get_product([4, 17, 79])

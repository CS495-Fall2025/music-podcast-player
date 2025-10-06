def get_sum(numbers: list[int]) -> int:
    sum = 0

    for number in numbers:
        sum += number

    return sum


def get_product(numbers: list[int]) -> int:
    product = 1

    for number in numbers:
        product *= number

    return product

def test_get_magic_number(client) -> None:
    response = client.get("/math")
    number = response.get_json()["number"]

    assert 0 == number


def test_post_for_sum(client) -> None:
    request = [4, 7, 2]

    response = client.post("/math", json=request)
    sum = response.get_json()["sum"]

    assert 13 == sum


def test_post_for_product(client) -> None:
    request = [4, 7, 2]

    response = client.post("/math", json=request)
    product = response.get_json()["product"]

    assert 56 == product


def test_post_with_invalid_data_type(client) -> None:
    request = {"data": [1, 2, 3]}
    headers = {
        "Content-Type": "application/json",
    }

    response = client.post("/math", headers=headers, data=request)
    error = response.get_json()["error"]

    assert "invalid_format" == error

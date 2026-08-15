import pytest


def test_get_nonexistent_post(api_request_context):
    response = api_request_context.get("/posts/9999")

    assert response.status == 404
    assert not response.ok
    assert response.json() == {}


@pytest.mark.parametrize(
    "endpoints, ids", [("/posts/1", 1), ("/posts/2", 2), ("/posts/3", 3)]
)
def test_get_multiple_post(api_request_context, endpoints, ids):
    response = api_request_context.get(endpoints)

    assert response.ok
    body = response.json()
    assert body["id"] == ids


def test_create_post(api_request_context):
    new_post = {"title": "sample", "body": "test", "userId": 23}
    response = api_request_context.post("/posts", data=new_post)

    assert response.ok
    assert response.status == 201

    body = response.json()
    assert body["title"] == "sample"
    assert "id" in body

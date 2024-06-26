import json
import typing as t

import httpx
import pytest
import respx

from tests.utils import does_not_raise

from .expected.fastapi_app_client.apis import Api as FastApiAppClient
from .expected.fastapi_app_client.models import Document, Foo, PaginatedFoo


client_base_url = "https://domain.tld"
client = FastApiAppClient(base_url=client_base_url)

foo_id = "00000000-0000-0000-0000-000000000000"


@respx.mock
@pytest.mark.asyncio
async def test_read_foo() -> None:
    """
    Check that the client sends a GET request to the correct endpoint
    and returns the expected model (parsing the response content correctly).
    """

    expected_response = Foo(field_1="field_1", field_2=1)

    route = respx.get(f"{client_base_url}/api/foo/{foo_id}")
    route.mock(return_value=httpx.Response(200, content=expected_response.json()))

    response = await client.read_foo_api_foo__foo_id__get(foo_id=foo_id)

    assert route.called
    assert response == expected_response


@respx.mock
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expectation, expected_response",
    [
        (200, does_not_raise(), Foo(field_1="field_1", field_2=1, field_3=1.1).dict()),
        (400, pytest.raises(httpx.HTTPStatusError), {"detail": "Bad Request"}),
        (401, pytest.raises(httpx.HTTPStatusError), {"detail": "Unauthorized"}),
        (403, pytest.raises(httpx.HTTPStatusError), {"detail": "Forbidden"}),
        (404, pytest.raises(httpx.HTTPStatusError), {"detail": "Not Found"}),
        (500, pytest.raises(httpx.HTTPStatusError), {"detail": "Internal Server Error"}),
    ],
)
async def test_read_foo_raises(
    status_code: int, expectation: t.Any, expected_response: t.Any
) -> None:
    """
    Check that the client sends a GET request to the correct endpoint
    and raises an exception when the response status code is not 2xx.
    """

    route = respx.get(f"{client_base_url}/api/foo/{foo_id}")
    route.mock(return_value=httpx.Response(status_code, content=json.dumps(expected_response)))

    with expectation:
        await client.read_foo_api_foo__foo_id__get(foo_id=foo_id)


@respx.mock
@pytest.mark.asyncio
async def test_create_foo() -> None:
    foo = Foo(field_1="field_1", field_2=1)

    route = respx.post(f"{client_base_url}/api/foo")
    route.mock(return_value=httpx.Response(200, content=foo.json()))

    response = await client.create_foo_api_foo_post(body=foo)

    assert route.called
    assert response == foo


@respx.mock
@pytest.mark.asyncio
async def test_upload_doc() -> None:
    file_data = ("file_name", "file")
    document = Document(field_1="field_1")

    route = respx.post(f"{client_base_url}/api/foo/{foo_id}/documents")
    route.mock(return_value=httpx.Response(200, content=document.json()))

    response = await client.upload_doc_api_foo__foo_id__documents_post(
        file=file_data, foo_id=foo_id
    )

    assert route.called
    assert response == document


@respx.mock
@pytest.mark.asyncio
async def test_list_foos() -> None:
    paginated_response = PaginatedFoo(
        results=[Foo(field_1="field_1", field_2=1)],
        offset=0,
        limit=10,
        size=1,
    )

    route = respx.get(f"{client_base_url}/api/foo")
    route.mock(return_value=httpx.Response(200, content=paginated_response.json()))

    response = await client.list_foos_api_foo_get()

    assert route.called
    assert response == paginated_response

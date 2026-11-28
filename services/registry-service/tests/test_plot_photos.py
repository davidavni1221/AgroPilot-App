"""POST and GET /v1/plots/{id}/photo. S3 is replaced by FakeS3, so no test talks to AWS."""
import pytest
from botocore.exceptions import ClientError, NoCredentialsError

import main
from tests.test_api import DEMO_FARM, NORTH_BLOCK, assert_problem

EAST_BLOCK = "d9a4e2c1-5e3f-4b6a-9c33-2e7f4a803003"
NORTH_KEY = f"{DEMO_FARM}/{NORTH_BLOCK}/photo"
JPEG = b"\xff\xd8\xff\xe0 a small jpeg"


class FakeS3:
    """Keeps objects in a dict. With fail set, every call raises it, like a boto3 client would."""

    def __init__(self):
        self.objects = {}
        self.calls = 0
        self.fail = None

    def put_object(self, Bucket, Key, Body, ContentType):
        self.calls += 1
        if self.fail:
            raise self.fail
        self.objects[(Bucket, Key)] = (Body, ContentType)

    def get_object(self, Bucket, Key):
        self.calls += 1
        if self.fail:
            raise self.fail
        body, _ = self.objects[(Bucket, Key)]
        return {"Body": FakeBody(body)}


class FakeBody:
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


@pytest.fixture
def s3(monkeypatch):
    monkeypatch.setenv("AWS_S3_BUCKET", "test-bucket")
    monkeypatch.setenv("AWS_REGION", "eu-north-1")
    fake = FakeS3()
    monkeypatch.setattr(main, "s3_client", lambda: fake)
    return fake


def upload(client, plot_id=NORTH_BLOCK, data=JPEG, content_type="image/jpeg"):
    return client.post(f"/v1/plots/{plot_id}/photo", files={"file": ("north.jpg", data, content_type)})


S3_ERRORS = [
    pytest.param(NoCredentialsError(), id="no-credentials"),
    pytest.param(ClientError({"Error": {"Code": "AccessDenied", "Message": "denied"}}, "PutObject"), id="access-denied"),
]


# --- Upload ---
@pytest.mark.parametrize("content_type", ["image/jpeg", "image/png", "image/webp"])
def test_upload_photo(client, s3, content_type):
    response = upload(client, content_type=content_type)
    assert response.status_code == 201
    assert response.json() == {"plot_id": NORTH_BLOCK, "key": NORTH_KEY, "content_type": content_type}
    assert s3.objects[("test-bucket", NORTH_KEY)] == (JPEG, content_type)


def test_second_upload_overwrites(client, s3):
    upload(client, data=b"first", content_type="image/jpeg")
    response = upload(client, data=b"second", content_type="image/png")
    assert response.status_code == 201
    assert s3.objects[("test-bucket", NORTH_KEY)] == (b"second", "image/png")
    photo = client.get(f"/v1/plots/{NORTH_BLOCK}/photo")
    assert photo.content == b"second"
    assert photo.headers["content-type"] == "image/png"


def test_upload_unknown_plot(client, s3):
    assert_problem(upload(client, plot_id="no-such-plot"), 404, "NOT_FOUND")
    assert s3.calls == 0


@pytest.mark.parametrize("data, content_type", [
    pytest.param(b"", "image/jpeg", id="empty"),
    pytest.param(JPEG, "text/plain", id="not-an-image"),
    pytest.param(JPEG, "image/gif", id="gif"),
    pytest.param(b"x" * (5 * 1024 * 1024 + 1), "image/jpeg", id="over-5-mb"),
])
def test_upload_invalid_file(client, s3, data, content_type):
    assert_problem(upload(client, data=data, content_type=content_type), 422, "VALIDATION")
    assert s3.calls == 0


def test_upload_exactly_5_mb(client, s3):
    assert upload(client, data=b"x" * (5 * 1024 * 1024)).status_code == 201


def test_upload_without_file_field(client, s3):
    assert_problem(client.post(f"/v1/plots/{NORTH_BLOCK}/photo"), 422, "VALIDATION")
    assert s3.calls == 0


@pytest.mark.parametrize("error", S3_ERRORS)
def test_upload_s3_error_keeps_the_stored_photo(client, s3, error):
    upload(client, data=b"first", content_type="image/jpeg")
    s3.fail = error
    response = upload(client, data=b"second", content_type="image/png")
    assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"]

    s3.fail = None
    photo = client.get(f"/v1/plots/{NORTH_BLOCK}/photo")
    assert photo.content == b"first"
    assert photo.headers["content-type"] == "image/jpeg"


def test_upload_without_bucket_setting(client, s3, monkeypatch):
    monkeypatch.delenv("AWS_S3_BUCKET")
    assert_problem(upload(client), 503, "UNAVAILABLE")
    assert s3.calls == 0


def test_upload_keeps_the_plot_json_unchanged(client, s3):
    before = client.get(f"/v1/plots/{NORTH_BLOCK}").json()
    upload(client)
    assert client.get(f"/v1/plots/{NORTH_BLOCK}").json() == before


# --- Download ---
def test_get_photo(client, s3):
    upload(client)
    response = client.get(f"/v1/plots/{NORTH_BLOCK}/photo")
    assert response.status_code == 200
    assert response.content == JPEG
    assert response.headers["content-type"] == "image/jpeg"


def test_get_photo_unknown_plot(client, s3):
    assert_problem(client.get("/v1/plots/no-such-plot/photo"), 404, "NOT_FOUND")


def test_get_photo_when_plot_has_none(client, s3):
    upload(client)
    assert_problem(client.get(f"/v1/plots/{EAST_BLOCK}/photo"), 404, "NOT_FOUND")
    assert s3.calls == 1


@pytest.mark.parametrize("error", S3_ERRORS)
def test_get_photo_s3_error(client, s3, error):
    upload(client)
    s3.fail = error
    response = client.get(f"/v1/plots/{NORTH_BLOCK}/photo")
    assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"]


def test_get_photo_without_bucket_setting(client, s3, monkeypatch):
    upload(client)
    monkeypatch.delenv("AWS_S3_BUCKET")
    assert_problem(client.get(f"/v1/plots/{NORTH_BLOCK}/photo"), 503, "UNAVAILABLE")


# --- Delete plot ---
def test_delete_plot_with_photo(client, s3):
    upload(client)
    assert client.delete(f"/v1/plots/{NORTH_BLOCK}").status_code == 204
    assert_problem(client.get(f"/v1/plots/{NORTH_BLOCK}/photo"), 404, "NOT_FOUND")


# --- The real client ---
def test_s3_client_uses_the_region_setting(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "eu-north-1")
    assert main.s3_client().meta.region_name == "eu-north-1"

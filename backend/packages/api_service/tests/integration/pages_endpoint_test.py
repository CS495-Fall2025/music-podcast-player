import json
import os

import boto3
import pytest
from unittest import mock

from rss_music_api_service.auth import pkce

from helpers import ConstantResponse

CMS_BUCKET = "test-cms-bucket"


@pytest.fixture
def s3_bucket(app):
    """Create a mocked S3 bucket. moto is already active via the dynamodb fixture."""
    os.environ["RSS_PLAYER_CMS_BUCKET"] = CMS_BUCKET
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=CMS_BUCKET)
    yield s3
    del os.environ["RSS_PLAYER_CMS_BUCKET"]


@pytest.fixture
def s3_client(client, s3_bucket):
    """Flask test client with S3 available."""
    yield client


@pytest.fixture
def admin_client(client, user, custom_responses, s3_bucket):
    """Authenticated Flask test client with is_admin=True and S3 available."""
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/login"] = (
        ConstantResponse(
            status_code=200,
            json_data={
                "username": user.username,
                "id": user.id,
                "email_verified": True,
                "is_admin": True,
            },
        )
    )
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/exists"] = (
        ConstantResponse(
            status_code=200,
            json_data={"exists": "true"},
        )
    )

    verifier = "test_challenge"
    challenge = pkce.generate_code_challenge(verifier)

    response = client.get("/auth/", query_string={"code_challenge": challenge})
    assert response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "username": user.username,
            "password": "t3st_p@ssword",
            "code_verifier": verifier,
        },
    )
    assert response.status_code == 200

    del custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/login"]

    yield client


class TestGetPage:
    def test_get_returns_empty_html_when_no_content_stored(self, s3_client):
        response = s3_client.get("/pages/about")
        assert response.status_code == 200
        data = response.get_json()
        assert data["page"] == "about"
        assert data["html"] == ""

    def test_get_returns_stored_html(self, s3_client, s3_bucket):
        content = json.dumps({"html": "<h1>About Us</h1>"}).encode()
        s3_bucket.put_object(Bucket=CMS_BUCKET, Key="pages/about.json", Body=content)

        response = s3_client.get("/pages/about")
        assert response.status_code == 200
        assert response.get_json()["html"] == "<h1>About Us</h1>"

    def test_get_unknown_page_returns_404(self, s3_client):
        response = s3_client.get("/pages/unknown")
        assert response.status_code == 404

    def test_get_contact_page(self, s3_client):
        response = s3_client.get("/pages/contact")
        assert response.status_code == 200
        assert response.get_json()["page"] == "contact"


class TestPutPage:
    def test_put_requires_authentication(self, s3_client):
        response = s3_client.put("/pages/about", json={"html": "<p>content</p>"})
        assert response.status_code == 401

    def test_put_requires_admin(self, client, user, custom_responses, s3_bucket):
        # Log in as non-admin user
        custom_responses[
            f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/login"
        ] = ConstantResponse(
            status_code=200,
            json_data={
                "username": user.username,
                "id": user.id,
                "email_verified": True,
                "is_admin": False,
            },
        )
        custom_responses[
            f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/exists"
        ] = ConstantResponse(status_code=200, json_data={"exists": "true"})

        verifier = "test_challenge"
        challenge = pkce.generate_code_challenge(verifier)
        client.get("/auth/", query_string={"code_challenge": challenge})
        client.post(
            "/auth/login",
            json={
                "username": user.username,
                "password": "t3st_p@ssword",
                "code_verifier": verifier,
            },
        )
        del custom_responses[
            f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/login"
        ]

        response = client.put("/pages/about", json={"html": "<p>content</p>"})
        assert response.status_code == 403

    def test_put_saves_content(self, admin_client):
        response = admin_client.put("/pages/about", json={"html": "<p>Hello</p>"})
        assert response.status_code == 200
        assert response.get_json()["html"] == "<p>Hello</p>"

    def test_put_strips_script_tags(self, admin_client):
        response = admin_client.put(
            "/pages/about",
            json={"html": "<p>Safe</p><script>alert('xss')</script>"},
        )
        assert response.status_code == 200
        assert "<script>" not in response.get_json()["html"]
        assert "<p>Safe</p>" in response.get_json()["html"]

    def test_put_unknown_page_returns_404(self, admin_client):
        response = admin_client.put("/pages/unknown", json={"html": "<p>x</p>"})
        assert response.status_code == 404

    def test_put_missing_html_field_returns_400(self, admin_client):
        response = admin_client.put("/pages/about", json={})
        assert response.status_code == 400

    def test_put_then_get_persists_content(self, admin_client, s3_client):
        html = "<h1>Persisted</h1>"
        admin_client.put("/pages/about", json={"html": html})

        response = s3_client.get("/pages/about")
        assert response.status_code == 200
        assert response.get_json()["html"] == html

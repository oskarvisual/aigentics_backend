def test_register_and_login(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "full_name": "Owner User",
            "password": "supersecurepassword",
            "workspace_name": "Acme Corp",
            "workspace_slug": "acme-corp",
        },
    )
    assert register_response.status_code == 200
    tenant_id = register_response.json()["tenant_id"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "owner@example.com",
            "password": "supersecurepassword",
            "tenant_id": tenant_id,
        },
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()


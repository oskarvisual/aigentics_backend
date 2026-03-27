def _bootstrap_owner(client) -> tuple[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "scope@example.com",
            "full_name": "Scope Owner",
            "password": "supersecurepassword",
            "workspace_name": "Scoped Inc",
            "workspace_slug": "scoped-inc",
        },
    )
    tenant_id = register_response.json()["tenant_id"]
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "scope@example.com",
            "password": "supersecurepassword",
            "tenant_id": tenant_id,
        },
    )
    return tenant_id, login_response.json()["access_token"]


def test_workspace_header_is_required(client) -> None:
    tenant_id, token = _bootstrap_owner(client)
    response = client.get(
        "/api/v1/agents",
        headers={"Authorization": f"Bearer {token}", "X-Workspace-ID": tenant_id},
    )
    assert response.status_code == 200

    missing_header = client.get("/api/v1/agents", headers={"Authorization": f"Bearer {token}"})
    assert missing_header.status_code == 400


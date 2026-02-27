from okta_auth_mcp import server


def test_server_exports_tools() -> None:
    expected = [
        "okta_login",
        "okta_check_session",
        "okta_list_sessions",
        "okta_delete_session",
        "okta_get_cookies",
        "main",
    ]
    for name in expected:
        assert hasattr(server, name)

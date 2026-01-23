"""Authentication status and flow tools."""

from mcp.server import Server

from drchrono_mcp.auth.oauth import OAuthManager


def register_auth_tools(server: Server, oauth: OAuthManager) -> None:
    """Register authentication tools with MCP server.

    Args:
        server: MCP Server instance
        oauth: OAuth manager for authentication
    """

    @server.tool()
    async def drchrono_auth_status() -> dict:
        """Check DrChrono OAuth authentication status.

        Use this tool to:
        - Check if you're authenticated with DrChrono
        - Get the authorization URL if authentication is needed
        - See what scopes/permissions are granted

        Returns:
            Authentication status with auth_url if not authenticated
        """
        if oauth.is_authenticated:
            return {
                "authenticated": True,
                "scopes": oauth.current_scopes,
                "message": "Authenticated with DrChrono API. Ready to make requests.",
            }
        else:
            auth_url = oauth.get_authorization_url()
            return {
                "authenticated": False,
                "auth_url": auth_url,
                "message": (
                    "Not authenticated. Visit the auth_url in a browser to authorize. "
                    "After authorizing, the callback will be captured automatically."
                ),
                "instructions": [
                    "1. Open the auth_url in a web browser",
                    "2. Log in to DrChrono if prompted",
                    "3. Click 'Authorize' to grant access",
                    "4. Wait for the callback (page will show success message)",
                    "5. Call this tool again to confirm authentication",
                ],
            }

    @server.tool()
    async def drchrono_start_auth() -> dict:
        """Start the OAuth authorization flow.

        This will open a browser window for you to log in and authorize.
        After authorization, tokens will be saved automatically.

        Only use this if drchrono_auth_status shows not authenticated.

        Returns:
            Status of the auth flow initiation
        """
        if oauth.is_authenticated:
            return {
                "success": True,
                "message": "Already authenticated. No action needed.",
                "scopes": oauth.current_scopes,
            }

        try:
            auth_url = oauth.start_auth_flow(open_browser=True)
            return {
                "success": True,
                "message": "Authorization flow started. Check your browser.",
                "auth_url": auth_url,
                "instructions": (
                    "A browser window should have opened. Log in and authorize the app. "
                    "Once complete, call drchrono_auth_status to confirm."
                ),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start authorization flow.",
            }

    @server.tool()
    async def drchrono_logout() -> dict:
        """Clear stored DrChrono authentication tokens.

        Use this to:
        - Sign out of DrChrono
        - Clear stored credentials
        - Re-authenticate with different scopes

        Returns:
            Confirmation of logout
        """
        oauth.logout()
        return {
            "success": True,
            "message": "Logged out. Stored tokens have been cleared.",
        }

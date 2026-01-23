"""OAuth 2.0 Authorization Code flow for DrChrono API."""

import asyncio
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import httpx

from drchrono_mcp.auth.token_store import TokenStore
from drchrono_mcp.models.types import TokenData

# DrChrono OAuth endpoints
AUTHORIZE_URL = "https://app.drchrono.com/o/authorize/"
TOKEN_URL = "https://app.drchrono.com/o/token/"

# Default scopes for full API access
DEFAULT_SCOPES = [
    "calendar:read",
    "calendar:write",
    "patients:read",
    "patients:write",
    "patients:summary:read",
    "clinical:read",
    "clinical:write",
    "billing:read",
    "billing:patient-payment:write",
    "labs:read",
    "tasks:read",
    "tasks:write",
    "messages:read",
    "messages:write",
]


class OAuthManager:
    """Manages OAuth 2.0 flow for DrChrono API.

    Handles authorization, token exchange, and automatic refresh.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8765/callback",
        scopes: list[str] | None = None,
        token_store: TokenStore | None = None,
    ):
        """Initialize OAuth manager.

        Args:
            client_id: DrChrono API client ID
            client_secret: DrChrono API client secret
            redirect_uri: OAuth callback URL (must match DrChrono app config)
            scopes: Requested OAuth scopes. Defaults to full access.
            token_store: Token persistence. Defaults to file-based storage.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or DEFAULT_SCOPES
        self.token_store = token_store or TokenStore()
        self._tokens: TokenData | None = None

        # Try to load existing tokens
        self._tokens = self.token_store.load()

    @property
    def is_authenticated(self) -> bool:
        """Check if we have valid (non-expired) tokens."""
        if not self._tokens:
            return False
        return not self._tokens.is_expired()

    @property
    def current_scopes(self) -> list[str]:
        """Get scopes from current token."""
        if self._tokens and self._tokens.scope:
            return self._tokens.scope.split()
        return []

    def get_authorization_url(self) -> str:
        """Generate the authorization URL for user to visit.

        Returns:
            URL string for OAuth authorization
        """
        scope_string = urllib.parse.quote(" ".join(self.scopes))
        return (
            f"{AUTHORIZE_URL}"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={urllib.parse.quote(self.redirect_uri)}"
            f"&scope={scope_string}"
        )

    async def get_access_token(self) -> str:
        """Get valid access token, refreshing if needed.

        Returns:
            Valid access token string

        Raises:
            RuntimeError: If not authenticated
        """
        if not self._tokens:
            raise RuntimeError("Not authenticated. Call start_auth_flow() first.")

        if self._tokens.is_expired():
            await self.refresh_tokens()

        return self._tokens.access_token

    async def exchange_code(self, authorization_code: str) -> TokenData:
        """Exchange authorization code for tokens.

        Args:
            authorization_code: Code from OAuth callback

        Returns:
            TokenData with access and refresh tokens
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": authorization_code,
                },
            )
            response.raise_for_status()
            data = response.json()

        tokens = TokenData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_at=datetime.now() + timedelta(seconds=data["expires_in"]),
            scope=data.get("scope", ""),
        )

        self._tokens = tokens
        self.token_store.save(tokens)
        return tokens

    async def refresh_tokens(self) -> TokenData:
        """Refresh expired access token using refresh token.

        Returns:
            New TokenData with fresh access token
        """
        if not self._tokens:
            raise RuntimeError("No tokens to refresh")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self._tokens.refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()

        tokens = TokenData(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self._tokens.refresh_token),
            token_type=data.get("token_type", "Bearer"),
            expires_at=datetime.now() + timedelta(seconds=data["expires_in"]),
            scope=data.get("scope", self._tokens.scope),
        )

        self._tokens = tokens
        self.token_store.save(tokens)
        return tokens

    def start_auth_flow(self, open_browser: bool = True) -> str:
        """Start the OAuth authorization flow.

        This method starts a local HTTP server to receive the callback,
        then opens the authorization URL in the user's browser.

        Args:
            open_browser: Whether to automatically open browser

        Returns:
            Authorization URL (in case manual opening is needed)
        """
        auth_url = self.get_authorization_url()

        # Parse redirect URI for server config
        parsed = urllib.parse.urlparse(self.redirect_uri)
        port = parsed.port or 8765

        # Store reference to exchange code later
        captured_code: dict[str, str | None] = {"code": None, "error": None}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # Parse the callback URL
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)

                if "code" in params:
                    captured_code["code"] = params["code"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h1>Authorization successful!</h1>"
                        b"<p>You can close this window and return to your application.</p>"
                        b"</body></html>"
                    )
                elif "error" in params:
                    captured_code["error"] = params.get("error_description", params["error"])[0]
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        f"<html><body><h1>Authorization failed</h1>"
                        f"<p>{captured_code['error']}</p></body></html>".encode()
                    )
                else:
                    self.send_response(400)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress logging

        # Start server in background thread
        server = HTTPServer(("localhost", port), CallbackHandler)

        def serve_once():
            server.handle_request()
            server.server_close()

        thread = Thread(target=serve_once)
        thread.daemon = True
        thread.start()

        # Open browser
        if open_browser:
            webbrowser.open(auth_url)

        # Wait for callback (with timeout)
        thread.join(timeout=300)  # 5 minute timeout

        if captured_code["error"]:
            raise RuntimeError(f"OAuth error: {captured_code['error']}")

        if captured_code["code"]:
            # Exchange code for tokens synchronously
            asyncio.get_event_loop().run_until_complete(
                self.exchange_code(captured_code["code"])
            )

        return auth_url

    def logout(self) -> None:
        """Clear stored tokens."""
        self._tokens = None
        self.token_store.delete()

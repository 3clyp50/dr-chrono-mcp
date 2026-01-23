"""Secure token storage for OAuth credentials."""

import json
import os
from datetime import datetime
from pathlib import Path

from drchrono_mcp.models.types import TokenData


class TokenStore:
    """Persists OAuth tokens securely to disk.

    Tokens are stored with restrictive file permissions (600) to protect PHI access.
    """

    def __init__(self, token_file: str | None = None):
        """Initialize token store.

        Args:
            token_file: Path to token file. Defaults to ~/.drchrono/tokens.json
        """
        if token_file:
            self.token_file = Path(token_file).expanduser()
        else:
            self.token_file = Path.home() / ".drchrono" / "tokens.json"

    def save(self, tokens: TokenData) -> None:
        """Save tokens to disk with secure permissions."""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_at": tokens.expires_at.isoformat(),
            "scope": tokens.scope,
        }

        # Write with restrictive permissions
        self.token_file.write_text(json.dumps(data, indent=2))
        os.chmod(self.token_file, 0o600)

    def load(self) -> TokenData | None:
        """Load tokens from disk if they exist."""
        if not self.token_file.exists():
            return None

        try:
            data = json.loads(self.token_file.read_text())
            return TokenData(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                token_type=data.get("token_type", "Bearer"),
                expires_at=datetime.fromisoformat(data["expires_at"]),
                scope=data.get("scope", ""),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def delete(self) -> None:
        """Remove stored tokens."""
        if self.token_file.exists():
            self.token_file.unlink()

    def exists(self) -> bool:
        """Check if tokens are stored."""
        return self.token_file.exists()

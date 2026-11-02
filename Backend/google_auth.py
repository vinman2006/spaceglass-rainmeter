"""
SpaceGlass — Google OAuth 2.0 Desktop Authentication Module (Backend/google_auth.py).
Implements the official Google OAuth 2.0 InstalledAppFlow for Desktop apps:
- Minimum required scopes:
    * https://www.googleapis.com/auth/calendar.readonly
    * https://www.googleapis.com/auth/tasks
- Dynamic localhost callback port
- Protected token persistence using Windows DPAPI (CryptProtectData) when running
  on Windows, with restricted user-only file permissions (0600)
- Automatic access-token refresh and revoked-permission cleanup
- Never logs or exposes access/refresh tokens to Rainmeter skins
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import logging
import os
import platform
import stat
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from Backend.config import ConfigManager

logger = logging.getLogger("spaceglass.auth")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks",
]


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def _dpapi_encrypt(raw_bytes: bytes) -> bytes:
    """Encrypt token bytes with Windows DPAPI (CurrentUser scope) when on Windows."""
    if platform.system() != "Windows":
        return raw_bytes
    try:
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        buf = ctypes.create_string_buffer(raw_bytes, len(raw_bytes))
        blob_in = _DATA_BLOB(len(raw_bytes), buf)
        blob_out = _DATA_BLOB()
        if crypt32.CryptProtectData(
            ctypes.byref(blob_in),
            "SpaceGlassOAuthToken",
            None,
            None,
            None,
            0x01,  # CRYPTPROTECT_UI_FORBIDDEN
            ctypes.byref(blob_out),
        ):
            encrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            kernel32.LocalFree(blob_out.pbData)
            return b"DPAPI1:" + encrypted
    except Exception as exc:
        logger.warning("DPAPI encryption fallback to OS file permissions: %s", type(exc).__name__)
    return raw_bytes


def _dpapi_decrypt(stored_bytes: bytes) -> bytes:
    """Decrypt Windows DPAPI token bytes if prefixed with DPAPI1:."""
    if not stored_bytes.startswith(b"DPAPI1:"):
        return stored_bytes
    if platform.system() != "Windows":
        raise RuntimeError("Token was encrypted with Windows DPAPI and cannot be decrypted on non-Windows OS.")
    payload = stored_bytes[len(b"DPAPI1:") :]
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    buf = ctypes.create_string_buffer(payload, len(payload))
    blob_in = _DATA_BLOB(len(payload), buf)
    blob_out = _DATA_BLOB()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0x01,
        ctypes.byref(blob_out),
    ):
        raise RuntimeError("Unable to decrypt stored OAuth token via Windows DPAPI.")
    decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    kernel32.LocalFree(blob_out.pbData)
    return decrypted


class GoogleAuthError(Exception):
    """Raised when Google OAuth configuration, consent, or token refresh fails."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class GoogleAuthManager:
    """Manages Google OAuth 2.0 credentials lifecycle safely without exposing secrets."""

    def __init__(self, config_mgr: ConfigManager) -> None:
        self.config_mgr = config_mgr
        self._lock = threading.Lock()
        self._auth_in_progress = False
        self._last_error: Optional[str] = None

    @property
    def token_path(self) -> Path:
        return self.config_mgr.token_path

    def has_client_Secret_file(self) -> bool:
        return self.config_mgr.find_credentials_file() is not None

    def _load_stored_credentials(self) -> Optional[Any]:
        """Load and validate stored OAuth user credentials from protected file."""
        if not self.token_path.exists():
            return None
        try:
            from google.oauth2.credentials import Credentials

            encrypted = self.token_path.read_bytes()
            decrypted_json = _dpapi_decrypt(encrypted).decode("utf-8")
            info = json.loads(decrypted_json)
            creds = Credentials.from_authorized_user_info(info, SCOPES)
            return creds
        except Exception as exc:
            logger.warning("Stored token could not be loaded (%s). Clearing corrupt token.", type(exc).__name__)
            self._remove_token_file()
            return None

    def _save_credentials(self, creds: Any) -> None:
        """Persist OAuth credentials using DPAPI + strict 0600 file permissions."""
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = creds.to_json().encode("utf-8")
        encrypted = _dpapi_encrypt(serialized)
        tmp_path = self.token_path.with_suffix(".tmp")
        tmp_path.write_bytes(encrypted)
        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
        tmp_path.replace(self.token_path)

    def _remove_token_file(self) -> None:
        try:
            if self.token_path.exists():
                self.token_path.unlink()
        except Exception as exc:
            logger.warning("Failed to delete token file: %s", type(exc).__name__)

    def get_valid_credentials(self) -> Any:
        """
        Return valid, non-expired Google OAuth2 Credentials.
        Automatically refreshes expired tokens when a refresh_token is available.
        Raises GoogleAuthError with clear diagnostic code if unauthenticated or revoked.
        """
        with self._lock:
            creds = self._load_stored_credentials()
            if creds is None:
                if not self.has_client_Secret_file():
                    raise GoogleAuthError(
                        code="missing_client_credentials",
                        message=(
                            "Google OAuth credentials.json is missing. Place your Desktop OAuth "
                            "credentials.json in %LOCALAPPDATA%\\SpaceGlass\\credentials.json or Config/credentials.json."
                        ),
                        status_code=401,
                    )
                raise GoogleAuthError(
                    code="not_authenticated",
                    message="Google account is not connected. Click 'Connect Google Account' in SpaceGlass Settings.",
                    status_code=401,
                )

            if creds.valid:
                return creds

            if creds.expired and creds.refresh_token:
                try:
                    from google.auth.transport.requests import Request

                    creds.refresh(Request())
                    self._save_credentials(creds)
                    self._last_error = None
                    return creds
                except Exception as exc:
                    err_str = str(exc).lower()
                    if "invalid_grant" in err_str or "revoked" in err_str or "expired" in err_str:
                        self._remove_token_file()
                        self._last_error = "OAuth access was revoked or expired. Please reconnect your Google account."
                        raise GoogleAuthError(
                            code="token_revoked",
                            message=self._last_error,
                            status_code=401,
                        ) from exc
                    self._last_error = f"Token refresh failed (network or Google API error): {type(exc).__name__}"
                    raise GoogleAuthError(
                        code="refresh_failed",
                        message=self._last_error,
                        status_code=503,
                    ) from exc

            self._remove_token_file()
            raise GoogleAuthError(
                code="token_expired_no_refresh",
                message="OAuth session expired without a refresh token. Please reconnect your Google account.",
                status_code=401,
            )

    def get_auth_status(self) -> Dict[str, Any]:
        """Return safe authentication status summary (never includes raw tokens)."""
        creds_file = self.config_mgr.find_credentials_file()
        has_token = self.token_path.exists()
        authenticated = False
        token_expired = False

        if has_token:
            try:
                creds = self.get_valid_credentials()
                authenticated = bool(creds and creds.valid)
            except GoogleAuthError as exc:
                self._last_error = exc.message
                token_expired = exc.code in ("token_revoked", "token_expired_no_refresh")

        return {
            "authenticated": authenticated,
            "credentials_configured": creds_file is not None,
            "credentials_path": str(creds_file) if creds_file else None,
            "auth_in_progress": self._auth_in_progress,
            "token_expired": token_expired,
            "scopes": SCOPES,
            "last_error": self._last_error,
        }

    def start_oauth_flow(self, open_browser: bool = True, timeout_seconds: int = 180) -> Dict[str, Any]:
        """
        Run the official Google OAuth 2.0 Desktop Application flow via localhost callback.
        Uses port=0 to bind to an available ephemeral localhost port safely.
        """
        creds_file = self.config_mgr.find_credentials_file()
        if creds_file is None:
            raise GoogleAuthError(
                code="missing_client_credentials",
                message=(
                    "credentials.json not found. Download your OAuth 2.0 Desktop Client JSON from "
                    "Google Cloud Console and place it at %LOCALAPPDATA%\\SpaceGlass\\credentials.json."
                ),
                status_code=400,
            )

        if self._auth_in_progress:
            raise GoogleAuthError(
                code="auth_already_in_progress",
                message="Google OAuth sign-in is already waiting for browser authorization.",
                status_code=409,
            )

        self._auth_in_progress = True
        self._last_error = None
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(
                host="127.0.0.1",
                port=0,
                open_browser=open_browser,
                authorization_prompt_message="Please complete SpaceGlass sign-in in your web browser...",
                success_message="SpaceGlass is now connected to your Google Calendar and Google Tasks! You may close this tab.",
                timeout_seconds=timeout_seconds,
            )
            if not creds or not creds.valid:
                raise GoogleAuthError(
                    code="auth_cancelled",
                    message="Google sign-in was cancelled or did not complete before timeout.",
                    status_code=400,
                )
            with self._lock:
                self._save_credentials(creds)
            return {
                "connected": True,
                "scopes": list(creds.scopes or SCOPES),
                "message": "Successfully connected Google Calendar and Google Tasks.",
            }
        except GoogleAuthError:
            raise
        except Exception as exc:
            self._last_error = f"Google OAuth failed or was cancelled: {exc}"
            raise GoogleAuthError(
                code="oauth_flow_error",
                message=self._last_error,
                status_code=400,
            ) from exc
        finally:
            self._auth_in_progress = False

    def disconnect(self) -> Dict[str, Any]:
        """Revoke/delete stored OAuth credentials and clear local cache."""
        with self._lock:
            creds = self._load_stored_credentials()
            if creds and getattr(creds, "token", None):
                try:
                    import urllib.parse
                    import urllib.request

                    data = urllib.parse.urlencode({"token": creds.token}).encode("utf-8")
                    req = urllib.request.Request(
                        "https://oauth2.googleapis.com/revoke",
                        data=data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        method="POST",
                    )
                    urllib.request.urlopen(req, timeout=5)
                except Exception:
                    # Even if offline when disconnecting, always purge local token
                    pass
            self._remove_token_file()
            self._last_error = None
        return {
            "connected": False,
            "message": "Disconnected Google Account and deleted stored OAuth credentials.",
        }

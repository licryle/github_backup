import time
import logging
from pathlib import Path
from typing import Optional

import requests
from cryptography.fernet import Fernet
from github import Github, GithubException
from ..config import AppConfig

# GitHub CLI's Client ID - used for Device Flow
GITHUB_CLIENT_ID = "Ov23liUEh9QokkvwegCh"

def _get_fernet(cfg: AppConfig, logger: logging.Logger) -> Optional[Fernet]:
    """Initialize Fernet with the key from TOKEN_KEY_FILE."""
    if not cfg.token_key_file:
        logger.critical("TOKEN_KEY_FILE is not set. Program cannot start.")
        return None
    
    key_path = Path(cfg.token_key_file)
    if not key_path.exists():
        logger.critical(f"Encryption key file not found: {key_path}")
        return None
        
    try:
        key = key_path.read_bytes().strip()
        return Fernet(key)
    except Exception as e:
        logger.critical(f"Invalid encryption key in {key_path}: {e}")
        return None

def get_github_token(cfg: AppConfig, logger: logging.Logger) -> Optional[str]:
    """Decrypt the token from TOKEN_ENCRYPTED_FILE."""
    fernet = _get_fernet(cfg, logger)
    if not fernet:
        return None

    enc_path = Path(cfg.token_encrypted_file)
    if not enc_path.exists():
        return None
        
    try:
        encrypted_data = enc_path.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        # If decryption fails, we assume it's either corrupt or plain text where it shouldn't be
        logger.critical(f"Failed to decrypt token from {enc_path}: {e}")
        return None
def write_github_token(cfg: AppConfig, logger: logging.Logger, token: str) -> bool:
    fernet = _get_fernet(cfg, logger)
    if fernet:
        try:
            encrypted = fernet.encrypt(token.encode('utf-8'))
            Path(cfg.token_encrypted_file).write_bytes(encrypted)
            logger.info("Successfully authenticated and saved encrypted token.")
        except Exception as e:
            logger.error(f"Failed to save encrypted token: {e}")

def _perform_device_flow(logger: logging.Logger) -> Optional[str]:
    """Execute the GitHub Device Flow to get a new token."""
    logger.info("Initiating GitHub Device Flow.")
    
    try:
        resp = requests.post(
            "https://github.com/login/device/code",
            data={"client_id": GITHUB_CLIENT_ID, "scope": "repo"},
            headers={"Accept": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"Failed to connect to GitHub for device flow: {e}")
        return None

    device_code = data["device_code"]
    user_code = data["user_code"]
    url = data["verification_uri"]
    interval = data.get("interval", 5)

    auth_msg = (
        f"\n[AUTH REQUIRED]\n"
        f"1. Go to: {url}\n"
        f"2. Enter code: {user_code}\n"
        f"Warning: this requests read & write access, only read will be used.\n"
        f"Warning: the token will be stored, encrypted on your device."
    )

    logger.priority_info(auth_msg)

    logger.info("Waiting for user authorization.")
    while True:
        try:
            poll_resp = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                },
                headers={"Accept": "application/json"},
                timeout=10
            )
            poll_data = poll_resp.json()
            
            if "access_token" in poll_data:
                return poll_data["access_token"]
            
            error = poll_data.get("error")
            if error == "authorization_pending":
                time.sleep(interval)
            elif error == "slow_down":
                interval += 5
                time.sleep(interval)
            else:
                logger.error(f"Device flow failed: {error}")
                return None
        except Exception as e:
            logger.error(f"Error during token polling: {e}")
            return None

def check_auth(cfg: AppConfig, logger: logging.Logger) -> bool:
    """Validate current token or trigger Device Flow."""
    token = get_github_token(cfg, logger)
    
    def validate(t: str) -> bool:
        if not t: return False
        try:
            g = Github(t)
            # Verification: Attempt to fetch repositories
            g.get_user().get_repos().get_page(0)
            logger.info(f"Authenticated as: {g.get_user().login}")
            return True
        except Exception:
            return False

    if validate(token):
        return True

    logger.warning("No valid encrypted token found. Starting Device Flow.")
    new_token = _perform_device_flow(logger)
    
    if new_token and validate(new_token):
        write_github_token(cfg, logger, new_token)
        return True

    return False

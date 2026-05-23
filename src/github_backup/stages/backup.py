import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from github import Github, GithubException
import git
from ..config import AppConfig
from .auth import get_github_token

@dataclass
class BackupSummary:
    total: int = 0
    cloned: int = 0
    updated: int = 0
    failed: int = 0

    def __str__(self):
        return (f"\n💾Backup Summary: {self.total} repos found.\n" +
                f"✅ {self.cloned} cloned + {self.updated} updated.\n" +
                f"⚠️ {self.failed} failed.")

    @property
    def success(self) -> bool:
        return self.failed == 0

def update_repo(logger: logging.Logger, auth_url: str, gh_repo: any, repo_name: str, repo_path: str):
    repo = git.Repo(str(repo_path))
    origin = repo.remotes.origin

    # Ensure the remote URL is up to date (contains current token)
    origin.set_url(auth_url)
    origin.fetch(prune=True)

    # Perform a "hard" update to the remote HEAD
    # We try origin/HEAD first, then fall back to the default branch
    try:
        repo.git.reset('--hard', 'origin/HEAD')
    except git.GitCommandError:
        default_branch = gh_repo.default_branch
        repo.git.reset('--hard', f'origin/{default_branch}')

    # Clean any untracked files to ensure a "hard" sync
    repo.git.clean('-fd')

    logger.info(f"✅ Successfully updated and reset {repo_name}")

def backup_repos(cfg: AppConfig, logger: logging.Logger) -> Optional[BackupSummary]:
    """Clone or update GitHub repositories using PyGithub and GitPython.
    
    Ensures each repository is synced and reset to the remote's HEAD.
    """
    token = get_github_token(cfg, logger)
    if not token:
        logger.error("No valid GitHub token found. Please authenticate first.")
        return None

    if not cfg.backup_dir:
        logger.error("BACKUP_DIR is not configured.")
        return None

    backup_base = Path(cfg.backup_dir)
    if not backup_base.exists():
        backup_base.mkdir(parents=True, exist_ok=True)

    g = Github(token)
    try:
        user = g.get_user()
        logger.info(f"Fetching owned repositories for user: {user.login}")
        # Fetching all repositories where the user is the owner
        repos = user.get_repos(type='owner', sort='full_name')
    except GithubException as e:
        logger.error(f"Failed to fetch repositories from GitHub: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching repositories: {e}")
        return None

    summary = BackupSummary()
    
    for gh_repo in repos:
        summary.total += 1
        repo_name = gh_repo.full_name  # e.g., "owner/repo"
        repo_path = backup_base / repo_name
        
        # Inject token into the URL for GitPython authentication
        auth_url = gh_repo.clone_url.replace("https://", f"https://{token}@")

        try:
            if not repo_path.exists():
                logger.info(f"{summary.total}/{repos.totalCount} - Cloning {repo_name}.")
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                # Normal clone (non-mirror) to allow "hard HEAD" resets
                git.Repo.clone_from(auth_url, str(repo_path))
                logger.info(f"✅ Successfully cloned {repo_name}")
                summary.cloned += 1
            else:
                logger.info(f"{summary.total}/{repos.totalCount} - Fetching and updating {repo_name}.")
                update_repo(logger, auth_url, gh_repo, repo_name, repo_path)
                summary.updated += 1

        except Exception as e:
            # Scrub the token from any error messages before logging
            error_str = str(e).replace(token, "********")
            logger.error(f"❌ Error processing {repo_name}: {error_str}")
            summary.failed += 1

    return summary

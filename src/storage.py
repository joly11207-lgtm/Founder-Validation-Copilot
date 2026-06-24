import base64
import json
import re
import requests
import streamlit as st
from typing import Optional
from src.models import Opportunity


def _cfg():
    return {
        "token": st.secrets["GITHUB_STORAGE_TOKEN"],
        "repo": st.secrets["GITHUB_STORAGE_REPO"],
        "branch": st.secrets.get("GITHUB_STORAGE_BRANCH", "main"),
        "dir": st.secrets.get("GITHUB_STORAGE_DIR", "data/opportunities"),
    }


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _file_url(cfg: dict, filename: str) -> str:
    return f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['dir']}/{filename}"


def _index_url(cfg: dict) -> str:
    return f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['dir']}/index.json"


def _get_file(url: str, cfg: dict) -> tuple[Optional[str], Optional[str]]:
    """Returns (content, sha) or (None, None) if not found."""
    resp = requests.get(url, headers=_headers(cfg["token"]), params={"ref": cfg["branch"]}, timeout=30)
    if resp.status_code == 404:
        return None, None
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def _put_file(url: str, cfg: dict, content: str, message: str, sha: Optional[str] = None):
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": cfg["branch"],
    }
    if sha:
        payload["sha"] = sha
    resp = requests.put(url, headers=_headers(cfg["token"]), json=payload, timeout=30)
    resp.raise_for_status()


def _load_index(cfg: dict) -> tuple[list, Optional[str]]:
    content, sha = _get_file(_index_url(cfg), cfg)
    if content is None:
        return [], None
    return json.loads(content), sha


def _save_index(cfg: dict, index: list, sha: Optional[str]):
    _put_file(_index_url(cfg), cfg, json.dumps(index, indent=2), "Update opportunity index", sha)


def save_opportunity(opp: Opportunity):
    cfg = _cfg()
    # Save individual file
    filename = f"{opp.id}.json"
    url = _file_url(cfg, filename)
    _, existing_sha = _get_file(url, cfg)
    _put_file(url, cfg, json.dumps(opp.to_dict(), indent=2), f"Save opportunity: {opp.title}", existing_sha)

    # Update index
    index, index_sha = _load_index(cfg)
    summary = {
        "id": opp.id,
        "created_at": opp.created_at,
        "title": opp.title,
        "input_type": opp.input_type,
        "score": opp.score,
        "decision": opp.decision,
        "status": opp.status,
    }
    existing = next((i for i, x in enumerate(index) if x["id"] == opp.id), None)
    if existing is not None:
        index[existing] = summary
    else:
        index.insert(0, summary)
    _save_index(cfg, index, index_sha)


def load_opportunity(opp_id: str) -> Optional[Opportunity]:
    cfg = _cfg()
    url = _file_url(cfg, f"{opp_id}.json")
    content, _ = _get_file(url, cfg)
    if content is None:
        return None
    return Opportunity.from_dict(json.loads(content))


def list_opportunities() -> list[dict]:
    cfg = _cfg()
    index, _ = _load_index(cfg)
    return index


def update_status(opp_id: str, status: str):
    opp = load_opportunity(opp_id)
    if opp:
        opp.status = status
        save_opportunity(opp)



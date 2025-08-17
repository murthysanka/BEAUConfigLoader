from __future__ import annotations
from pathlib import Path
import copy
import os
import yaml

# ---------- Strict YAML loader (errors on duplicate keys) ----------
class _StrictLoader(yaml.SafeLoader):
    pass

def _construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping

_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)

# ---------- Helpers ----------
def _load_yaml(path: Path) -> dict:
    """Load YAML file or return {} if it doesn't exist."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.load(f, Loader=_StrictLoader) or {}

def _deep_merge(a: dict, b: dict) -> dict:
    """
    Merge dict b over dict a (b wins). Dicts merge recursively; lists REPLACE.
    """
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out

# ---------- Public API ----------
def load_config(
    env: str | None = None,
    config_dir: str | Path | None = None,
    *,
    use_local: bool = True,
    local_filename: str = "local.yaml",
) -> dict:
    """
    Load base.yaml, then <env>.yaml, then optional local.yaml (if present).
    Precedence: base < env < local.
    """
    env = env or os.getenv("APP_ENV", "dev")
    cfg_dir = Path(config_dir or Path(__file__).parent / "config").resolve()

    base   = _load_yaml(cfg_dir / "base.yaml")
    envcfg = _load_yaml(cfg_dir / f"{env}.yaml")
    merged = _deep_merge(base, envcfg)

    if use_local:
        local = _load_yaml(cfg_dir / local_filename)
        merged = _deep_merge(merged, local)

    merged["_meta"] = {"env": env, "loaded_from": str(cfg_dir)}
    return merged

def validate_cfg(
    cfg: dict,
    *,
    allowed_top_keys: set[str] | None = None,
    require_db_connections: bool = True,
    require_sftp_profiles: bool = True,
) -> None:
    """
    Lightweight structural checks to catch common mistakes (mis-nesting, typos).
    """
    allowed_top_keys = allowed_top_keys or {"app", "db", "sftp", "api", "secrets", "_meta"}

    extra = set(cfg.keys()) - allowed_top_keys
    if extra:
        raise ValueError(f"Unexpected top-level keys: {sorted(extra)}")

    if require_db_connections and "db" in cfg:
        if not isinstance(cfg["db"], dict) or not isinstance(cfg["db"].get("connections"), dict):
            raise ValueError("db.connections must be a mapping")

    if require_sftp_profiles and "sftp" in cfg:
        if not isinstance(cfg["sftp"], dict) or not isinstance(cfg["sftp"].get("profiles"), dict):
            raise ValueError("sftp.profiles must be a mapping")

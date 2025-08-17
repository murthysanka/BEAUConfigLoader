# config-loader

Loads `base.yaml`, overlays `<env>.yaml`, then optional `local.yaml`.
- Strict YAML (errors on duplicate keys)
- Deep merge (dicts merge, lists replace)

```python
from config_loader_util import load_config, validate_cfg

cfg = load_config(env="dev", config_dir="config")
validate_cfg(cfg)

# config_loader_util

Loads `base.yaml`, overlays `<env>.yaml`, then optional `local.yaml`.
- Strict YAML (errors on duplicate keys)
- Deep merge (dicts merge, lists replace)



=============================================================
Sample wheel package build steps
# from the util repo root
=============================================================
py -3 -m pip install --upgrade build
py -3 -m build
# copy wheel to your feed
Copy-Item .\dist\config_loader_util-0.0.0-py3-none-any.whl file:///C:/Users/Murth/OneDrive/Documents/Python%20Projects/custompackages/config_loader_util/1.2.0/"

=================================================================
#How apps consume
================================================================
#requirements.txt (option A)
PyYAML>=6.0                
config-loader-util @ file:///C:/Users/Murth/OneDrive/Documents/Python%20Projects/custompackages/config_loader_util/1.2.0/config_loader_util-0.0.0-py3-none-any.whl

pip install -r requirements.txt

#requirements.txt (option B)
PyYAML>=6.0                
config-loader-util=1.2.0

.\.venv\Scripts\pip.exe install --no-index --find-links file:///C:/Users/Murth/OneDrive/Documents/Python%20Projects/custompackages 
  -r requirements.txt


#usage in python code..

from config_loader_util import load_config, validate_cfg

cfg = load_config(env="dev", config_dir="config")
validate_cfg(cfg)
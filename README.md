# devfs-snapshot-python

a snapshot for device filesystem.

## Example

add a config file `devss.json` with following content in a **EMPTY** directory:

``` json
{
    "device": "ftp://<YOUR_PSVITA_IP>:1337",
    "remotes": [
        "ux0:/pspemu/ISO"
    ]
}
```

than run `poetry run python devss.py /path/to/devss.json`.

# LVM plugins for Icinga2/Nagios

## `icinga_lvs.py`

## Parameters

- `--command` - default `lsv`
- `--warning` - default `50`
- `--critical` - default `70`
- `--snapshot` - default none (goes through all snapshots)

```sh
python icinga_lvs.py --command='sudo lvs' --snapshot=foobar
```

Tested with:

- Python 2.7
- Python 3.4
- Python 3.6
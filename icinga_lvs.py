"""
Example of `lvs --noheadings --separator : -o` output:

lv_attr,lv_name,data_percent,metadata_percent,lv_uuid,lv_role
  -wi-ao----:backup:::fPcmj0-PQIP-A28Q-8dEw-js2R-Ch8U-KXajg4:public
  -wi-ao----:root:::eFh4eI-d9r2-XP9z-dPmP-ckaN-bUm8-GD9dnw:public
  owi-aoC---:slow_storage:99.99:4.83:eWTr4c-WCMW-2wgo-cWav-149i-XPSe-30qMCj:public,origin,thickorigin
  -wi-ao----:swap:::Mf8INv-AGYY-YuJO-DSEw-bzjU-fe6x-dWFZqV:public
  swi-aos---:virt-snapshot:1.28::cYfLtz-I43W-1sgq-TOUo-Ary1-VDvp-28HWEg:public,snapshot,thicksnapshot
"""


from __future__ import print_function

import argparse
import subprocess
import sys


def parse_lv_item(line):
    line = line.strip().split(':')
    return dict(
        lv_attr=line[0],
        lv_name=line[1],
        data_percent=float(line[2]) if line[2] != '' else 0.0,
        metadata_percent=float(line[3]) if line[3] != '' else 0.0,
        lv_uuid=line[4],
        lv_role=line[5].split(',')
    )


def get_stats(cmd):
    args = cmd.split(' ')
    args.append('--noheadings')
    args.append('--separator :')
    args.append('-o')
    output = subprocess.check_output(args)
    lines = output.decode('utf-8').splitlines()
    # Header
    del lines[0]
    for line in lines:
        yield parse_lv_item(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', type=str, default='lvs')
    parser.add_argument('--warning', type=int, default=50)
    parser.add_argument('--critical', type=int, default=70)
    parser.add_argument('--snapshot', type=str, default=None)
    args = parser.parse_args()

    snapshots = []
    performance_data = []
    for lv in get_stats(args.command):
        if 'snapshot' in lv['lv_role']:
            if args.snapshot is None:
                snapshots.append(lv)
                performance_data.append(
                    '{}:{}%'.format(lv['lv_name'], lv['data_percent']))
            elif args.snapshot == lv['lv_name']:
                snapshots.append(lv)
                performance_data.append(
                    '{}:{}%'.format(lv['lv_name'], lv['data_percent']))
    if len(snapshots) == 0:
        if args.snapshot is not None:
            print('CRITICAL - snapshot {} not found'.format(args.snapshot))
            return 2
        else:
            print('OK - no snapshots found')
            return 0
    for snapshot in snapshots:
        if snapshot['data_percent'] >= args.critical:
            print('CRITICAL -', end=' ')
            print('snapshot {} data_percent is {}'.format(snapshot['lv_name'],
                                                          snapshot['data_percent']),
                  end='|')
            print('snapshots={}'.format(','.join(performance_data)))
            return 2
        elif snapshot['data_percent'] >= args.warning:
            print('WARNING -', end=' ')
            print('snapshot {} data_percent is {}'.format(snapshot['lv_name'],
                                                          snapshot['data_percent']),
                  end='|')
            print('snapshots={}'.format(','.join(performance_data)))
            return 1
    print('OK', end='|')
    print('snapshots={}'.format(','.join(performance_data)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print('CRITICAL - {}'.format(str(e)))
        sys.exit(2)


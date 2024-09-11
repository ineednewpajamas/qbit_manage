#!/usr/bin/env python3
"""qBittorrent Manager RecycleBin Recovery."""
import argparse
import glob
import json
import logging
import os
import ruamel.yaml # type: ignore
import shutil
import sys
import time
from ruamel.yaml import YAML # type: ignore

parser = argparse.ArgumentParser(
    prog="QBM_Recovery",
    description="Move files in the RecycleBin back into place",
    epilog="Don't forget to restart qbittorrent...",
)
parser.add_argument(
    "-c",
    "--config-file",
    dest="configfiles",
    action="store",
    default="config.yml",
    type=str,
    help=(
        "This is used if you want to use a different name for your config.yml or if you want to load multiple"
        "config files using *. Example: tv.yml or config*.yml"
    ),
)
parser.add_argument(
    "-db",
    "--debug",
    dest="debug",
    help=argparse.SUPPRESS,
    action="store_true",
    default=False
)
parser.add_argument(
    "-ll",
    "--log-level",
    dest="log_level",
    action="store",
    default="INFO",
    type=str,
    help="Change your log level."
)
args = parser.parse_args()

config_files = args.configfiles
log_level = args.log_level
debug = args.debug

if debug:
    log_level = "DEBUG"

if os.path.isdir("/config") and glob.glob(os.path.join("/config", config_files)):
    default_dir = "/config"
else:
    default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

# TODO multiple configs add complexity that i'm not prepared to handle in a separate script
if "*" in config_files:
    print(f"Config Error: This script can only support a single config file right now...")
    sys.exit(1)

# setup the logger
# TODO the qbm one is a lot that i'm not prepared to handle in a separate script
logger = logging.getLogger("qBit Manage Recycle Bin Recovery")
numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % log_level)
logging.basicConfig(filename='recyclebin_recovery.log', encoding='utf-8', level=numeric_level)

def move_files(src, dest, mod=False):
    """Move files from source to destination, mod variable is to change the date modified of the file being moved"""
    dest_path = os.path.dirname(dest)
    to_delete = False
    if os.path.isdir(dest_path) is False:
        os.makedirs(dest_path, exist_ok=True)
    try:
        if mod is True:
            mod_time = time.time()
            os.utime(src, (mod_time, mod_time))
        shutil.move(src, dest)
    except PermissionError as perm:
        logger.warning(f"{perm} : Copying files instead.")
        try:
            shutil.copyfile(src, dest)
        except Exception as ex:
            # logger.stacktrace() # TODO i'm not prepared to handle in a separate script
            logger.error(ex)
            return to_delete
        if os.path.isfile(src):
            logger.warning(f"Removing original file: {src}")
            try:
                os.remove(src)
            except OSError as e:
                logger.warning(f"Error: {e.filename} - {e.strerror}.")
        to_delete = True
    except FileNotFoundError as file:
        logger.warning(f"{file} : source: {src} -> destination: {dest}")
    except Exception as ex:
        # logger.stacktrace() # TODO i'm not prepared to handle in a separate script
        logger.error(ex)
    return to_delete

# TODO the qbm one is a lot that i'm not prepared to handle in a separate script
def load_config(config_path):
    """Load configuration from qbit manage's YAML config"""
    with open(config_path) as file:
        yaml=YAML()
        return yaml.load(file)

def tor_recover_recycle(recycle_path):
    """Recover torrents and files from recycle bin"""
    torrents_json_path = os.path.join(recycle_path, "torrents_json")
    for torrents_json_file in os.listdir(torrents_json_path):
        with open(os.path.join(torrents_json_path, torrents_json_file)) as tf:
            torrent_json = json.load(tf)
            print("placeholder")

if __name__ == "__main__":
    # Load configuration from YAML
    try:
        config = load_config(os.path.join(default_dir, config_files))
    except FileNotFoundError as ex:
        logger.error(ex)
        sys.exit(1)
    try:
        # Retrieve directories from the config
        recyclebin_dir = config.get("directory", {}).get("recycle_bin")
        torrents_dir = config.get("directory", {}).get("torrents_dir")
        remote_dir = config.get("directory", {}).get("remote_dir")
        recyclebin = config.get("recyclebin", {})
        categories = config.get('cat')
    except Exception as ex:
        logger.error(ex)
        sys.exit(1)
    try:
        if recyclebin.get("enabled"):
            if recyclebin.get("split_by_category"):
                for cat, cat_path in categories.items():
                    recycle_path = os.path.join(cat_path, os.path.basename(recyclebin_dir.rstrip(os.sep)))
                    print("placeholder")
            else:
                recycle_path = recyclebin_dir
                print("placeholder")
        else:
            logger.warning("The Recyclebin isn't enabled so there is nothing to restore...")
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as ex:
        logger.error(ex)
        sys.exit(1)

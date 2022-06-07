"""Downloads a 5 minute recording from an NVR.

The web interface limits the clip length to 5 minutes. This seems to work with up to about 15
minutes. Above that, it generally times out.
"""
import os
from configparser import RawConfigParser
from datetime import datetime as dt
from datetime import timedelta
from tempfile import TemporaryDirectory

from reolinkapi import Camera

MINUTES = 5


def read_config(props_path: str) -> dict:
    """Reads in a properties file into variables.

    NB! this config file is kept out of commits with .gitignore. The structure of this file is such:
    # secrets.cfg
        [camera]
        ip={ip_address}
        username={username}
        password={password}
        channel={channel}
    """
    config = RawConfigParser()
    assert os.path.exists(props_path), f"Path does not exist: {props_path}"
    config.read(props_path)
    return config


# Read in your ip, username, & password
#   (NB! you'll likely have to create this file. See tests/test_camera.py for details on structure)
config = read_config("../secrets.cfg")

ip = config.get("camera", "ip")
un = config.get("camera", "username")
pw = config.get("camera", "password")
channel = int(config.get("camera", "channel")) or 0

# Get time range
now = dt.now()
end = now.replace(minute=now.minute // MINUTES *
                  MINUTES, second=0, microsecond=0)
start = end - timedelta(minutes=MINUTES)

# Connect to camera
with Camera(ip=ip, username=un, password=pw) as cam:
    # Get clips from the provided time range.
    print(f"Getting clips for time range: {start}-{end}")
    processed_files = cam.get_nvr_files(start=start, end=end, channel=channel)

    print(f"Processed Files: {processed_files}")

    with TemporaryDirectory() as td:
        for filename in processed_files:
            # Download the mp4
            print(f"Downloading: {filename}")
            video_file = os.path.join(td, filename)

            # resp = cam.get_file(filename=filename, output_path=str(video_file))
            # print(resp)

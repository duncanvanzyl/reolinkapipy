from datetime import datetime as dt
from typing import Any


def is_error(resp: dict[str, Any]) -> bool:
    return resp["code"] == 1 and resp.get("error") is not None


def cmd_error(resp: dict[str, Any]) -> str:
    if err := resp.get("error"):
        return f"Command Error: rspCode: {err['rspCode']}, {err['detail']}"
    return ""


class NVRDownloadAPIMixin:
    """API calls for NVR video files."""

    def get_nvr_files(self, start: dt, end: dt = dt.now(), channel: int = 0) -> list[str]:
        """Get the filenames of a clip of stored video on an NVR.

        Args:
            start: the starting time range to create a clip of
            end: the end time of the time range to create a clip of
            channel: the channel of the nvr
                this is one less than the value from the app.
                ie, if the app names the channel "CH04", then the channel is 3
        :return: a list of file names

        Raises ValueError on an error.
        """

        cmd = "NvrDownload"

        params = {
            cmd: {
                "EndTime": {
                    "year": end.year,
                    "mon": end.month,
                    "day": end.day,
                    "hour": end.hour,
                    "min": end.minute,
                    "sec": end.second,
                },
                "StartTime": {
                    "year": start.year,
                    "mon": start.month,
                    "day": start.day,
                    "hour": start.hour,
                    "min": start.minute,
                    "sec": start.second,
                },
                "channel": channel,
            }
        }

        body = [{"cmd": cmd, "action": 1, "param": params}]

        resp = self._execute_command(cmd, body)[0]
        if is_error(resp):
            raise ValueError(cmd_error(resp))

        files = resp["value"].get("fileList")
        print(f"Files: {files}")
        if files:
            # Begin processing files
            processed_files = self._process_files(files)
            return processed_files
        return []

    @staticmethod
    def _process_files(files) -> list[str]:
        """Processes raw list of dicts containing motion timestamps
        and the filename associated with them"""
        # Process files
        processed_files: list[str] = []
        for file in files:
            filename = file.get("fileName")
            if filename:
                processed_files.append(filename)
        return processed_files

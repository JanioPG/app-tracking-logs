import io
import re
import subprocess
import json
from urllib.parse import unquote
from tools import utils, ui_data
from interface import show_log, show_program_finished


def convert_to_JSON(log: str) -> str:
    try:
        data = unquote(log)
        data = re.sub(r'\"\{', '{', data)
        data = re.sub(r'\}\"', '}', data)
        data = re.sub(r'\\\"', '"', data)
        data = json.loads(data)
        return json.dumps(data, indent=4)

    except Exception as error:
        print(f"error data json: {error}")
        return log


def appsflyer():
    colors = ui_data.Colors()
    command = utils.COMMAND.FILTER_APPSFLYER.value

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    RE_CUID = re.compile(r'CustomerUserID:', re.IGNORECASE)
    RE_SEND = re.compile(r'SEND\ Event', re.IGNORECASE)
    RE_KEYS = re.compile(r'(eventName|eventvalue|appUID)', re.IGNORECASE)

    with subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding="utf-8"
    ) as proc:
        try:
            for line in proc.stdout:
                if RE_CUID.search(line, re.IGNORECASE):
                    styled_line = f"{colors.GREEN}{line}{colors.CLOSE}"
                
                elif RE_KEYS.search(line, re.IGNORECASE):
                    line = convert_to_JSON(line)
                    styled_line = RE_KEYS.sub(f"{colors.BLUE}\\1{colors.CLOSE}", line)

                elif RE_SEND.search(line, re.IGNORECASE):
                    styled_line = f"{colors.BLUE}{line}{colors.CLOSE}"

                else:
                    styled_line = f"{colors.LIGHT_GRAY}{line}{colors.CLOSE}"
                
                show_log(styled_line)

        except KeyboardInterrupt:
            proc.terminate()
            show_program_finished()


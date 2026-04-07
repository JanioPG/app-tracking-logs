import re
import subprocess
import json
from tools import ui_data
from interface import show_error_message, show_log, show_program_finished
import asyncio.subprocess as async_subprocess


# constants
cmd_clear: List[str] = ["adb", "logcat", "-c"]
cmd_stream: List[str] = ["adb", "logcat", "-v", "time"]
CUSTOMER_USER_ID = re.compile(r'AppsFlyer.*setCustomerUserId', re.IGNORECASE)
APPSFLYER_DATA = re.compile(r'AppsFlyer.*\ preparing\ data:.*', re.IGNORECASE)
APPSFLYER_LOG = re.compile(r'\/AppsFlyer_')
url_request = re.compile(r'POST:.*.appsflyersdk.com', re.IGNORECASE)
response_code = re.compile(r'response\ code')


def edit_log(log: str):
    """Edits the log to better organize key values.

    Args:
        log (str): log/record to be edited.

    Returns:
        log (str): edited log/record.
    """
    colors = ui_data.Colors()
    keys_delete = ["isFirstCall", "registeredUninstall", "cell", "operator", "network",
                "af_v2", "sig", "isGaiWithGps", "installDate", "dim", "firstLaunchDate", "device",
                "model", "brand", "last_boot_time", "deviceData", "date2", "date1", "counter",
                "af_v", "carrier", "disk", "iaecounter", "sc_o", "isGaidWithGps", "prev_event"]

    try:
        if APPSFLYER_DATA.search(log, re.IGNORECASE):
            tag, data = log.split(": preparing data: ", 1)
            data_json = json.loads(data)
            event_value = data_json.get('eventValue')

            if isinstance(event_value, str) and event_value.strip():
                try:
                    data_json['eventValue'] = json.loads(event_value)
                except json.JSONDecodeError:
                    pass
            
            for key in keys_delete:
                data_json.pop(key, None)
            
            formatted_json = json.dumps(data_json, indent=4)
            
            log = f"{tag} \n{formatted_json}\n"

            if "eventName" in log or "eventValue" in log:
                log = re.sub(r'("eventName")', f"{colors.LIGHT_CYAN}\\1{colors.CLOSE}", log)
                log = re.sub(r'("event[vV]alue")', f"{colors.LIGHT_CYAN}\\1{colors.CLOSE}", log)
        else:
            return log

    except Exception as error:
        # show_error_message(str(error))
        pass

    finally:
        return log


async def appsflyer_logs():
    proc = None
    colors = ui_data.Colors()

    try:
        try:
            clear_proc = await async_subprocess.create_subprocess_exec(
                *cmd_clear,
                stdout=async_subprocess.PIPE,
                stderr=async_subprocess.PIPE
            )
            await clear_proc.wait()
            print(f"Logcat buffer cleared.\n")

        except Exception as e:
            print(f"Could not clear logcat buffer: {e}")

        proc = await async_subprocess.create_subprocess_exec(
            *cmd_stream,
            stdout=async_subprocess.PIPE,
            stderr=async_subprocess.PIPE
        )
   
        async for line_bytes in proc.stdout:
            line = line_bytes.decode('utf-8', errors='ignore')
            is_appsflyer = APPSFLYER_LOG.search(line, re.IGNORECASE) != None

            if is_appsflyer:
                if url_request.search(line, re.IGNORECASE):
                    show_log(f"{colors.LIGHT_GRAY}{line} {colors.CLOSE}")

                elif APPSFLYER_DATA.search(line, re.IGNORECASE):
                    show_log(f"{edit_log(line)}")

                elif response_code.search(line, re.IGNORECASE):
                    show_log(f"{colors.LIGHT_GRAY}{line} {colors.CLOSE}")
                    
                elif CUSTOMER_USER_ID.search(line, re.IGNORECASE):
                    show_log(f"{colors.LIGHT_CYAN}{line} {colors.CLOSE}")


    except FileNotFoundError:
        print("'adb' command not found. Please ensure it is installed and in your system's PATH.")
    except KeyboardInterrupt:
        show_program_finished()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        if proc:
            proc.terminate()
            try:
                await proc.wait()
            except Exception:
                proc.kill()
            show_program_finished()


if __name__ == "__main__":
    appsflyer_logs()
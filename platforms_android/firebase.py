import io
import re
import subprocess
import sys
import argparse
import json
from tools import ui_data, utils
from interface import show_log, show_error_message

colors = ui_data.Colors()


def enable_verbose_logging(FA_verbose: bool = False) -> subprocess.Popen:
    """Enable verbose logging mode.

    Args:
        FA_verbose (bool, optional): Enables FA Verbose. Defaults to False.

    Returns:
        proc (subprocess.Popen): Instance of the Popen class. 
    """
    try:
        if FA_verbose:
            subprocess.run(utils.COMMAND.FA_VERBOSE.value.split(" "))

        subprocess.run(utils.COMMAND.FA_SVC_VERBOSE.value.split(" "))
        proc = subprocess.Popen(utils.COMMAND.FILTER_FA_FA_SVC.value.split(" "), stdout=subprocess.PIPE)
    except Exception as error:
        show_error_message(ui_data.Error.ENABLE_VERBOSE_ANDROID.value, possible_cause=str(error))
        sys.exit(1)
    else:
        return proc


def parse_bundle_to_params(content: str) -> str:
    data = {}
    
    # handle nested lists of bundles for items=[Bundle[{...}, Bundle[{...}]]
    list_pattern = re.compile(r"([a-zA-Z0-9_]+)=\[Bundle\[\{(.*?)\}\](?:,\s*Bundle\[\{(.*?)\}\])*\]")
    
    # handle key=value pairs
    item_pattern = re.compile(r"([a-zA-Z0-9_()]+)=(.+?)(?=\,\s*[a-zA-Z0-9_()]+=|\s*$)")

    # extract items
    for match in list_pattern.finditer(content):
        key = match.group(1)
        inner_bundles = re.findall(r"\{(.*?)\}", match.group(0))

        data[key] = [parse_bundle_to_params(b) for b in inner_bundles]
        # Remove the processed list from the content string
        content = content.replace(match.group(0), "")

    # extract root key=value pairs
    for match in item_pattern.finditer(content):
        key = match.group(1)
        value = match.group(2).strip()
        data[key] = value

    return data
    

def edit_log(log: str) -> str:
    """Edits the log to better organize key values.

    Args:
        log (str): log/record to be edited.

    Returns:
        log (str): edited log/record.
    """
    try:
        metadata, bundle = log.split(",params=Bundle[{", 1)
        bundle_content = bundle.rsplit("}]", 1)[0]
        metadata = re.sub(r"V.*Logging event: ", ",", metadata)
        time, origin, event_name = [s.strip() for s in metadata.split(",")]

        params = parse_bundle_to_params(bundle_content)

        return f"{time} {origin.replace('=', ': ')} | {event_name.replace('=', ': ')} \n{json.dumps(params, indent=2).replace('\"', '')}\n"

    except Exception as error:
        return log


def no_arguments() -> None:
    """Displays logs of events being logged. 
    """
    proc = enable_verbose_logging()

    re_registered_event = re.compile(r"Logging\ event:")
    screenview_event = re.compile(r'name\s*=\s*(?:edo_)?screen_view', re.IGNORECASE)
    automatic_event = re.compile(r'origin\s*=\s*auto')

    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):

        if re_registered_event.search(line, re.IGNORECASE):
            is_screen_view = screenview_event.search(line)
            is_automatic_event = automatic_event.search(line)

            line = edit_log(line)

            if is_screen_view and not is_automatic_event:
                show_log(f"{colors.LIGHT_CYAN}{line}{colors.CLOSE}")

            elif is_automatic_event:
                show_log(f"{colors.LIGHT_GRAY}{line}{colors.CLOSE}")
            else:
                show_log(f"{line}")


def with_arguments(args: argparse.Namespace) -> None:
    """Filters the logs/records based on arguments given by the user.

    Args:
        args (argparse.Namespace): Arguments passed by the user in the call to execute the script.
    """
    if args.pattern1 == None and args.pattern2 == None: # Only -v exists in the call
        no_arguments()

    elif args.pattern1 != None and args.pattern2 != None:
        proc = enable_verbose_logging(FA_verbose=True)
        re_terms = re.compile(rf"{args.pattern1}|{args.pattern2}")

        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            check_terms = list(set(re_terms.findall(line, re.IGNORECASE)))
            
            if len(check_terms) == 2:
                check_terms.sort() # sort - alphabetically
                line = edit_log(line)

                line = re.sub(f"{check_terms[0]}", f"{colors.BLUE}{check_terms[0]}{colors.CLOSE}", line)
                line = re.sub(f"{check_terms[1]}", f"{colors.GREEN}{check_terms[1]}{colors.CLOSE}", line)
                show_log(line)

    elif args.pattern1 != None or args.pattern2 != None:
        proc = enable_verbose_logging(FA_verbose=True)
        term = args.pattern1 if args.pattern1 != None else args.pattern2
        re_terms = re.compile(rf"{term}")
        
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            term_match = re_terms.search(line, re.IGNORECASE)         
            if term_match:
                line = edit_log(line)
                line = re.sub(term_match.group(), f"{colors.BLUE}{term_match.group()}{colors.CLOSE}", line)
                show_log(line)


def view_user_property():
    proc = enable_verbose_logging()

    re_set_user_property = re.compile(r"Setting\ user\ property:")
    re_user_property_removed = re.compile(r"User\ property\ removed:")

    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if re_set_user_property.search(line, re.IGNORECASE):
            line = re.sub(r"V\/FA.*user\ property:", "Setting user property:\n", line)
            show_log(f"{colors.YELLOW}{line}{colors.CLOSE}")

        elif re_user_property_removed.search(line, re.IGNORECASE):
            line = re.sub(r"D\/FA.*property\ removed", "User property removed", line)
            show_log(f"{colors.LIGHT_GRAY}{line}{colors.CLOSE}")


if __name__ == "__main__":
    no_arguments()

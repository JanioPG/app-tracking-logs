import sys
from platforms_android import firebase, univesal_analytics, appsflyer, gtm
from interface import show_error_message, show_program_finished, show_custom_message
from tools import ui_data, utils
from asyncio import run

async def get_logs():
    operating_system = ui_data.OperatingSystem()
    platforms = ui_data.Platform()
    enabled_platforms = [
        platforms.GA4_EVENTS,
        platforms.GA4_USER_PROPERTY,
        platforms.APPSFLYER,
        platforms.GTM
    ]

    instructions = ui_data.Instructions(operating_system.ANDROID, enabled_platforms)

    try:
        args, platform = utils.get_arguments_and_option(instructions)

        no_argument: bool = True if (len(sys.argv) == 1) else False
        
        match (platform):
            case platforms.GA4_EVENTS:
                firebase.no_arguments() if (no_argument) else firebase.with_arguments(args)

            case platforms.GA4_USER_PROPERTY:
                firebase.view_user_property()

            case platforms.GAU:
                univesal_analytics.no_arguments() if (no_argument) else univesal_analytics.with_arguments(args)

            case platforms.APPSFLYER:
                await appsflyer.appsflyer_logs()

            case platforms.ADJUST | platforms.SINGULAR:
                show_custom_message(f"{ui_data.Icon.LOCK.value} {ui_data.Error.NO_SUPORT.value}")
                sys.exit(0)

            case platforms.GTM:
                gtm.main()

            case ui_data.Option.QUIT.value:
                show_program_finished()
                sys.exit(0)

            case _:
                show_error_message(ui_data.Error.CHOICE_OPTION.value)

    except KeyboardInterrupt:
        show_program_finished()
    
    except TypeError as te:
        show_error_message(str(te))

    except Exception as error:
        show_error_message(str(error))
        sys.exit(1)


if __name__ == "__main__":
    try:
        run(get_logs())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(1)

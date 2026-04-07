# App Tracking Logs

### Feature: Present app tracking logs in a more intuitive way. When running, view one of the options, such as Google Analytics 4, AppsFlyer, and Google Tag Manager.

## **Dependencies**:

* [Python 3.10+](https://www.python.org/)
* [Android Debug Bridge (adb)](https://developer.android.com/studio/command-line/adb)

## **How to use:**

Clone the repository. In the terminal, change the directory to the project root.
Run one of the scripts below according to your application's operating system:

Android:
`python android_debug_logs.py` or `python3 android_debug_logs.py`

iOS:
`python ios_debug_logs.py` or `python3 ios_debug_logs.py`

Note: Ensure that your Android emulator, iOS simulator, or Android device is active and connected to your computer.

After executing the command, select one of the options from the menu.

---
## **Alternative installation [Optional]**:

Download the _install.sh_ file.

Grant execution permission to the file (shell script) with the command: `chmod +x install.sh`

Then run it with the command: `./install.sh`

Once finished, you can simply run the script from any directory with the commands:

Android: `track_android`

iOS: `track_ios`

#### Secondary function: Filter

Run on your terminal: `python android_debug_logs.py -p1 <filter_1> -p2 <filter_2>` or `python ios_debug_logs.py -p1 <filter_1> -p2 <filter_2>`

Example:

For GA4, obtain only the add_to_cart event log and highlight the _value_ parameter:

`python android_debug_logs.py -p1 ‘add_to_cart’ -p2 ‘value’`

View only the purchase event log (Android and iOS):

`python android_debug_logs.py -p1 ‘name=purchase|purchase’`

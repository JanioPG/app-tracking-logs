#!/bin/zsh

# environment variables
DEBUG_LOGS=${HOME}/.appTrackingLogs/tracking_logs
ADB_URL_LINUX=https://dl.google.com/android/repository/platform-tools-latest-linux.zip
ADB_URL_MAC=https://dl.google.com/android/repository/platform-tools-latest-darwin.zip
OS_INFO=$(uname)
GITHUB_REPO="git@github.com:JanioPG/app-tracking-logs.git"

# COLORS
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
CLOSE="\033[0m"

# default strings
ARROW="\n${CYAN}==>${CLOSE}"
CONFIG_EMOJI="⚙️"
FINISH_EMOJI="🚀"
ERROR_EMOJI="🚨"
CHECK_EMOJI="✅"
ALERT_EMOJI="⚠️"

function get_OS_info {
    if [[ $OS_INFO == "Linux" ]]; then
        print "${CYAN}You are a Linux user. Awesome!${CLOSE}"
    elif [[ $OS_INFO == "Darwin" ]]; then
        print "${CYAN}You are a Mac user. Nice style!${CLOSE}"
    elif [[ $OS_INFO == "WindowsNT" ]]; then
        print "${CYAN}You are a Windows user. You are screwed!${CLOSE}"
    else
        print "${YELLOW} Operating system not recognised: $OS_INFO${CLOSE}"
    fi
}


function create_appTrackingLogs_folder {
    print "${CONFIG_EMOJI} ${GREEN} Getting started...${CLOSE}"
    if [[ -d $DEBUG_LOGS ]]; then
        print " The .appTrackingLogs directory exists!"
    else
        print " The .appTrackingLogs directory does not exist. Creating directories:"
        mkdir -v -p $DEBUG_LOGS
    fi
}


function download_repository {
    print "\n${CONFIG_EMOJI} ${GREEN} Downloading repository.${CLOSE}"

    if ! command -v git &>/dev/null; then
        print "${ALERT_EMOJI} ${YELLOW} Git is not installed.${CLOSE}"
        print " Install with apt for Linux (debian/ubuntu): 'sudo apt install git'."
        print " Or with homebrew for Mac: 'brew install git'."
        print " NOTE: After installing, add your name with:"
        print "${YELLOW}\tgit config --global user.name 'your name'.${CLOSE}"
        print "      Add your email address with:"
        print "${YELLOW}\tgit config --global user.email 'example@domain.com'.${CLOSE}"
        print " After installing and configuring git, run ./install.sh again."
        return 1
    fi

    if git clone $GITHUB_REPO $DEBUG_LOGS; then
        print "${CYAN}\tDone: repository downloaded!${CLOSE} ${CHECK_EMOJI}"
        add_alias
    else
        print "\n${CONFIG_EMOJI} ${GREEN}The repository probably already exists. Attempting to update the repository...${CLOSE}"
        if (cd $DEBUG_LOGS && git pull origin main); then
            print "${CYAN}\tDone: Repository updated!${CLOSE} ${CHECK_EMOJI}"
            add_alias
        else
            print "${ERROR_EMOJI} ${RED} Error downloading the repository. Check the error and, after correcting it if necessary, run the install.sh script again.${CLOSE}"
        fi
    fi
}


function add_alias {
    print "\n${CONFIG_EMOJI} ${GREEN} Adding aliases for the scripts.${CLOSE}"

    local android_script_path=($DEBUG_LOGS/**/android*logs.py(.N[1]))
    local ios_script_path=($DEBUG_LOGS/**/ios*logs.py(.N[1]))

    local shell_configs=("$HOME/.zshrc" "$HOME/.bashrc")

    if [[ -z "$android_script_path" ]]; then
        print "${ERROR_EMOJI} ${RED}Script 'android*logs.py' not found in $DEBUG_LOGS. Skipping alias 'track_android'.${CLOSE}"
    else
        local android_alias="alias track_android=\"python3 ${android_script_path}\""
        for config_file in $shell_configs; do
            if [[ -f "$config_file" ]]; then
                if grep -q "alias track_android" "$config_file"; then
                    print "alias track_android already exists in $config_file."
                else
                    print "\n${android_alias}" >> "$config_file"
                    print "${CYAN}\tAlias 'track_android' added to $config_file.${CLOSE} ${CHECK_EMOJI}"
                fi
            fi
        done
    fi

    if [[ -z "$ios_script_path" ]]; then
        print "${ERROR_EMOJI} ${RED}Script 'ios*logs.py' not found in $DEBUG_LOGS. Skipping alias 'track_ios'.${CLOSE}"
    else
        local ios_alias="alias track_ios=\"python3 ${ios_script_path}\""
        for config_file in $shell_configs; do
            if [[ -f "$config_file" ]]; then
                if grep -q "alias track_ios" "$config_file"; then
                    print "alias track_ios already exists in $config_file."
                else
                    print "\n${ios_alias}" >> "$config_file"
                    print "${CYAN}\tAlias 'track_ios' added to $config_file.${CLOSE} ${CHECK_EMOJI}"
                fi
            fi
        done
    fi

    install_adb
}


function add_adb_to_path {
    print "\n${CONFIG_EMOJI} ${GREEN} Adding 'adb' to the path variable:${CLOSE}"

    local adb_path_export="\n# Adding adb to the path variable \nexport PATH=\$PATH:\$HOME/.appTrackingLogs/platform-tools"

    local shell_configs=("$HOME/.zshrc" "$HOME/.bashrc")

    for config_file in $shell_configs; do
        if [[ -f "$config_file" ]]; then
            if grep -q 'export\ PATH.*platform-tools' "$config_file"; then
                print "$adb_path_export" >> "$config_file"
                print "${CYAN}\tCompleted for $config_file.${CLOSE} ${CHECK_EMOJI}"
            else
                print "${CYAN}\t'adb' is already added to the PATH variable in $config_file.${CLOSE}"
            fi
        fi
    done
}


function download_adb {

    get_OS_info

    local adb_url
    if [[ $OS_INFO == "Darwin" ]]; then
        adb_url=$ADB_URL_MAC
    elif [[ $OS_INFO == "Linux" ]]; then
        adb_url=$ADB_URL_LINUX
    else
        print "${ERROR_EMOJI} You are not a Linux or Mac user. But download adb for your operating system at 'https://developer.android.com/studio/releases/platform-tools'."
        exit 1
    fi

    if curl "$adb_url" -# -L --create-dirs -o "${HOME}/.appTrackingLogs/platform-tools.zip" -C -; then
        print "\n${CONFIG_EMOJI} 'adb' successfully downloaded. ${CHECK_EMOJI} \nUnzipping..."
        (cd "${HOME}/.appTrackingLogs" && unzip -o platform-tools.zip)
        rm "${HOME}/.appTrackingLogs/platform-tools.zip"

        add_adb_to_path
    else
        print "${ALERT_EMOJI} Error downloading adb. Please review the error and attempt to run the install.sh script again."
        print "If you receive error “92”, it may be because you already have the adb file downloaded in the .appTrackingLogs folder."
    fi
}


function install_adb {
    print "\n${CONFIG_EMOJI} ${GREEN} Checking if 'adb' is installed (applicable for Android).${CLOSE}"
    if command -v adb &>/dev/null; then
        print "${ALERT_EMOJI} ${YELLOW} 'adb' was not found in the current PATH.${CLOSE}"
        print "Note: If you have installed Android Studio, you may need to add adb to your PATH variable."

        local adb_found_path=""

        if [[ $OS_INFO == "Darwin" ]]; then
            local adb_paths=($HOME/Library/Android/sdk/platform-tools/adb(.N[1]))
            if [[ -f "$adb_paths" ]]; then
                adb_found_path=$adb_paths
            fi
        elif [[ $OS_INFO == "Linux" ]]; then
            local adb_paths=($HOME/Android/**/platform-tools/adb(.N[1]))
            if [[ -f "$adb_paths" ]]; then
                adb_found_path=$adb_paths
            fi
        fi

        if [[ -n "$adb_found_path" ]]; then
            print "${YELLOW}\nDespite this, I found adb in '$adb_found_path'.${CLOSE}"
            print "In your .zshrc (or .bashrc) file in your home directory, add the line:"
            print "\texport PATH=\$PATH:$(dirname $adb_found_path)\n"
        fi

        while true; do
            read -k 1 "userResponse?Would you like to download and install adb now? [Y/n]: "
            print

            case $userResponse in
                [Yy])
                    print "${CYAN}You chose to install it.${CLOSE}"
                    download_adb
                    break
                    ;;
                [Nn])
                    print "${CYAN}You have chosen not to install adb.${CLOSE}"
                    break
                    ;;
                *)
                    print "${ERROR_EMOJI} ${RED}Invalid option. Enter only y (yes) or n (no).${CLOSE}"
                    ;;
            esac
        done
    else
        print "${CHECK_EMOJI} 'adb' is now available in your PATH.${CLOSE}"
    fi

    completion_message
}

function completion_message {
    print "\n${FINISH_EMOJI} ${GREEN}Done!${CLOSE}"
    print "Restart the terminal (by closing and reopening it) so that the shell settings are reloaded."
    print "Once the settings have been reloaded, run ${CYAN}'track_android'${CLOSE} on your terminal to view Android events or ${CYAN}'track_ios'${CLOSE} to view iOS events. If you have any questions, please contact janiopg.p@gmail.com"
}

# start
create_appTrackingLogs_folder
download_repository

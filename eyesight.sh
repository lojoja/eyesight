#!/usr/bin/env bash
#
# eyesight
# eyesight/eyesight.sh
#
# Enable/disable the built in camera on OS X.
#

#
# CONSTANTS
#
EYESIGHT_NAME='eyesight'
EYESIGHT_VERSION='1.0.1'
EYESIGHT_FILES=(
  "/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC"
  "/System/Library/PrivateFrameworks/CoreMediaIOServices.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC"
  "/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/AVC.plugin/Contents/MacOS/AVC"
  "/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC"
  "/System/Library/QuickTime/QuickTimeUSBVDCDigitizer.component/Contents/MacOS/QuickTimeUSBVDCDigitizer"
  "/Library/CoreMediaIO/Plug-Ins/DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera"
  "/Library/CoreMediaIO/Plug-Ins/FCP-DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera"
)
IS_TERM=$([[ -t 0 || -p /dev/stdin ]]; echo $?) # interactive/non-interactive

#
# FUNCTIONS
#
log() {
  printf "%s $EYESIGHT_NAME: %s\n" "$(date '+%b %d %I:%M:%S')" "$1"
}

errorMessage() {
  [[ $IS_TERM -eq true ]] && printf "\033[1;31mError:\033[0m %s\n" "$1" || log "Error: $1"
}

infoMessage() {
  [[ $IS_TERM -eq true ]] && printf "\033[1;34m==>\033[0m %s\n" "$1" || log "==> $1"
}

successMessage() {
  [[ $IS_TERM -eq true ]] && printf "\033[1;32mOK:\033[0m %s\n" "$1" || log "OK: $1"
}

die() {
  errorMessage "$1"
  exit 1
}

eyesightHelp() {
  cat <<- EOF
Usage: $EYESIGHT_NAME [--help|--version]
       $EYESIGHT_NAME enable
       $EYESIGHT_NAME disable
'$EYESIGHT_NAME' enables/disables the iSight camera on OS X.

Examples:
  $EYESIGHT_NAME enable   # Enable the iSight camera
  $EYESIGHT_NAME disable  # Disable the iSight camera

Options:
  -h, --help                 display this help and exit
  -v, --version              display the $EYESIGHT_NAME version and exit
EOF
}

#
# RUN
#
if [[ $# = 0 || $1 = "-h" || $1 = "--help" ]]
then
  eyesightHelp && exit 0
fi

if [[ $1 = "-v" || $1 = "--version" ]]
then
  printf "$EYESIGHT_NAME $EYESIGHT_VERSION" && exit 0
fi

EYESIGHT_COMMAND="$1"

case $EYESIGHT_COMMAND in
  enable)
    infoMessage "Enabling iSight camera"
    permissions=755
    ;;
  disable)
    infoMessage "Disabling iSight camera"
    permissions=000
    ;;
  *)
    die "Unknown command: $EYESIGHT_COMMAND"
    ;;
esac

# Check System Integrity Protection status on OS X 10.10.x+
osx=$(sw_vers -productVersion | awk -F '.' '{print $1$2}')

if [[ $osx -ge 1010 ]]
then
  sip=$(csrutil status | grep -Eo '(dis|en)abled')

  if [[ $sip == "enabled" ]]
  then
    die "System Integrity Protection is enabled."
  fi
fi

# Set file permissions for selected action
perm_ok=0

for file in "${EYESIGHT_FILES[@]}"; do
  if [[ -f $file ]]
  then
    if ! chmod $permissions "$file"
    then
      errorMessage "Failed to set permissions on $file"
      perm_ok=1
    fi
  fi
done

if [[ ! $perm_ok ]]
then
  die "Failed to $EYESIGHT_COMMAND iSight"
else
  successMessage "iSight ${EYESIGHT_COMMAND}d" && exit 0
fi

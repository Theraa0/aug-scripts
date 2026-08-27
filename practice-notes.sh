#!/usr/bin/env bash

notes=("A " "B " "C " "D " "E " "F " "G " "A#" "C#" "D#" "F#" "G#" "Ab" "Bb" "Db" "Eb" "Gb")
notes_unpad=("G#Ab" "A" "A#Bb" "B" "C" "C#Db" "D" "D#Eb" "E" "F" "F#Gb" "G")

rand_note() {
	local rand_idx=$((RANDOM % ${#notes[@]}))
		echo "${notes[$rand_idx]}"
}

wait_for_input() {
	echo
	read -n 1 -s -p "  $(accent_text 'Press key to continue...')" key
	if [[ "$key" == "q" ]]; then
		exit 0
	fi
}

# Funktion zum Finden des Index eines Elements
get_index() {
	# Alle Leerzeichen aus dem Such-String entfernen (wichtig für "A ")
	local match="${1// /}" 
	for i in "${!notes_unpad[@]}"; do
		local current="${notes_unpad[i]}"
		# Erste zwei Zeichen prüfen (z.B. G# aus G#Ab)
		if [[ "${current:0:2}" == "$match" ]]; then
			echo "$i"
			return 0
		# Letzte zwei Zeichen prüfen (z.B. Ab aus G#Ab)
		elif [[ "${current: -2}" == "$match" ]]; then
			echo "$i"
			return 0
		fi
	done
	return 1
}

distance() {
	local idx1=$(get_index "$1")
	local idx2=$(get_index "$2")
	local len=${#notes_unpad[@]}
	echo $(( (idx2 - idx1 + len) % len ))
}


countdown() {
	local seconds=$1
	local key
	while (( seconds > 0 )); do
		printf "\r\33[2K  %02d:%02d" $(( seconds / 60 )) $(( seconds % 60 ))

		if read -n 1 -s -t 1 key; then
			if [ "$key" = "q" ]; then
				exit
			else
				echo -e "\r  skipped"
				return
			fi
		fi

		(( seconds-- ))
	done
	printf "\r\33[2K  finished"
	alarm
}
alarm() {
	tput bel
	sleep 1
	tput bel
	sleep 1
	tput bel
}

# FORMATTING
gray="\033[38;2;120;120;120m"
reset="\033[0m"
accent_text() {
	echo -e "${gray}$*${reset}"
}

# CLEANUP ON EXIT
cleanup() {
	tput cnorm
	tput rmcup
}
trap cleanup EXIT

# PARSE FLAGS
PARSED=$(getopt -o l: --long loop: -n "$0" -- "$@")
if [ $? -ne 0 ]; then
    exit 1
fi
eval set -- "$PARSED"
LOOP_MODE=false
TIMER=15
while true; do
	case "$1" in
		-l|--loop)
			LOOP_MODE=true
			TIMER=$2
			shift 2
			;;
		--)
			shift
			break
			;;
		*)
			echo "Error parsing flags" >&2
			exit 1
			;;
	esac
done

# INIT
base_note="$1"
if [[ -z "$base_note" ]]; then
	echo "no base note"
	exit
fi
tput civis
tput smcup

while true; do
	clear
	echo
	note=$(rand_note)
	echo "  $note on $base_note"
	if [ "$LOOP_MODE" = true ]; then
		countdown $TIMER
	else
		wait_for_input
	fi

	calc_distance=$(distance "$base_note" "$note")

	printf "\r\033[2K  Abstand: %s\n" "$calc_distance"
	if [ "$LOOP_MODE" = true ]; then
		countdown 4
	else
		wait_for_input
	fi
done

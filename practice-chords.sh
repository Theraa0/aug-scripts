#!/usr/bin/env bash
# CHOSE RANDOM CHORD
rand_chord () {
	rand_note=$((RANDOM%${#notes[@]}))
	chosen_note=${notes[$rand_note]}

	rand_type=$((RANDOM%${#chord_types[@]}))
	chosen_type=${chord_types[$rand_type]}

	rand_form=$((RANDOM%${#chord_forms[@]}))
	chosen_form=${chord_forms[$rand_form]}

	if [ "$SIMPLE_MODE" = true ]; then
		# echo -e "$chosen_type $(accent_text in the) $chosen_form $(accent_text form)"
		string="$chosen_form,$chosen_type,$chosen_form"
	else
		string="$chosen_note,$chosen_type,$chosen_form"
	fi
	echo $string
}

pretty_print_chord() {
	IFS=',' read -ra ADDR <<< $1
	if [ "$SIMPLE_MODE" = true ]; then
		echo -e "  ${ADDR[0]} ${ADDR[1]}"
	else
		echo -e "  ${ADDR[0]} ${ADDR[1]} $(accent_text in the) ${ADDR[2]} $(accent_text form)"
	fi
}

print_chord_wrapper() {
	echo
	IFS=',' read -ra ADDR <<< $1
	key=${ADDR[0]}
	dings=${ADDR[1]}
	form=${ADDR[2]}
	if [ "$dings" == "Power" ]; then
		dings="power"
	elif [ "$dings" == "Major" ]; then
		dings="major"
	elif [ "$dings" == "Minor" ]; then
		dings="minor"
	fi
	pretty_print_chord $1
	print-chords $key $dings $form --finger | sed 's/^/  /'
}

# COUNTDOWN 5 MINUTES WITH ALARM
countdown() {
	local seconds=$(( 60 * 5 ))
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
	# printf "\r\33[2K"
	echo -e "\r  finished"
	alarm
	date="$(date -Iminutes)"
	echo "$date,$1" >> $data_dir/chord-log.csv
	echo "$date,$2" >> $data_dir/chord-log.csv
}
alarm() {
	tput bel
	sleep 1
	tput bel
	sleep 1
	tput bel
}

wait_for_input() {
	echo
	read -n 1 -s -p "  $(accent_text Press key to continue...)" key
	if [ "$key" = "q" ]; then
		exit
	fi
}

# FORMATTING
gray="\033[38;2;120;120;120m"
reset="\033[0m"
accent_text() {
    echo -e "${gray}$@${reset}"
}

# CLEANUP ON EXIT
cleanup() {
    tput cnorm
	tput rmcup
}
trap cleanup EXIT

# INIT
notes=("A " "B " "C " "D " "E " "F " "G " "A#" "C#" "D#" "F#" "G#" "Ab" "Bb" "Db" "Eb" "Gb")
chord_types=("Major" "Minor" "7    " "Min 7" "Maj 7" "Power")
chord_forms=("E" "A" "D" "C" "G")
SIMPLE_MODE=false
INPUT_FILE=""
data_dir="$XDG_DATA_HOME/aug-scripts"
# config_file="$XDG_CONFIG_HOME/aug-scripts/config.toml"
config_file="./config.toml"
mkdir -p $data_dir
tput civis
tput smcup

# Parse Config
readarray -t chord_types < <(yq '.practice_chords.types[]' $config_file)
SIMPLE_MODE=$(yq '.practice_chords.simple' $config_file)

# Parse Flags
PARSED=$(getopt -o si: --long simple,input: -n "$0" -- "$@")
if [ $? -ne 0 ]; then
    exit 1
fi
eval set -- "$PARSED"
while true; do
	case "$1" in
		-s|--simple)
			SIMPLE_MODE=true
			shift
			;;
		-i|--input)
			INPUT_FILE="$2"
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

# MAIN LOOP
while true; do
	clear
	echo
	chord_1=$(rand_chord)
	pretty_print_chord $chord_1
	while true; do # prevent chord_1 and chord_2 being the same chord
		chord_2=$(rand_chord)
		if [[ "$chord_1" != "$chord_2" ]]; then
			break
		fi
	done
	pretty_print_chord $chord_2
	echo
	read -n 1 -s -p "  $(accent_text Press key to continue...)" key
	if [ "$key" = "q" ]; then
		exit
	elif [ "$key" = "h" ]; then
		clear
		print_chord_wrapper "$chord_1"
		print_chord_wrapper "$chord_2"
		wait_for_input
	fi
	countdown $chord_1 $chord_2
	wait_for_input
done

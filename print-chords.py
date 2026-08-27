#!/usr/bin/env python3
import sys
import argparse

NOTES = ['E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb']

# Format: e, B, G, D, A, E (High to Low)
# Data: "relative_fret,finger,type". '-' for unplayed strings. 
# Fret 0 represents the nut or the barre finger.
# Format: e, B, G, D, A, E (High to Low)
CHORD_DB = {
    'major': {
        'E': {
            'position': [0, 2, 2, 1, 0, 0],
            'finger': [0, 2, 3, 1, 0, 0],
            'type': ['r', '', '', '', '', '']
        },
        'A': {
            'position': [0, 0, 2, 2, 2, 0],
            'finger': [0, 0, 1, 2, 3, 0],
            'type': ['m', 'r', '', '', '', '']
        },
        'D': {
            'position': [0, 0, 0, 2, 3, 2],
            'finger': [0, 0, 0, 1, 3, 2],
            'type': ['m', 'm', 'r', '', '', '']
        },
        'G': {
            'position': [3, 2, 0, 0, 3, 3],
            'finger': [1, 2, 0, 0, 3, 4],
            'type': ['r', 'om', '', '', 'o', '']
        },
        'C': {
            'position': [0, 3, 2, 0, 1, 0],
            'finger': [0, 3, 2, 0, 1, 0],
            'type': ['m', 'r', '', '', '', '']
        },
    },
    'minor': {
        'E': {
            'position': [0, 2, 2, 0, 0, 0],
            'finger': [0, 1, 2, 0, 0, 0],
            'type': ['r', '', '', '', '', '']
        },
        'A': {
            'position': [0, 0, 2, 2, 1, 0],
            'finger': [0, 0, 2, 3, 1, 0],
            'type': ['m', 'r', '', '', '', '']
        },
        'D': {
            'position': [0, 0, 0, 2, 3, 1],
            'finger': [0, 0, 0, 2, 4, 1],
            'type': ['m', 'm', 'r', '', '', '']
        },
        'G': {
            'position': [3, 1, 0, 0, 0, 0],
            'finger': [3, 1, 0, 0, 0, 0],
            'type': ['r', '', '', '', 'm', 'm']
        },
        'C': {
            'position': [0, 3, 1, 0, 1, 0],
            'finger': [0, 4, 1, 0, 2, 0],
            'type': ['m', 'r', '', '', '', 'm']
        },
    },
    'power': {
        'E': {
            'position': [1, 3, 3, 0, 0, 0],
            'finger': [1, 3, 4, 0, 0, 0],
            'type': ['r', '', '', 'm', 'm', 'm']
        },
        'A': {
            'position': [0, 1, 3, 3, 0, 0],
            'finger': [0, 1, 3, 3, 0, 0],
            'type': ['m', 'r', '', '', 'm', 'm']
        },
        'D': {
            'position': [0, 0, 1, 3, 4, 0],
            'finger': [0, 0, 1, 3, 4, 0],
            'type': ['m', 'm', 'r', '', '', 'm']
        },
        'G': {
            'position': [0, 0, 0, 1, 4, 4],
            'finger': [0, 0, 0, 1, 4, 4],
            'type': ['m', 'm', 'm', 'r', '', '']
        },
        'C': {
            'position': [0, 3, 0, 0, 1, 0],
            'finger': [0, 3, 0, 0, 1, 0],
            'type': ['m', 'r', 'm', '', '', 'm']
        },
    },
    # 'chord': {
    #     'E': {
    #         'position': [0, 0, 0, 0, 0, 0],
    #         'finger': [0, 0, 0, 0, 0, 0],
    #         'type': ['', '', '', '', '', '']
    #     },
    #     'A': {
    #         'position': [0, 0, 0, 0, 0, 0],
    #         'finger': [0, 0, 0, 0, 0, 0],
    #         'type': ['', '', '', '', '', '']
    #     },
    #     'D': {
    #         'position': [0, 0, 0, 0, 0, 0],
    #         'finger': [0, 0, 0, 0, 0, 0],
    #         'type': ['', '', '', '', '', '']
    #     },
    #     'G': {
    #         'position': [0, 0, 0, 0, 0, 0],
    #         'finger': [0, 0, 0, 0, 0, 0],
    #         'type': ['', '', '', '', '', '']
    #     },
    #     'C': {
    #         'position': [0, 0, 0, 0, 0, 0],
    #         'finger': [0, 0, 0, 0, 0, 0],
    #         'type': ['', '', '', '', '', '']
    #     },
    # },
}

def calculate_offset(base_form_note, target_note):
    try:
        base_idx = next(i for i, n in enumerate(NOTES) if base_form_note in n)
        target_idx = next(i for i, n in enumerate(NOTES) if target_note in n)
        return (target_idx - base_idx) % 12
    except StopIteration:
        raise ValueError(f"Note '{target_note}' not found in chromatic scale.")

def parse_chord_data(chord_info, offset):
    strings = []
    positions = chord_info['position']
    fingers = chord_info['finger']
    types = chord_info['type']
    for pos, finger, typ in zip(positions, fingers, types):
        if 'm' in typ.lower():
            parsed_pos = None
        else:
            parsed_pos = pos + offset
        is_root = 'r' in typ.lower()
        strings.append({
            'pos': parsed_pos,
            'finger': str(finger) if finger != 0 else '-',
            'type': 'R' if is_root else '-'
        })
    return strings

def draw_horizontal(chord_data, title, offset, use_fingers, use_title):
    if use_title:
        print(f"{title}")

    # Print fret numbers
    fret_header = "  0   "
    if offset > 0:
        fret_header += f" {offset}   {offset+1}   {offset+2}   {offset+3}   {offset+4} "
    else:
        fret_header += "1   2   3   4   5 "
    print(fret_header)

    # print fret
    string_names = ['e', 'B', 'G', 'D', 'A', 'E'] # High 'e' at top
    for i, s in enumerate(chord_data):
        line = f"{string_names[i]} "
        # Header area: Muted / Root marker
        if s['pos'] is None:
            line += "\033[31mx\033[0m "
        elif s['type'] == 'R':
            line += "R "
        else:
            line += "  "

        # Draw base fretboard lines depending on layout constraints
        if offset > 0:
            if i == 0:
                line += "┄┬─│─┬───┬───┬───┬───┬┄"
            elif i == 5:
                line += "┄┴─│─┴───┴───┴───┴───┴┄"
            else:
                line += "┄┼─│─┼───┼───┼───┼───┼┄"
        else:
            if i == 0:
                line += "╭───┬───┬───┬───┬───┬┄"
            elif i == 5:
                line += "╰───┴───┴───┴───┴───┴┄"
            else:
                line += "├───┼───┼───┼───┼───┼┄"

        # Calculate marker placement exactly onto standard fret slots
        if s['pos'] is not None and s['pos'] > 0:
            marker = s['finger'] if use_fingers and s['finger'] != '-' else '●'

            if offset > 0:
                relative_pos = s['pos'] - offset
                if relative_pos == 0:
                    # Barre chord is active on this fret. We leave the `│` untouched 
                    # so the unbroken bar is rendered 'over' the fret position.
                    pass
                else:
                    insert_idx = 7 + (relative_pos * 4) 
                    line = line[:insert_idx] + marker + line[insert_idx+1:]
            else:
                insert_idx = 6 + ((s['pos'] - 1) * 4)
                line = line[:insert_idx] + marker + line[insert_idx+1:]
        print(line)

if __name__ == "__main__":
    types = []
    for key in CHORD_DB: types.append(key)

    parser = argparse.ArgumentParser(description="Render guitar chord tablatures.")
    parser.add_argument("note", help="Root note (e.g., C, G, F#)")
    parser.add_argument("type", choices=types, help="Chord type")
    parser.add_argument("shape", choices=['C', 'A', 'G', 'E', 'D'], help="CAGED shape to use")
    parser.add_argument("-f", "--fingers", action="store_true", help="Display finger numbers instead of dots")
    parser.add_argument("--title", action="store_true", help="Display title")

    args = parser.parse_args()

    try:
        offset = calculate_offset(args.shape, args.note)
        chord_lines = CHORD_DB[args.type][args.shape]
        parsed_data = reversed(parse_chord_data(chord_lines, offset))
        title = f"{args.note} {args.type} ({args.shape} Shape)"
        draw_horizontal(parsed_data, title, offset, args.fingers, args.title)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

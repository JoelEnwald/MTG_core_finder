# First get all the Core sets, Duels cores, Conspiracies and MTGO 540 as data
import json
import numpy
import os
import pandas as pd
import csv
import numpy as np
import time

ALL_SETS_PATH = 'D:/Games/MTG/AllSets.json'
MODERN_SETS_PATH = 'D:/Games/MTG/Modern.json'
STANDARD_SETS_PATH = 'D:/Games/MTG/Standard.json'
MATRIX_PATH = 'D:/Games/MTG/'
CSV_DATA_PATH = "C:/Users/joele/OneDrive/Games/MTG/Data/Code data/"

def create_and_save_conn_matrix(additional_sets):
    path = ALL_SETS_PATH
    json_file = open(path, encoding='utf-8')
    json_str = json_file.read()
    #json_str = pd.load_json(json_path, encoding='UTF-8')
    dict_data = json.loads(json_str)

    path_std = STANDARD_SETS_PATH
    json_file = open(path_std, encoding='utf-8')
    json_str = json_file.read()
    #json_str = pd.load_json(json_path, encoding='UTF-8')
    dict_data_std = json.loads(json_str)

    path_mod = MODERN_SETS_PATH
    json_file = open(path_mod, encoding='utf-8')
    json_str = json_file.read()
    #json_str = pd.load_json(json_path, encoding='UTF-8')
    dict_data_mod = json.loads(json_str)

    if (path == ALL_SETS_PATH):
        con_sets = ['CNS', 'CN2']
        con_dict_data = dict()
        for con_set in con_sets:
            con_dict_data[con_set] = dict_data[con_set]

    # The sets that need to be removed are XLN, RIX, M19, DOM, GRN and RNA
    postmod_sets = ['XLN', 'RIX', 'M19', 'DOM', 'GRN', 'RNA']

    # Dictionary only for the postmodern sets
    postmod_dict_data = dict()
    for set_name in postmod_sets:
        postmod_dict_data[set_name] = dict_data_mod[set_name]

    # Remove the postmodern sets
    for set_name in postmod_sets:
        dict_data_mod.pop(set_name)

    # Make a dict with all the sets and the cards in the sets
    sets_cards = dict()
    cards_sets = dict()

    # Get sets from csv files
    if additional_sets:
        for filename in os.listdir(CSV_DATA_PATH):
            with open(os.path.join(CSV_DATA_PATH, filename), 'r') as csvfile:
                set_card_list = []
                card_set_list = []
                filereader = csv.reader(csvfile, delimiter = ';')
                for row in filereader:
                    card_name = row[0]
                    # Add card to cards of sets
                    set_card_list.append(card_name)
                    # Add set to sets of cards
                    if card_name in cards_sets.keys():
                        curr_sets = cards_sets[card_name]
                        curr_sets.append(filename)
                        cards_sets[card_name] = curr_sets
                    else:
                        new_set_list = []; new_set_list.append(filename)
                        cards_sets[card_name] = new_set_list

            sets_cards[filename] = set_card_list

    core_sets = ['8ED', '9ED', '10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'ORI']
    #core_sets = ['LEB', '2ED', '3ED', '4ED', '5ED', '6ED', '7ED', '8ED', '9ED', '10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'ORI', 'W16', 'W17', 'M19']
    #core_sets = ['ALA','CON','ARB','ZEN', 'WWK', 'ROE', 'SOM', 'MBS', 'NPH', 'ISD', 'DKA', 'AVR', 'RTR', 'GTC', 'DGM','THS','BNG','JOU']
    #core_sets = ['M10', 'M11', 'M12', 'M13', 'M14']

    card_rarities = dict()
    rarities_key = {'common':0, 'uncommon':1, 'rare':2, 'mythic':3}
    for set_name in dict_data_mod:
        # Checklist for which cards have been added for this set. Some cards are in sets twice
        cards_added_in_this_set = set()
        set_info = dict_data_mod[set_name]
        cards = set_info['cards']

        # Only run this if we are looking at one of the core sets. WHY?
        # Remove duplicate cards
        if set_name in core_sets:
            sets_cards[set_name] = []
            # Add the cards to the print counts
            for i in range(0, len(cards)):
                card_name = cards[i]['name']

                # Looking at specific colors. Remove if needed
                # if 'B' in cards[i]['colors']:
                # ONLY COUNT CARD ONCE PER SET
                if not card_name in cards_added_in_this_set:
                    # Add card to a set's list
                    sets_cards[set_name].append(card_name)
                    # Add set to a card's list
                    if card_name in cards_sets.keys():
                        cards_sets[card_name].append(set_name)
                    else:
                        new_set_list = []; new_set_list.append(set_name)
                        cards_sets[card_name] = new_set_list

                cards_added_in_this_set.add(card_name)

    # Add W16W17 deck cards
    set_card_list = []
    card_set_list = []
    for filename in os.listdir(CSV_DATA_PATH):
        if filename == "W16W17.csv":
            with open(os.path.join(CSV_DATA_PATH, filename), 'r') as csvfile:
                filereader = csv.reader(csvfile, delimiter=';')
                for row in filereader:
                    card_name = row[0]
                    # Add card to cards of sets
                    set_card_list.append(card_name)
                    # Add set to sets of cards
                    if card_name in cards_sets.keys():
                        curr_sets = cards_sets[card_name]
                        curr_sets.append(filename)
                        cards_sets[card_name] = curr_sets
                    else:
                        new_set_list = [];
                        new_set_list.append(filename)
                        cards_sets[card_name] = new_set_list

            sets_cards[filename] = set_card_list

    conn_matrix = np.zeros((len(cards_sets.keys()), len(cards_sets.keys())))
    # Sorted list of cards
    master_cards_list = list(cards_sets.keys())
    master_cards_list.sort()

    # Add cards printed in same set as connections to connection_matrix
    for card_set in sets_cards.keys():
        # normalization
        # weight = 1/len(sets_cards[card_set])
        weight = 1
        for cardA in sets_cards[card_set]:
            for cardB in sets_cards[card_set]:
                if cardA != cardB:
                    conn_matrix[master_cards_list.index(cardA)][master_cards_list.index(cardB)] += weight

    # Save parameters
    sets_cards_json = json.dumps(sets_cards)
    cards_sets_json = json.dumps(cards_sets)
    if additional_sets:
        np.save(os.path.join(MATRIX_PATH, "conn_matrix.npy"), conn_matrix)
        np.save(os.path.join(MATRIX_PATH, "master_cards_list.npy"), master_cards_list)
        sets_cards_file = open(os.path.join(MATRIX_PATH, "sets_cards.json"), "w")
        cards_sets_file = open(os.path.join(MATRIX_PATH, "cards_sets.json"), "w")
    else:
        np.save(os.path.join(MATRIX_PATH, "conn_matrix_AMCS.npy"), conn_matrix)
        np.save(os.path.join(MATRIX_PATH, "master_cards_list_AMCS.npy"), master_cards_list)
        sets_cards_file = open(os.path.join(MATRIX_PATH, "sets_cards_AMCS.json"), "w")
        cards_sets_file = open(os.path.join(MATRIX_PATH, "cards_sets_AMCS.json"), "w")
    sets_cards_file.write(sets_cards_json)
    sets_cards_file.close()
    cards_sets_file.write(cards_sets_json)
    cards_sets_file.close()

create_and_save_conn_matrix(additional_sets=True)

# Load parameters
conn_matrix = np.load(os.path.join(MATRIX_PATH, "conn_matrix_normalized.npy"))
master_cards_list = np.load(os.path.join(MATRIX_PATH, "master_cards_list.npy"))
with open(os.path.join(MATRIX_PATH, "sets_cards.json")) as sets_cards_file:
    sets_cards = json.load(sets_cards_file)
with open(os.path.join(MATRIX_PATH, "cards_sets.json")) as cards_sets_file:
    cards_sets = json.load(cards_sets_file)
# Convert to list
master_cards_list = list(master_cards_list)
core_cards = []
# Find starting set for growing
#row_sums = sum(conn_matrix)
#for i in range(0, 15):
#    max_value = max(row_sums)
#    for j in range(0, len(row_sums)):
#        if row_sums[j] == max_value:
#            core_cards.append(master_cards_list[j])
#            row_sums[j] = 0
# Basic lands
core_cards = ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']
# Cards with largest total strength of connections, one from each color
#core_cards = ['Serra Angel', 'Mind Rot', 'Shock', 'Giant Growth', 'Negate']
set_counts = np.zeros(len(sets_cards.keys()))
set_sizes = np.zeros(len(sets_cards.keys()))
i = 0
for set_name in sets_cards.keys():
    set_sizes[i] = len(sets_cards[set_name])
    i += 1

# Go through the cards, always adding the card to the core set that has the most
# connections to the current core set
while len(core_cards) < 300:
    max_conn_strength = 0
    cards_to_add = []
    # Go through every card to check their connection strength to curr. core set
    for i in range(0, len(conn_matrix)):
        # Check the card is not already in the core set CAN BE MADE FASTER
        if not master_cards_list[i] in core_cards:
            total_conn_strength = 0
            # Check connection to every current core set card
            for card in core_cards:
                card_index = master_cards_list.index(card)
                conn_strength = conn_matrix[i][card_index]
                # Add connection strength to total of cards in core set
                total_conn_strength += conn_strength
            # If total conn strength larger than current maximum, make a new list of cards
            # to add with only the new card
            if total_conn_strength > max_conn_strength:
                cards_to_add = []
                cards_to_add.append(master_cards_list[i])
                max_conn_strength = total_conn_strength
            # If total conn strength equal to current maximum, add current card to cards to
            # be added
            elif total_conn_strength == max_conn_strength:
                cards_to_add.append(master_cards_list[i])
    # Show cards that will be added, add them to core set
    print(cards_to_add)
    for card_name in cards_to_add:
        core_cards.append(card_name)
        # Print sets the added card belongs to
        print(cards_sets[card_name])
        cardname_sets = cards_sets[card_name]
        for set_name in cardname_sets:
            set_counts[list(sets_cards.keys()).index(set_name)] += 1
    # Print statistics about what percentage of each set has been added
    print(np.round(set_counts/set_sizes, 2))
    print(str(len(core_cards)))

for card_name in core_cards:
    print(card_name)

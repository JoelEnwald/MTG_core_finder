# To do:

# AHHHHH! REVELATION!:
# Choose cards by how many different decks/sets they were in!
# Choose the amount of copies by how many of them there were on average in the decks/sets
# the cards was in!
# Separates the repeats of a card in decks/sets from repeats due to many of them being needed!
# -> Gets more rares! Does not get cards in few decks/sets with multiple copies in each!
# Separates card inclusion and the amount needed!
# Does it give the right ratios???
# If Pacifism has 2 copies on average in 10 decks, and it gets chosen, then it would...
# need to have CUBESIZE/AVGDECKSIZE copies?! Maybe not
# No?! D: What do? I'll figure this out
# Calculate PRINT_COUNT and AVG_MASS
# PRINT_COUNT should affect how many times the card appears in cube? Maybe a multiplier?

# Actually, since players need to pick cards when several decks are combined, best results
# might be achieved by just taking the (ramped) average of all decks. Try this!
# Create the average draft environment cube!
# Currently smaller sets have more weight than big ones! Should I instead just
# weigh rarity equally??
# Check which sets were designed to be drafted! Only use those!
# Combine functional reprints!
# Create the draft set-precon deck hybrid cube, by scaling the counts so the total masses
# of the draft sets and precon decks are in a ratio of 2:1

import json
import numpy
import os
import pandas as pd
import numpy as np
import csv

ALL_CARDS_PATH = 'D:/Games/MTG/AllCards.json'
PATH_SETS = 'D:/Games/MTG/AllSets.json'
PATH_DECKS = "D:/Games/MTG/Main set intro,theme,pw decks"
PATH_RESULTS = "C:/Users/joele/OneDrive/Games/MTG/Data"
TARGET_CUBE_SIZE = 360
RARITY_LABELS = ['common', 'uncommon', 'rare', 'mythic']
RARITY_OCCURRENCES = [11/15, 3/15, (7/8)/15, (1/8)/15]
COLOR_TO_INDEX = {'W':0, 'U':1, 'B':2, 'R':3, 'G':4}
RARITY_TO_INDEX = {'common':0, 'uncommon':1, 'rare':2, 'mythic':3}
INDEX_TO_RARITY = {0:'common', 1:'uncommon', 2:'rare', 3:'mythic'}

def avg_deck_card_rarity_type_and_cmc_portion_finder():
    total_mass = 0
    # For each color, multicolor, colorless: commons, uncommons, rares, mythics
    color_rarity_amounts = np.zeros((7, 4))
    # For each color, multicolor, colorless: Creatures, Instants/Sorceries, Auras/Equipment,
    # non-Aura Enchantments/non-Equipment Artifacts, Planeswalkers, and Land
    color_type_amounts = np.zeros((7, 6))
    # For each color, multicolor, colorless: Converted mana costs 0-1, 2, 3, 4, 5, and 6+
    # These buckets are chosen so that there wouldn't be too many, and that they would be roughly
    # equal in size.
    color_cmc_amounts = np.zeros((7, 6))
    # What about variable mana costs? How are they listed?
    for deck_name in os.listdir(PATH_DECKS):
        json_file = open(os.path.join(PATH_DECKS, deck_name), encoding='utf-8')
        json_str = json_file.read()
        dict_data_deck = json.loads(json_str)
        set_name = dict_data_deck['code']
        if set_name in main_sets:
            set_weight = main_set_points[main_sets.index(set_name)]
            # For each card in deck
            for card in dict_data_deck['mainBoard']:
                if 'Basic' not in card['type']:
                    # Determine the card color slot
                    if len(card['colors']) > 1:
                        color_index = 5
                    elif len(card['colors']) < 1:
                        color_index = 6
                    else:
                        color_index = COLOR_TO_INDEX[card['colors'][0]]
                    # Determine the card type slot
                    type_index = -1
                    if 'Creature' in card['types']:
                        type_index = 0
                    elif 'Instant' in card['types'] or 'Sorcery' in card['types']:
                        type_index = 1
                    elif 'Aura' in card['subtypes'] or 'Equipment' in card['subtypes']:
                        type_index = 2
                    elif 'Enchantment' in card['types'] or 'Artifact' in card['types']:
                        type_index = 3
                    elif 'Planeswalker' in card['types']:
                        type_index = 4
                    elif 'Land' in card['types']:
                        type_index = 5
                    # Determine the card rarity slot
                    rarity_index = RARITY_TO_INDEX[card['rarity']]
                    # Determine the card cmc slot
                    if card['convertedManaCost'] <= 1:
                        cmc_index = 0
                    elif card['convertedManaCost'] >= 6:
                        cmc_index = 5
                    else:
                        cmc_index = int(card['convertedManaCost']) - 1
                    # Weight the cards linearly by the set their deck is from
                    color_type_amounts[color_index][type_index] += set_weight * card['count']
                    color_rarity_amounts[color_index][rarity_index] += set_weight*card['count']
                    color_cmc_amounts[color_index][cmc_index] += set_weight*card['count']
                    total_mass += set_weight*card['count']
    color_type_amounts = color_type_amounts/total_mass
    color_rarity_amounts = color_rarity_amounts/total_mass
    color_cmc_amounts = color_cmc_amounts/total_mass
    color_amounts = np.zeros(5)
    for i in range(0, 5):
        color_amounts[i] = sum(color_rarity_amounts[i, :])
    avg_color_portion = 0
    for i in range(0, 5):
        avg_color_portion += color_amounts[i]
    avg_color_portion /= 5
    # Balance the colors
    for i in range(0, 5):
        color_type_amounts[i, :] = avg_color_portion * color_type_amounts[i, :] / color_amounts[i]
        color_rarity_amounts[i, :] = avg_color_portion * color_rarity_amounts[i, :] / color_amounts[i]
        color_cmc_amounts[i, :] = avg_color_portion * color_cmc_amounts[i, :] / color_amounts[i]
    # Normalize to the amount of cards wanted
    color_type_amounts = color_type_amounts*410
    color_rarity_amounts = color_rarity_amounts*410
    color_cmc_amounts = color_cmc_amounts*410
    color_type_amounts = np.round(color_type_amounts)
    color_rarity_amounts = np.round(color_rarity_amounts)
    color_cmc_amounts = np.round(color_cmc_amounts)
    hallo = 5


# Note: W16 and W17 sets included
#main_sets = ["LEB","2ED","ARN","ATQ","3ED","LEG","DRK","FEM","4ED","ICE","HML","ALL","MIR","VIS","5ED","WTH","TMP","STH","EXO","USG","ULG","6ED","UDS","MMQ","NEM","PCY","INV","PLS","7ED","APC","ODY","TOR","JUD","ONS","LGN","SCG","8ED","MRD","DST","5DN","CHK","BOK","SOK","9ED","RAV","GPT","DIS","CSP","TSP","PLC","FUT","10E","LRW","MOR","SHM","EVE","ALA","CON","ARB","M10","ZEN","WWK","ROE","M11","SOM","MBS","NPH","M12","ISD","DKA","AVR","M13","RTR","GTC","DGM","M14","THS","BNG","JOU","M15","KTK","FRF","DTK","ORI","BFZ","OGW","SOI","EMN","KLD","AER","AKH","HOU","XLN","RIX","DOM","M19","GRN","RNA","WAR","M20"]
main_sets = ["ICE","HML","ALL","MIR","VIS","5ED","WTH","TMP","STH","EXO","USG","ULG","6ED","UDS","MMQ","NEM","PCY","INV","PLS","7ED","APC","ODY","TOR","JUD","ONS","LGN","SCG","8ED","MRD","DST","5DN","CHK","BOK","SOK","9ED","RAV","GPT","DIS","CSP","TSP","PLC","FUT","10E","LRW","MOR","SHM","EVE","ALA","CON","ARB","M10","ZEN","WWK","ROE","M11","SOM","MBS","NPH","M12","ISD","DKA","AVR","M13","RTR","GTC","DGM","M14","THS","BNG","JOU","M15","KTK","FRF","DTK","ORI","BFZ","OGW","SOI","EMN","KLD","AER","AKH","HOU","XLN","RIX","DOM","M19","GRN","RNA","WAR","M20"]
#main_sets = ["7ED", "8ED", "9ED", "10E", "M10", "M11", "M12", "M13", "M14", "M15", "ORI"]
# Sets without planeswalker decks
#main_sets = ["ICE","HML","ALL","MIR","VIS","5ED","WTH","TMP","STH","EXO","USG","ULG","6ED","UDS","MMQ","NEM","PCY","INV","PLS","7ED","APC","ODY","TOR","JUD","ONS","LGN","SCG","8ED","MRD","DST","5DN","CHK","BOK","SOK","9ED","RAV","GPT","DIS","CSP","TSP","PLC","FUT","10E","LRW","MOR","SHM","EVE","ALA","CON","ARB","M10","ZEN","WWK","ROE","M11","SOM","MBS","NPH","M12","ISD","DKA","AVR","M13","RTR","GTC","DGM","M14","THS","BNG","JOU","M15","KTK","FRF","DTK","ORI","BFZ","OGW","SOI","EMN"]

# Even points
#main_set_points = list(np.ones(1000))
# Ramped points
main_set_points = list(range(1, 1000))

path_cards = ALL_CARDS_PATH
json_file = open(path_cards, encoding='utf-8')
json_str = json_file.read()
dict_data_cards = json.loads(json_str)

avg_deck_card_rarity_type_and_cmc_portion_finder()

# Get the functional reprints mapping
dict_func_reprint = dict()
with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + 'Functional reprints.csv') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in csvreader:
        hallo = 5


# Go through the theme decks
print_counts_decks = dict()
card_avg_copies = dict()
dict_data_decks = dict()
total_points_decks = 0
# For each deck
for deck_name in os.listdir(PATH_DECKS):
    json_file = open(os.path.join(PATH_DECKS, deck_name), encoding='utf-8')
    json_str = json_file.read()
    dict_data_deck = json.loads(json_str)
    set_name = dict_data_deck['code']
    if set_name in main_sets:
        set_weight = main_set_points[main_sets.index(set_name)]
        # For each card in deck
        for card in dict_data_deck['mainBoard']:
            if 'Basic' not in card['type']:
                # If the card is in the deck, increase the card's print count by one
                # Card already in dict
                if card['name'] in print_counts_decks.keys():
                    print_counts_decks[card['name']] = print_counts_decks[card['name']] + set_weight * card['count']
                    # Keep a running average of the copies of a card in a deck
                    #n = print_counts_decks[card['name']]
                    #card_avg_copies[card['name']] = card_avg_copies[card['name']]*(n-1)/n + card['count']/n
                # First time card added to dict
                else:
                    print_counts_decks[card['name']] = set_weight * card['count']
                    #card_avg_copies[card['name']] = card['count']
                # Keep count of total points
                total_points_decks += set_weight * card['count']

# Get the Arena decks, add print counts to total_points_decks
# Does not currently work with ramped scores
for i in range(1, 5):
    deck_file_name = "Magic Arena NPE Starting decks " + str(i) + " cards.csv"
    with open(PATH_RESULTS + "\\" + deck_file_name) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for card_data in csvreader:
            if card_data[0] in print_counts_decks.keys():
                print_counts_decks[card_data[0]] += int(card_data[1])
            else:
                print_counts_decks[card_data[0]] = int(card_data[1])
            total_points_decks += int(card_data[1])

# Normalize card values so they sum to ~360
# Make a new dict of cards with normalized nonzero amounts
normalized_sum = 0
counts_decks_normalized = dict()
# Adjust this to get the amount of cards you want
point_multiplier = 0.16
for card_name in print_counts_decks:
    if round(point_multiplier*print_counts_decks[card_name]) != 0:
        counts_decks_normalized[card_name] = round(point_multiplier*print_counts_decks[card_name])
        normalized_sum += round(point_multiplier*print_counts_decks[card_name])

# Write results to file
prints_file = open("prints_file_decks.txt", "w")
for card_name in counts_decks_normalized:
    card_count = round(counts_decks_normalized[card_name])
    for i in range(0, int(card_count)):
        prints_file.write(card_name + "\n")
prints_file.close()

card_portions_sets = dict()
dict_data_sets = dict()
total_cards_sets = 0
total_card_mass = 0
json_file_sets = open(PATH_SETS, encoding='utf-8')
json_str_sets = json_file_sets.read()
dict_data_sets = json.loads(json_str_sets)
# Go through the sets to calculate each card's portion in each set's drafting
# Currently small sets are weighted more than big ones!
for set_name in main_sets:
    set_data = dict_data_sets[set_name]
    # Count the number of commons, uncommons, rares and mythics in set
    set_rarity_amounts = [0, 0, 0, 0]
    for card in set_data['cards']:
        if 'Basic' not in card['type']:
            set_rarity_amounts[RARITY_LABELS.index(card['rarity'])] += 1
    # Go through the cards again, now assigning each card its portion of appearance in
    # drafting the set.
    set_weight = main_set_points[main_sets.index(set_name)]
    for card in set_data['cards']:
        if 'Basic' not in card['type']:
            card_rarity_index = RARITY_LABELS.index(card['rarity'])
            card_mass = set_weight * RARITY_OCCURRENCES[card_rarity_index] / set_rarity_amounts[card_rarity_index]
            # With these masses, the cards in a set sum to (1)
            if card['name'] not in card_portions_sets.keys():
                card_portions_sets[card['name']] = card_mass
            else:
                card_portions_sets[card['name']] = card_portions_sets[card['name']] + card_mass
            # Should currently only be close to sum over set weights, since I assume that
            # every set has mythics, which isn't true.
            total_card_mass += card_mass
    # Also counts basics
    total_cards_sets += len(set_data['cards'])

card_portions_sets_normed = dict()
total_card_mass_normed = 0
# Normalize and round the card masses
for card_name in card_portions_sets:
    card_mass_normalized = round(0.51*card_portions_sets[card_name])
    if card_mass_normalized != 0:
        card_portions_sets_normed[card_name] = card_mass_normalized
        total_card_mass_normed += card_mass_normalized

# Write results to file
prints_file = open("prints_file_sets.txt", "w")
for card_name in card_portions_sets_normed:
    card_count = card_portions_sets_normed[card_name]
    for i in range(0, card_count):
        prints_file.write(card_name + "\n")
prints_file.close()



combined_masses = dict()
# Combine deck and set card masses, with total masses in a ratio of 1:2
for card in print_counts_decks:
    # Normalize so the total mass of cards is 1, multiply to get the right ratio
    combined_masses[card] = 1*print_counts_decks[card]/total_points_decks
for card in card_portions_sets:
    if card in combined_masses:
        combined_masses[card] += 2*card_portions_sets[card]/total_card_mass
    else:
        combined_masses[card] = 2*card_portions_sets[card]/total_card_mass

combined_masses_normed = dict()
total_combined_mass_normed = 0
# Normalize and round the card masses
for card_name in combined_masses:
    card_mass_normalized = round(625*combined_masses[card_name])
    if card_mass_normalized != 0:
        combined_masses_normed[card_name] = card_mass_normalized
        total_combined_mass_normed += card_mass_normalized

# Write results to file
prints_file = open("prints_file_combined.txt", "w")
for card_name in combined_masses_normed:
    card_count = combined_masses_normed[card_name]
    for i in range(0, card_count):
        prints_file.write(card_name + "\n")
prints_file.close()
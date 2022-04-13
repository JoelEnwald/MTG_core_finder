import json
import numpy
import os
import pandas as pd
import numpy as np
import csv

ALL_CARDS_PATH = 'D:/Games/MTG/AtomicCards.json'
ALL_SETS_PATH = 'D:/Games/MTG/AllPrintings.json'
# New location
PATH_ALL_SETS = "D:/Games/MTG/AllSetFiles"
PATH_MODERN_SETS = 'D:/Games/MTG/Modern.json'
PATH_STANDARD_SETS = 'D:/Games/MTG/Standard.json'
PATH_DECKS = "D:/Games/MTG/Main set intro,theme,pw decks"
PATH_DECKS_2COLOR = "D:/Games/MTG/2-colored core set theme decks"
RARITY_TO_INDEX = {'common':0, 'uncommon':1, 'rare':2, 'mythic':3}
INDEX_TO_RARITY = {0:'common', 1:'uncommon', 2:'rare', 3:'mythic'}
COLOR_TO_INDEX = {'W':0, 'U':1, 'B':2, 'R':3, 'G':4}
N_SETS = 106



# Automatic color balancing
def color_balance():
    # ratio for W/U/B/R/G/C
    target_col_amounts = {'W': 40, 'U': 40, 'B': 40, 'R': 40, 'G': 40, 'C': 40}
    curr_col_amounts = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}

    results = core_set_results
    cards_to_add = {'W': [], 'U': [], 'B': [], 'R': [], 'G': [], 'C': []}
    color_amounts_to_add = []
    top_cards = []
    something_was_added = 1
    i = 0
    while something_was_added:
        curr_best_score = results[i][1]
        # Keep score of the best score, add cards with same score in a batch
        while results[i][1] == curr_best_score:
            card_name = results[i][0]
            card_colors = dict_data_cards[card_name]['colors']
            # Add only monocolored and colorless cards
            if len(card_colors) <= 1:
                if len(card_colors) == 1:
                    card_color = card_colors[0]
                else:
                    card_color = 'C'
                cards_to_add[card_color].append(card_name)
            curr_best_score = results[i][1]
            i += 1
        # Add all the cards with the next largest number of points
        something_was_added = 0
        for color in cards_to_add:
            if curr_col_amounts[color] < target_col_amounts[color]:
                for card_name in cards_to_add[color]:
                    top_cards.append(card_name)
                    print(card_name)
                    curr_col_amounts[color] += 1
                    something_was_added = 1

        print("")
        cards_to_add = {'W': [], 'U': [], 'B': [], 'R': [], 'G': [], 'C': []}
    return

def card_slotter():
    total_slots = 390
    cards_list = []
    # For each color, multicolor, colorless: commons, uncommons, rares, mythics
    #color_rarity_slots = [[36, 17, 4, 0], [36, 17, 4, 0], [36, 17, 4, 0], [36, 17, 4, 0], [36, 17, 4, 0], [10, 13, 4, 0], [26, 17, 2, 0]]
    # 0 multi-colored cards
    color_rarity_slots = [[42, 18, 5, 0], [42, 18, 5, 0], [42, 18, 5, 0], [42, 18, 5, 0], [42, 18, 5, 0], [0, 0, 0, 0], [16, 25, 2, 0]]
    # For each color, multicolor, colorless: Creatures, Instants/Sorceries, Auras/Equipment,
    # non-Aura Enchantments/non-Equipment Artifacts, Planeswalkers, and Land
    #color_type_slots = [[38, 12, 5, 2, 0, 0], [35, 17, 4, 1, 0, 0], [36, 16, 3, 2, 0, 0], [32, 22, 1, 2, 0, 0], [38, 15, 3, 1, 0, 0], [20, 5, 1, 1, 0, 0], [15, 0, 4, 11, 0, 15]]
    # 0 multi-colored cards
    color_type_slots = [[43, 14, 6, 2, 0, 0], [40, 20, 4, 1, 0, 0], [42, 18, 3, 2, 0, 0], [37, 25, 1, 2, 0, 0], [44, 17, 3, 1, 0, 0], [0, 0, 0, 0, 0, 0], [22, 0, 5, 16, 0, 0]]
    # For each color, multicolor, colorless: Converted mana costs 0-1, 2, 3, 4, 5, and 6+
    # These buckets are chosen so that there wouldn't be too many, and that they would be roughly
    # equal in size.
    color_cmc_slots = [[10, 21, 15, 11, 6, 2], [7, 15, 18, 12, 7, 6], [8, 15, 17, 12, 8, 5], [10, 16, 16, 11, 8, 4], [8, 18, 14, 10, 8, 7], [0, 0, 0, 0, 0, 0], [7, 11, 12, 7, 2, 4]]
    with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + 'Main sets ramped points.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in csvreader:
            card_name = row[0]
            card_data = dict_data_cards[card_name]
            # Determine the card color
            if len(card_data['colors']) > 1:
                card_color_index = 5
            elif len(card_data['colors']) < 1:
                card_color_index = 6
            else:
                card_color_index = COLOR_TO_INDEX[card_data['colors'][0]]
            # Determine the card rarity slot
            card_rarity_index = card_rarity_finder(card_data)
            # Determine the card type slot
            card_type_index = -1
            if 'Creature' in card_data['types']:
                card_type_index = 0
            elif 'Instant' in card_data['types'] or 'Sorcery' in card_data['types']:
                card_type_index = 1
            elif 'Aura' in card_data['subtypes'] or 'Equipment' in card_data['subtypes']:
                card_type_index = 2
            elif 'Enchantment' in card_data['types'] or 'Artifact' in card_data['types']:
                card_type_index = 3
            elif 'Planeswalker' in card_data['types']:
                card_type_index = 4
            elif 'Land' in card_data['types']:
                card_type_index = 5
            # Determine the card cmc slot
            if card_data['convertedManaCost'] <= 1:
                card_cmc_index = 0
            elif card_data['convertedManaCost'] >= 6:
                card_cmc_index = 5
            else:
                card_cmc_index = int(card_data['convertedManaCost']) - 1
            # Check if card fits. If yes, it takes up a slot, in both tables
            if color_rarity_slots[card_color_index][card_rarity_index] > 0\
                    and color_type_slots[card_color_index][card_type_index] > 0\
                    and color_cmc_slots[card_color_index][card_cmc_index] > 0:
                # If the card is common, it takes 2 slots since I want duplicates
                if card_rarity_index == 0:
                    amount = 2
                else:
                    amount = 1
                color_rarity_slots[card_color_index][card_rarity_index] -= amount
                color_type_slots[card_color_index][card_type_index] -= amount
                color_cmc_slots[card_color_index][card_cmc_index] -= amount
                total_slots -= amount
                for i in range(0, amount):
                    cards_list.append(card_name)
    # Write results to file
    prints_file = open("prints_file.txt", "w")
    for card_name in cards_list:
        prints_file.write(card_name + "\n")
    prints_file.close()

# Find the average rarity of a card by looking at its rarities through all sets
# Weigh rarities linearly, similarly to ramped points for sets
def card_rarity_finder(card_data):
    rarity_index_sum = 0
    weights_sum = 0
    rarity_weights = list(range(1, 1000))
    card_sets = card_data['printings']
    for i in range(0, len(card_sets)):
        card_set = card_sets[i]
        set_data = dict_data_sets[card_set]
        set_cards_list = set_data['cards']
        # Super slow to do this every time
        for j in range(0, len(set_cards_list)):
            set_card_data = set_cards_list[j]
            if set_card_data['name'] == card_data['name']:
                rarity_index_sum += rarity_weights[i]*RARITY_TO_INDEX[set_card_data['rarity']]
                weights_sum += rarity_weights[i]
    avg_weighted_rarity = round(rarity_index_sum/weights_sum)
    return avg_weighted_rarity

# Get the averaged rarity based on rarities
def avg_rarity(rarity_indices):
    weight = 1
    total_weight = 0
    rarity_weighted = 0
    # Start with weighted average
    for rarity_index in rarity_indices:
        rarity_weighted += rarity_index*weight
        total_weight += weight
        weight += 1
    rarity_weighted /= total_weight
    rarity_decimal = rarity_weighted - np.floor(rarity_weighted)
    if not 0.4999 < rarity_decimal < 0.5001:
        return int(np.round(rarity_weighted))
    # If that doesn't work, use a regular average
    else:
        rarity_avg = np.sum(rarity_indices)/len(rarity_indices)
    rarity_decimal = rarity_avg - np.floor(rarity_avg)
    if not 0.4999 < rarity_decimal < 0.5001:
        return int(np.round(rarity_avg))
    # If that doesn't work, just return the most recent rarity
    else:
        return rarity_indices[len(rarity_indices)-1]


# Get the average points for different types, rarities and cmc's of cards
def cards_pointsavgs_by_type_rarity_cmc(cards_attributes):
    type_avgpoints = {'Creature': 0, 'Instant': 0, 'Sorcery': 0, 'Enchantment': 0, 'Artifact': 0, 'Planeswalker': 0,
                      'Land': 0}
    type_counts = {'Creature': 0, 'Instant': 0, 'Sorcery': 0, 'Enchantment': 0, 'Artifact': 0, 'Planeswalker': 0,
                   'Land': 0}
    rarity_avgpoints = np.zeros(4)
    rarity_counts = np.zeros(4)
    #cmc_avgpoints = np.zeros(17)
    #cmc_counts = np.zeros(17)
    total_avgpoints = 0

    for card_name in cards_attributes:
        for card_type in cards_attributes[card_name]['types']:
            if card_type in type_avgpoints:
                type_avgpoints[card_type] += cards_attributes[card_name]['points']
                type_counts[card_type] += 1
        rarity_index = cards_attributes[card_name]['avg_rarity']
        rarity_avgpoints[rarity_index] += cards_attributes[card_name]['points']
        rarity_counts[rarity_index] += 1
        #cmc_avgpoints[int(cards_attributes[card_name]['cmc'])] += cards_attributes[card_name]['points']
        #cmc_counts[int(cards_attributes[card_name]['cmc'])] += 1
        total_avgpoints += cards_attributes[card_name]['points']
    # Divide points by card count
    for card_type in type_avgpoints:
        type_avgpoints[card_type] /= type_counts[card_type]
    # Divide points by card count
    for i in range(0, 4):
        rarity_avgpoints[i] /= rarity_counts[i]
    # Divide points by card count
    #for i in range(0, 17):
    #    cmc_avgpoints[i] /= cmc_counts[i]
    total_avgpoints /= len(cards_attributes)

    return type_avgpoints, rarity_avgpoints, total_avgpoints #, cmc_avgpoints

def find_best_decks(main_set_print_counts):
    lands_to_color_ref = {"Plains":"W", "Island":"U", "Swamp":"B", "Mountain":"R", "Forest":"G"}
    deck_scores = dict()
    data_decks = dict()
    # Go through core set decks M10 - ORI
    for deck_file_name in os.listdir(PATH_DECKS_2COLOR):
        data_deck = dict()
        deck_size = 0
        land_count_a = 0
        land_count_b = 0
        deck_score = 0
        json_file = open(PATH_DECKS_2COLOR + "/" + deck_file_name, encoding='utf-8')
        json_str = json_file.read()
        deck_file = json.loads(json_str)
        deck_cards = deck_file['mainBoard']
        deck_cards_list = []
        deck_guild = ""
        for card in deck_cards:
            if card['name'] not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                for i in range(0, card['count']):
                    deck_cards_list.append(card['name'])
                card_score = main_set_print_counts[card['name']]*card['count']
                deck_size += card['count']
                deck_score += card_score
            else:
                deck_guild = deck_guild + lands_to_color_ref[card['name']]
                # Take note of the lands' color ratio, and use that to get only real 2-color decks
                if land_count_a == 0:
                    land_count_a = card['count']
                else:
                    land_count_b = card['count']
        if land_count_a < land_count_b:
            land_ratio = land_count_b/land_count_a
        elif land_count_b < land_count_a:
            land_ratio = land_count_a/land_count_b
        else: land_ratio = 1
        # I detemined this to split the decks well
        if land_ratio <= 1.5:
            data_deck['cards'] = deck_cards_list
            data_deck['guild'] = deck_guild
            data_deck['name'] = deck_file['name']
            data_decks[deck_file['name']] = data_deck
            deck_score /= deck_size
            deck_scores[deck_file['name']] = deck_score
    # Go through Magic Arena and Duels core decks
    with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + 'MTG Arena and Duels 2-color starter decks.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        i = 0
        for file_row in csvreader:
            # Every other row contains counts, every other names
            if i % 2 == 0:
                deck = file_row[0]
                card_counts = file_row[1:]
                i += 1
            else:
                data_deck = dict()
                deck_size = 0
                land_count_a = 0
                land_count_b = 0
                deck_score = 0
                card_names = file_row[1:]
                deck_cards_list = []
                deck_guild = ""
                for j in range(0, len(card_names)):
                    if card_names[j] not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                        # If card name is empty (for some reason), ignore. Also ignore split cards.
                        if card_names[j] == '' or "///" in card_names[j] or "//" in card_names[j]:
                            hallo = 5
                        else:
                            for k in range(0, int(card_counts[j])):
                                deck_cards_list.append(card_names[j])
                            card_score = main_set_print_counts[card_names[j]]*int(card_counts[j])
                            deck_size += int(card_counts[j])
                            deck_score += card_score
                    else:
                        deck_guild = deck_guild + lands_to_color_ref[card_names[j]]
                        # Take note of the lands' color ratio, and use that to normalize scores
                        if land_count_a == 0:
                            land_count_a = int(card_counts[j])
                        else:
                            land_count_b = int(card_counts[j])
                # Find out the land ratio. If it's too high, ignore the deck
                if land_count_a < land_count_b:
                    land_ratio = land_count_b/land_count_a
                elif land_count_b < land_count_a:
                    land_ratio = land_count_a/land_count_b
                else: land_ratio = 1
                if land_ratio <= 1.5:
                    data_deck['cards'] = deck_cards_list
                    data_deck['guild'] = deck_guild
                    data_deck['name'] = deck
                    data_decks[deck] = data_deck
                    if deck_size != 0:
                        deck_score /= deck_size
                    deck_scores[deck] = deck_score
                i += 1
    # Find out which guild decks are closest to the average of their guild
    # Split the decks into guilds
    guilds_decks = dict()
    for deck in data_decks:
        guild = data_decks[deck]['guild']
        if guild in guilds_decks.keys():
            guilds_decks[guild][deck] = data_decks[deck]
        elif guild[::-1] in guilds_decks.keys():
            guilds_decks[guild[::-1]][deck] = data_decks[deck]
        else:
            guilds_decks[guild] = {}
            guilds_decks[guild][deck] = data_decks[deck]
    # For each guild, find the most average deck
    best_decks = dict()
    for guild in guilds_decks:
        best_guild_score = 0
        guild_cards_counts = dict()
        for deck_name in guilds_decks[guild]:
            deck = guilds_decks[guild][deck_name]
            for card in deck['cards']:
                if card not in guild_cards_counts:
                    guild_cards_counts[card] = 1
                else:
                    guild_cards_counts[card] += 1
        for deck_name in guilds_decks[guild]:
            deck = guilds_decks[guild][deck_name]
            deck_score = 0
            for card in deck['cards']:
                deck_score += guild_cards_counts[card]
            deck_score /= len(deck['cards'])
            guilds_decks[guild][deck_name]['score'] = deck_score
            if deck_score > best_guild_score:
                best_guild_score = deck_score
                best_deck = deck_name
        best_decks[best_deck] = best_guild_score
        #for card in data_decks[best_deck]['cards']:
        #    print(card)
    return deck_scores

def find_indeck_synergies():
    lands_to_color_ref = {"Plains":"W", "Island":"U", "Swamp":"B", "Mountain":"R", "Forest":"G"}
    data_decks = dict()
    card_print_counts = {}
    # Go through main set theme decks
    for deck_file_name in os.listdir(PATH_DECKS):
        data_deck = dict()
        json_file = open(PATH_DECKS + "/" + deck_file_name, encoding='utf-8')
        json_str = json_file.read()
        deck_file = json.loads(json_str)
        deck_cards = deck_file['mainBoard']
        deck_cards_list = []
        for card in deck_cards:
            if card['name'] not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                for i in range(0, card['count']):
                    deck_cards_list.append(card['name'])
                if card['name'] not in card_print_counts:
                    card_print_counts[card['name']] = 1
                else:
                    card_print_counts[card['name']] += 1
        data_deck['cards'] = deck_cards_list
        data_deck['name'] = deck_file['name']
        data_decks[deck_file['name']] = data_deck
    # Go through Magic Arena and Duels core decks
    with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + 'MTG Arena and Duels precon decks.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        i = 0
        for file_row in csvreader:
            # Every other row contains counts, every other names
            if i % 2 == 0:
                deck = file_row[0]
                card_counts = file_row[1:]
                i += 1
            else:
                data_deck = dict()
                card_names = file_row[1:]
                deck_cards_list = []
                for j in range(0, len(card_names)):
                    if card_names[j] not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                        # If card name is empty (for some reason), ignore. Also ignore split cards.
                        if card_names[j] == '' or "///" in card_names[j] or "//" in card_names[j]:
                            hallo = 5
                        else:
                            for k in range(0, int(card_counts[j])):
                                deck_cards_list.append(card_names[j])
                            if card_names[j] not in card_print_counts:
                                card_print_counts[card_names[j]] = 1
                            else:
                                card_print_counts[card_names[j]] += 1
                data_deck['cards'] = deck_cards_list
                data_deck['name'] = deck
                data_decks[deck] = data_deck
                i += 1
    card_print_counts = sorted(card_print_counts.items(), key=lambda x: x[1], reverse=True)
    for i in range(0, 350):
        print(card_print_counts[i][0])
    return card_print_counts

# Calculate the set that is closest to the Core
def find_most_core_set(main_set_print_counts, color):
    cardsets_points = {}
    for card_set in SETS_MAIN:
        set_card_points_total = 0
        added_cards = 0
        if card_set == "W16" or card_set == "W17":
            file_name = card_set + " decks cards.csv"
            with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + file_name) as csvfile:
                csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for row in csvreader:
                    card_name = row[0]
                    if card_name not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
            # Avoid division by 0
            if added_cards == 0:
                set_card_points_avg = 1
            else:
                set_card_points_avg = set_card_points_total/added_cards
            # Total points * avg points avoids favoring small or big sets.
            # Not sure this is the best approach though.
            #cardsets_points[card_set] = set_card_points_avg * set_card_points_total
            cardsets_points[card_set] = set_card_points_avg
        else:
            # Checklist for which cards have been added for this set. Some cards are in sets twice,
            # as foils for example.
            cards_added_in_this_set = set()
            set_info = dict_data_sets[card_set]
            set_cards = set_info['cards']
            for i in range(0, len(set_cards)):
                card_name = set_cards[i]['name']
                if card_name not in ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp'] and \
                        not card_name in cards_added_in_this_set:
                    if color=='all':
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
                        cards_added_in_this_set.add(card_name)
                    # Only add cards of given group
                    # Land
                    elif len(set_cards[i]['colors']) < 1 and 'Land' in set_cards[i]['types'] and color=='L':
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
                        cards_added_in_this_set.add(card_name)
                    # Colorless
                    elif len(set_cards[i]['colors']) < 1 and not 'Land' in set_cards[i]['types'] and color=='C':
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
                        cards_added_in_this_set.add(card_name)
                    # Multicolor
                    elif len(set_cards[i]['colors']) > 1 and color=='M':
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
                        cards_added_in_this_set.add(card_name)
                    # Specific color
                    elif len(set_cards[i]['colors']) == 1 and color in set_cards[i]['colors']:
                        set_card_points_total += main_set_print_counts[card_name]
                        added_cards += 1
                        cards_added_in_this_set.add(card_name)
            # Avoid division by 0
            if added_cards == 0:
                set_card_points_avg = 1
            else:
                set_card_points_avg = set_card_points_total/added_cards
            # Total points * avg points avoids favoring small or big sets. Not sure this is the best
            #cardsets_points[set_info['code']] = set_card_points_avg * set_card_points_total
            cardsets_points[set_info['code']] = set_card_points_avg
    cardsets_points = sorted(cardsets_points.items(), key=lambda x: x[1], reverse=True)
    return cardsets_points

# Calculate the F1-scores between core sets
def calculate_sets_F1_scores(dict_data_sets, core_set_codes):
    dict_core_sets = {}
    F1_coreset_score_matrix = np.ndarray(shape=(20, 20))
    for core_set_code in core_set_codes:
        dict_core_sets[core_set_code] = []
    # Compile core set cards into their own dictionary
    for core_set_code in core_set_codes:
        for card in dict_data_sets[core_set_code]['cards']:
            card_name = card['name']
            if card_name not in dict_core_sets[core_set_code] and card_name not in['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']:
                dict_core_sets[core_set_code].append(card['name'])
    # Compile cards in W16 and W17 decks to 'W16W17'
    dict_core_sets["W16W17"] = []
    with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + 'W16W17 cards.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in csvreader:
            dict_core_sets["W16W17"].append(row[0])
    for set_code_a in dict_core_sets:
        for set_code_b in dict_core_sets:
            overlap_count = 0
            for card_name in dict_core_sets[set_code_a]:
                if card_name in dict_core_sets[set_code_b]:
                    overlap_count += 1
            precision = overlap_count/len(dict_core_sets[set_code_a])
            recall = overlap_count/len(dict_core_sets[set_code_b])
            if precision == 0 or recall == 0:
                F1 = 0
            else:
                F1 = 2/(1/precision + 1/recall)
            F1_coreset_score_matrix[list(dict_core_sets.keys()).index(set_code_a),
                                    list(dict_core_sets.keys()).index(set_code_b)] = F1

# Starting with a list of cards' points, get the top card, remove it from the list,
# then add points for the other cards that are in the same sets. Then repa_seeat.
def top_cards_inset_regularization(points_dict, main_set_names, dict_datts, dict_data_cards):
    top_cards = []
    # Remove the basic lands
    points_dict.pop('Forest')
    points_dict.pop('Island')
    points_dict.pop('Mountain')
    points_dict.pop('Plains')
    points_dict.pop('Swamp')
    for k in range(0, 300):
        points_list = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)
        top_card = points_list[0][0]
        top_cards.append(top_card)
        points_dict.pop(top_card)
        # Checklist for which cards have been passed in this set. Some cards are in sets twice
        cards_passed_in_this_set = set()
        # Go through the sets the card has been printed in
        for set_name in dict_data_cards[top_card][0]['printings']:
            if set_name in main_set_names:
                # Go through the cards in the set
                for card_data in dict_data_sets[set_name]['cards']:
                    card_name = card_data['name']
                    # ONLY COUNT CARD ONCE PER SET
                    if not card_name in cards_passed_in_this_set:
                        # Increase those cards' points
                        if 'Basic' not in card_data['supertypes']:
                            if card_name in points_dict:
                                # Normalize added points by set size, so that bigger sets
                                # won't get more weight.
                                #points_additional = 300*(main_set_names.index(set_name)+1)/len(dict_data_sets[set_name]['cards'])
                                #points_additional = np.sqrt(main_set_names.index(set_name)+1)
                                #points_additional = np.sqrt((1+106)/2)
                                points_additional = 5
                                points_dict[card_name] = points_dict[card_name] + points_additional
                            cards_passed_in_this_set.add(card_name)
        print(top_card)
    hallo = 5


def get_print_counts(sets_pointsgiving):
    print_counts = dict()
    main_set_print_counts = dict()
    core_set_print_counts = dict()
    setwise_print_counts = dict()
    card_rarities = dict()
    cards_attributes = dict()
    rarities_key = {'common': 0, 'uncommon': 1, 'rare': 2, 'mythic': 3}
    for card_set in dict_data_sets:
        # Checklist for which cards have been added for this set. Some cards are in sets twice
        cards_added_in_this_set = set()
        set_info = dict_data_sets[card_set]
        set_cards = set_info['cards']

        # Get all cards from welcome decks W16 and W17, instead of just the cards printed specifically for them
        if card_set == "W16" or card_set == "W17":
            if "W16" in sets_pointsgiving and "W17" in sets_pointsgiving:
                file_name = card_set + " decks cards.csv"
                with open('C:\\Users\\joele\\OneDrive\\Games\\MTG\\Data' + '\\' + file_name) as csvfile:
                    csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                    for row in csvreader:
                        card_name = row[0]
                        if card_name in core_set_print_counts.keys():
                            core_set_print_counts[card_name] = core_set_print_counts[card_name] + core_set_points[
                                SETS_CORE.index(card_set)]
                        else:
                            core_set_print_counts[card_name] = core_set_points[SETS_CORE.index(card_set)]
                        if card_name in main_set_print_counts.keys():
                            main_set_print_counts[card_name] = main_set_print_counts[card_name] + main_set_points[
                                sets_pointsgiving.index(card_set)]
                        else:
                            main_set_print_counts[card_name] = main_set_points[sets_pointsgiving.index(card_set)]
        else:
            # Add the cards to the print counts
            for i in range(0, len(set_cards)):
                card_name = set_cards[i]['name']
                if card_name == "Gideon\'s Reproach":
                    hallo = 5
                # ONLY COUNT CARD ONCE PER SET
                if not card_name in cards_added_in_this_set:
                    if card_name in print_counts.keys():
                        print_counts[card_name] = print_counts[card_name] + 1
                    else:
                        print_counts[card_name] = 1
                    # Count the prints in core sets
                    if card_set in SETS_CORE:
                        if card_name in core_set_print_counts.keys():
                            # Points/counts
                            core_set_print_counts[card_name] = core_set_print_counts[card_name] + core_set_points[
                                SETS_CORE.index(card_set)]
                        else:
                            core_set_print_counts[card_name] = core_set_points[SETS_CORE.index(card_set)]
                    else:
                        if not card_name in core_set_print_counts.keys():
                            core_set_print_counts[card_name] = 0
                    if card_set in sets_pointsgiving:
                        rarity_index = rarities_key[set_cards[i]['rarity']]
                        if not card_name in cards_attributes:
                            cards_attributes[card_name] = {}
                            cards_attributes[card_name]['points'] = main_set_points[sets_pointsgiving.index(card_set)]
                            cards_attributes[card_name]['rarities'] = [rarity_index]
                            cards_attributes[card_name]['colors'] = set_cards[i]['colorIdentity']
                            cards_attributes[card_name]['types'] = set_cards[i]['types']
                            cards_attributes[card_name]['cmc'] = set_cards[i]['convertedManaCost']
                        else:
                            cards_attributes[card_name]['rarities'].append(rarity_index)
                            cards_attributes[card_name]['points'] += main_set_points[sets_pointsgiving.index(card_set)]
                        # Take notes of rarities
                        if not card_name in card_rarities.keys():
                            card_rarities[card_name] = list()
                        card_rarities[card_name].append(rarities_key[set_cards[i]['rarity']])
                        # Print counts
                        if card_name in main_set_print_counts.keys():
                            main_set_print_counts[card_name] = main_set_print_counts[card_name] + main_set_points[
                                sets_pointsgiving.index(card_set)]
                        else:
                            main_set_print_counts[card_name] = main_set_points[sets_pointsgiving.index(card_set)]
                    else:
                        if not card_name in main_set_print_counts.keys():
                            main_set_print_counts[card_name] = 0
                    cards_added_in_this_set.add(card_name)
    return main_set_print_counts, print_counts, core_set_print_counts, setwise_print_counts, card_rarities, cards_attributes



path_cards = ALL_CARDS_PATH
json_file = open(path_cards, encoding='utf-8')
json_str = json_file.read()
dict_data_cards = json.loads(json_str)['data']

dict_data_sets = {}
for card_set_file_name in os.listdir(PATH_ALL_SETS):
    json_file = open(PATH_ALL_SETS + "/" + card_set_file_name, encoding='utf-8')
    json_str = json_file.read()
    card_set = json.loads(json_str)['data']
    dict_data_sets[card_set['code']] = card_set

path_std = PATH_STANDARD_SETS
json_file = open(path_std, encoding='utf-8')
json_str = json_file.read()
dict_data_std = json.loads(json_str)

path_mod = PATH_MODERN_SETS
json_file = open(path_mod, encoding='utf-8')
json_str = json_file.read()
dict_data_mod = json.loads(json_str)

# Note: W16 and W17 sets included, Alpha not included since Beta is just a fixed version of it
SETS_MAIN = ["LEB", "2ED", "ARN", "ATQ", "3ED", "LEG", "DRK", "FEM", "4ED", "ICE", "HML", "ALL", "MIR", "VIS", "5ED", "WTH", "TMP", "STH", "EXO", "USG", "ULG", "6ED", "UDS", "MMQ", "NEM", "PCY", "INV", "PLS", "7ED", "APC", "ODY", "TOR", "JUD", "ONS", "LGN", "SCG", "8ED", "MRD", "DST", "5DN", "CHK", "BOK", "SOK", "9ED", "RAV", "GPT", "DIS", "CSP", "TSP", "PLC", "FUT", "10E", "LRW", "MOR", "SHM", "EVE", "ALA", "CON", "ARB", "M10", "ZEN", "WWK", "ROE", "M11", "SOM", "MBS", "NPH", "M12", "ISD", "DKA", "AVR", "M13", "RTR", "GTC", "DGM", "M14", "THS", "BNG", "JOU", "M15", "KTK", "FRF", "DTK", "ORI", "BFZ", "OGW", "W16", "SOI", "EMN", "KLD", "AER", "W17", "AKH", "HOU", "XLN", "RIX", "DOM", "M19", "GRN", "RNA", "WAR", "M20", "ELD", "THB", "IKO", "M21", "ZNR", "KHM", "STX", "AFR","MID","VOW","NEO"]
# Reprint sets LEB-M10 + W16/17 don't give points to cards
sets_pointsgiving = ["LEB", "ARN", "ATQ", "LEG", "DRK", "FEM", "ICE", "HML", "ALL", "MIR", "VIS", "WTH", "TMP", "STH", "EXO", "USG", "ULG", "UDS", "MMQ", "NEM", "PCY", "INV", "PLS", "APC", "ODY", "TOR", "JUD", "ONS", "LGN", "SCG", "MRD", "DST", "5DN", "CHK", "BOK", "SOK", "RAV", "GPT", "DIS", "CSP", "TSP", "PLC", "FUT", "LRW", "MOR", "SHM", "EVE", "ALA", "CON", "ARB", "M10", "ZEN", "WWK", "ROE", "M11", "SOM", "MBS", "NPH", "M12", "ISD", "DKA", "AVR", "M13", "RTR", "GTC", "DGM", "M14", "THS", "BNG", "JOU", "M15", "KTK", "FRF", "DTK", "ORI", "BFZ", "OGW", "SOI", "EMN", "KLD", "AER", "AKH", "HOU", "XLN", "RIX", "DOM", "M19", "GRN", "RNA", "WAR", "M20", "ELD", "THB", "IKO", "M21", "ZNR", "KHM", "STX", "AFR","MID","VOW","NEO"]
sets_pointsgiving = ['10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'W17', 'M15', 'W16', 'M19', 'M20']
top_sets = ['10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'W17', 'M15', 'W16', 'M19', 'M20']

# One point per print
main_set_points = list(np.ones(len(SETS_MAIN), dtype=int))
# Linearly increasing points
#main_set_points = list(range(1, len(main_sets)+1))
main_set_points_dict = dict(zip(SETS_MAIN, main_set_points))

SETS_CORE = ['LEB', '2ED', '3ED', '4ED', '5ED', '6ED', '7ED', '8ED', '9ED', '10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'ORI', 'BFZ', 'OGW', 'W16', "SOI", "KLD", "AER", "W17", "AKH", 'M19', 'M20', 'M21']

#core_sets = ['ALA','CON','ARB','ZEN', 'WWK', 'ROE', 'SOM', 'MBS', 'NPH', 'ISD', 'DKA', 'AVR', 'RTR', 'GTC', 'DGM','THS','BNG','JOU']
#core_sets = ['8ED', '9ED', '10E', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'ORI']
#core_set_points = list(range(1, 100))
#core_set_points = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 18, 18, 18, 19, 19, 19, 19, 20, 21, 22]
core_set_points = list(np.ones(len(SETS_CORE), dtype=int))
deck_names = []

main_set_print_counts, print_counts, core_set_print_counts, setwise_print_counts, card_rarities,\
    cards_attributes = get_print_counts(sets_pointsgiving)

cardsets_points = find_most_core_set(main_set_print_counts, color='all')


# Get the average rarities of cards
#for card_name in cards_attributes:
#    card_rarity = avg_rarity(cards_attributes[card_name]['rarities'])
#    cards_attributes[card_name]['avg_rarity'] = card_rarity

# Get the avg points of the cards by type, rarity and cmc
#for i in range(0, 100):
#    # Normalise iteratively the cards' points by card type and rarity
#    types_avgpoints, rarity_avgpoints, total_avgpoints = cards_pointsavgs_by_type_rarity_cmc(cards_attributes)
#    for card_name in cards_attributes:
#        card_rarity = cards_attributes[card_name]['rarity']
#        card_points = cards_attributes[card_name]['points'] - rarity_avgpoints[card_rarity] + total_avgpoints[card_rarity]

# lists
results = sorted(print_counts.items(), key=lambda x: x[1], reverse=True)
main_set_results = sorted(main_set_print_counts.items(), key=lambda x: x[1], reverse=True)
core_set_results = sorted(core_set_print_counts.items(), key=lambda x: x[1], reverse=True)
setwise_results = sorted(setwise_print_counts.items(), key=lambda x: x[0], reverse=False)
rarity_results = sorted(card_rarities.items(), key=lambda x: x[0], reverse=False)

for i in range(len(main_set_results)):
    if main_set_results[i][1] >= 2:
        print(main_set_results[i][0] + ";" + str(main_set_results[i][1]))

print("--------------------------------------------------------------------------")

for i in range(len(core_set_results)):
    if core_set_results[i][1] >= 2:
        print(core_set_results[i][0] + ";" + str(core_set_results[i][1]))

# Write results to file
prints_file = open("prints_file.txt", "w")
for card_name in cards_attributes:
    # Write results to a file
    if (cards_attributes[card_name]['points'] >= 107):
        print(card_name + ";" + str(cards_attributes[card_name]['points']) + ";" + str(cards_attributes[card_name]['colors']) + ";" + str(cards_attributes[card_name]['types']) + ";" + str(cards_attributes[card_name]['avg_rarity']))
        #print(results[i][0] + ";" + str(results[i][1]))
        prints_file.write(card_name + ";" + str(cards_attributes[card_name]['points']) + ";" + str(cards_attributes[card_name]['colors']) + ";" + str(cards_attributes[card_name]['types']) + ";" + str(cards_attributes[card_name]['avg_rarity']) + "\n")
prints_file.close()
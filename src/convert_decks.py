# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 21:25:53 2021

@author: Robert
"""
import pandas as pd
from pprint import pprint
import yaml

# Setup starting card property ordering for dataframe
prop_order=['name','deck','cost_treasure','cost_debt','cost_potion',
            'setup','isAction','isTreasure','isVictory','isAttack','isReaction',
            'isTrashing',]



def read_deck( path ):
    '''Read deck YAML data for a single deck and return it'''
    with open(path) as f:
        deck = yaml.load(f, Loader=yaml.FullLoader)
    return deck

def convertTrueFalse( value ):
    '''Convert Trues and Falses to 1s and 0s'''
    if isinstance(value,str):
        if value.lower()=='true':
            return 1
        elif value.lower()=='false':
            return 0
        else:
            return value
    elif isinstance(value,bool):
        return int(value)
    return value

def get_decks( deck_paths ):
    ''' Get all deck data from the provided decks and return a data frame for each type'''
    ### Build a data dictionary that contains all the data for all the types of 'cards'
    data = {}
    card_props = {}
    # Loop through decks
    for path in deck_paths:
        # Read the deck
        indv_deck = read_deck(path)
        deck_name = indv_deck.pop('name')
        # Loop through the types of 'cards' in the deck (cards, events, landmarks, ways, boons, projects)
        for card_type in indv_deck:
            data.setdefault(card_type,[])
            card_props.setdefault(card_type,set())
            # Loop through each 'card'
            for card in indv_deck[card_type]:
                # If there is a cost pull it out and split it into three separate entries (treasure, debt, potion)
                if 'cost' in card:
                    cost = card.pop('cost')
                    for cost_type in cost:
                        card['cost_{}'.format(cost_type)] = cost[cost_type]
                # Add deck name to 'card'
                card['deck'] = deck_name
                # Add 'card' to data structure
                data[card_type].append(card)
                # Add the properties available in this 'card' into the card_props structure
                for prop in card:
                    if prop not in card_props[card_type]:
                        card_props[card_type].add(prop)
    ### Taking the data from the last step build pandas data frames for each 'card' type
    data_out = {}
    # Loop through the 'card' types
    for card_type in data:
        # Take the property list and reorganize it based on prop_order
        prop_list = sorted(list(card_props[card_type]))
        for prop in prop_order[::-1]:
            if prop in prop_list:
                prop_list.remove(prop)
                prop_list.insert(0,prop)
        # Build an empty pandas dataframe with the columns pre-initialized
        data_out[card_type] = pd.DataFrame(columns=prop_list)
        # Loop through all the 'cards' of this 'card' type
        for card in data[card_type]:
            # For this 'card' add any non-initialized properties with their defaults
            for prop in prop_list:
                if prop not in card:
                    if prop.startswith('is'):
                        card[prop] = 0
                    elif prop.startswith('cost'):
                        card[prop] = 0
                    elif prop=='setup':
                        card[prop] = ''
                    else:
                        print(prop)
                        assert False
            # Add the 'card' to the data frame
            data_out[card_type] = data_out[card_type].append(pd.Series(card),ignore_index=True)
        # Convert all of the True/False values in the dataframe to 1/0
        data_out[card_type] = data_out[card_type].applymap( convertTrueFalse )
    return data_out

if __name__=='__main__':
    from glob import glob
    # Get all deck data for each 'card' type
    data = get_decks(glob('../_legacy/sets/*.yaml'))
    # Loop through 'card' types and save them to csv
    for card_type in data:
        file_out = '../decks/{}.csv'.format(card_type)
        print('> Writing file: {}'.format(file_out))
        data[card_type].to_csv(file_out)


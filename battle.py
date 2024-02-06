import random
import numpy as np

def roll_3d6():
    return (random.randint(1,6),random.randint(1,6),random.randint(1,6))

def check_difficulty_level(dice_value, qualifiy_value):
    '''
        1d100
        4: Critical
        3: Extreme Success
        2: Hard Success
        1: Regular Success
        0: Fail
        -1: Fumble 
    '''
    if 0 < dice_value < 6 & dice_value <= int(qualifiy_value):
        return 4
    elif dice_value <= int(qualifiy_value/5):
        return 3
    elif dice_value <= int(qualifiy_value/2):
        return 2
    elif dice_value <= int(qualifiy_value):
        return 1
    elif 95 < dice_value < 101:
        return -1
    else:
        return 0


def initialize_character(sloot):
    # Initializing Equipment
    equipment = sloot['equipment']
    
    c_item_lv = 5
    weapon_lv, weapon_g, weapon_e = equipment[0][1], equipment[0][2], c_item_lv * equipment[0][1] + equipment[0][2]
    chest_lv, chest_g, chest_e = equipment[1][1], equipment[1][2], c_item_lv * equipment[1][1] + equipment[1][2]
    head_lv, head_g, head_e = equipment[2][1], equipment[2][2], c_item_lv * equipment[2][1] + equipment[2][2]   
    waist_lv, waist_g, waist_e = equipment[3][1], equipment[3][2], c_item_lv * equipment[3][1] + equipment[3][2]   
    foot_lv, foot_g, foot_e = equipment[4][1], equipment[4][2], c_item_lv * equipment[4][1] + equipment[4][2]
    hand_lv, hand_g, hand_e = equipment[5][1], equipment[5][2], c_item_lv * equipment[5][1] + equipment[5][2]   
    neck_g, neck_e = equipment[6][2], c_item_lv * 3 + equipment[6][2]   
    ring_lv, ring_g, ring_e = equipment[7][1], equipment[7][2], c_item_lv * equipment[7][1] + equipment[7][2]  

    great_items = 0
    for item in equipment:
        if item[2] >18:
            great_items +=1
            
    STR = weapon_e + np.sum(roll_3d6())*3 #(8,99)
    CON = int(np.average([chest_e,head_e,waist_e]) + np.sum(roll_3d6())*3) #(8,99)
    DEX = foot_e + np.sum(roll_3d6())*3 #(8,99)
    INT = head_e + np.sum(roll_3d6())*3 #(8,99)
    APP = great_items * 10 + np.sum(roll_3d6()) #(3,98)
    LUK = neck_g + np.sum(roll_3d6()) + great_items #(3,46)
    SIZ = chest_e + np.sum(roll_3d6())*3 #(8,99)
    HP = int((CON + SIZ) * sum(roll_3d6())/10) #(28, 356)

    # POW
    # EDU
    
    # Initializing Character
    character = {
        'STR': STR,
        'CON': CON,
        'DEX': DEX,
        'INT': INT,
        'APP': APP,
        'LUK': LUK,
        'SIZ': SIZ,
        'HP': HP,
        'ATK_LV': [weapon_lv,weapon_g],
        'ATK':str(f"1~{2+weapon_g}"),
    }
        
    
    return character


def simulate_battle(player_sloot, enemy_sloot):
    player = initialize_character(player_sloot)
    enemy = initialize_character(enemy_sloot)

    while player['HP'] > 0 and enemy['HP'] > 0:
        # Determine initiative based on DEX
        if player['DEX'] >= enemy['DEX']:
            attackers = [(player, enemy), (enemy, player)]
        else:
            attackers = [(enemy, player), (player, enemy)]

        for current_attacker, current_defender in attackers:
            # Perform attack roll for the attacker
            attack_roll = random.randint(1, 101)
            attack_level = check_difficulty_level(attack_roll, current_attacker['STR'])

            # Perform defense roll for the defender
            defense_roll = random.randint(1, 101)
            defense_level = check_difficulty_level(defense_roll, current_defender['DEX'])

            # Determine outcome of the attack
            if attack_level > defense_level:
                # Calculate damage based on attack level and attacker's ATK_LV, DMG = 1D[weapon level] + [weapon greatness]/10
                base_damage = random.randint(1, current_attacker['ATK_LV'][0])
                damage = base_damage + round(current_attacker['ATK_LV'][1] / 10)
                if attack_level in [3, 4]:  # Extreme Success or Critical
                    damage += current_attacker['ATK_LV'][0] + round(current_attacker['ATK_LV'][1] / 10) * 2

                # Apply damage to the defender
                current_defender['HP'] -= damage
                if current_defender['HP'] <= 0:
                    break

    # Determine and return the battle result
    if player['HP'] > 0 and enemy['HP'] <= 0:
        return 'win'
    elif player['HP'] <= 0 and enemy['HP'] > 0:
        return 'lose'
    else:
        return 'draw'

def estimate_win_chance(player_sloot, enemy_sloot, num_simulations=160): 
    player_wins = 0

    for i in range(num_simulations):
        if simulate_battle(player_sloot,enemy_sloot) == 'win':
            player_wins +=1

    return int(player_wins / num_simulations * 100)
import random

def simulate_battle(player_sloot, enemy_sloot):
    player_hp = player_sloot['HP']
    enemy_hp = enemy_sloot['HP']
    player_critical_chance = int(player_sloot['equipment'][-1][-1]) / 100 
    player_critical_multiplier = player_sloot['equipment'][-1][1]
    enemy_critical_chance = int(enemy_sloot['equipment'][-1][-1]) / 100 
    enemy_critical_multiplier = enemy_sloot['equipment'][-1][1]
    
    while player_hp > 0 and enemy_hp > 0:
        # Player's turn 
        if random.random() < player_critical_chance:  
            enemy_hp -= player_sloot['Attack'] * player_critical_multiplier
        else:
            enemy_hp -= player_sloot['Attack']
        
        if enemy_hp <= 0:
            return 'win'
        
        # Enemy's turn 
        if random.random() < enemy_critical_chance:
            player_hp -= enemy_sloot['Attack'] * enemy_critical_multiplier
        else:
            player_hp -= enemy_sloot['Attack']
        
        if player_hp <= 0:
            return 'lost'
    
    return 'draw' 

def estimate_win_chance(player_sloot, enemy_sloot, num_simulations=160): 
    player_wins = 0

    for _ in range(num_simulations):
        if simulate_battle(player_sloot,enemy_sloot) == 'win':
            player_wins +=1

    return (player_wins / num_simulations) * 100 

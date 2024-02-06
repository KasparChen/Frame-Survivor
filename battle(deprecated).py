import random

def initialize_character(sloot):
    """
    equipment has 3 attributes:
         Level: like the position of your job, repersetin the form and base performance (lower and upper limits);
         Greatness: like the final kpi, repersetin the additional performance;
         Enengy: the summary value that works on battel, composed by (constant * level + greatness) , like your final salary.
    RETURNS:
        character attributes, dict
    """
    
    # Initializing Equipment
    equipment = sloot['equipment']
    
    c_item_lv = 10
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
            
    # Initializing Character
    character = {
        # HP = 100*avg(身具|Lv) + sum(身具|灵力)*5 = (100,500)+(0,300) = (100,800)
        'HP': int(100 * (chest_lv + head_lv + waist_lv)/3 + 5 * (chest_g + head_g + waist_g))*10,
        
        # DEF 减伤 = sum(身具|灵力)/(sum(身具|灵力)+315) = (0.03,0.4), * random(DEF_RE/2,DEF_RE) * 
        'DEF_RE%': round((chest_e + head_e + waist_e)/(chest_e + head_e + waist_e + 315), 2),

        # ATK = 10 + 武器能量 + 手具能量/2 = 10 + (10,70) + (5,35) = (25,125)
        'ATK': int(10 +  weapon_e + hand_e/2),

        # Slip-off rate = 0.4 - 手具|等级 * 0.07 (0.05,0.33)
        'SLP%': round(0.4 - hand_lv * 0.07, 2),
        
        # Critical rate = 武器|等级 + (戒指|能量*手具|等级)/10 (7,40)
        'CTR%': round(5 + weapon_lv + (ring_e * hand_lv)/10, 2),
        
        # Final damage = 武器|等级 * 满灵数量 + 戒指|能量/5 = (2,54)
        'FIN': int(weapon_lv * great_items + ring_e / 5),
        
        # AGI 敏捷 = 10 + 足具|能量 = (20, 80)
        'AGI': int(10 + foot_e),

        # INT 智力 = 10 + 项链|灵力 * 2  + 头具|能量 / 2 = (15, 75)
        'INT': int(10 + neck_g * 2 + head_e/2),

        # LUK 运气 = 戒指|等级 * 满灵数量 + 项链|灵力 (0,80)
        'LUK': int(ring_lv * great_items  + neck_g + ring_g),
    }
    
    return character

def calculate_damage(atk, atk_status_multipler,ctr_multipler, opponent_def_reduction, final_damage):
    # DMG 伤害{武器、首饰} = 攻击力 * 状态系数(脱手0.4~0.6/正常0.9~1.1) * 暴击系数(非暴击1/暴击1.5~2) * 对方减伤系数 + 最终伤害
    DMG = int(atk * atk_status_multipler * opponent_def_reduction * ctr_multipler + final_damage)
    return DMG

def simulate_battle(player_sloot, enemy_sloot):
    
    #Initialze character
    player = initialize_character(player_sloot)
    enemy = initialize_character(enemy_sloot)
#     print(f"===== Battle Started =====\n > Player: [{player['ATK']}] ATK, [{player['HP']}] HP,  \n > Enemy: [{enemy['ATK']}] ATK, [{enemy['HP']}] HP \n")

    rounds = 1
    while player['HP'] > 0 and enemy['HP'] > 0:
#         print(f"\n+++++ Round {rounds} +++++")
        # ===== Player's turn =====
         # 脱手判定
        if random.random() < player['SLP%']:
            player_atk_status_multipler = random.uniform(0.4,0.6)
        else:
            player_atk_status_multipler = random.uniform(0.9,1.1)
        
        # 暴击判定
        if random.random() < player['CTR%']:
            player_ctr_multipler = random.uniform(1.5,2.0)
        else:
            player_ctr_multipler = 1
        
        # 摇减伤系数
        enemy_def_reduction = random.uniform(enemy['DEF_RE%']/2,enemy['DEF_RE%'])
        
        player_damage = calculate_damage(player['ATK'], 
                                         player_atk_status_multipler, 
                                         player_ctr_multipler,
                                         enemy_def_reduction, 
                                         player['FIN'])
        
        enemy['HP'] -= player_damage
#         print(f"player deal {player_damage} DMG, enemy have {enemy['HP']} HP left.")
        
        if enemy['HP'] <= 0:
            return 'Win'
    
        # ===== Enemy's turn =====
         # 脱手判定
        if random.random() < enemy['SLP%']:
            enemy_atk_status_multipler = random.uniform(0.4,0.6)
        else:
            enemy_atk_status_multipler = random.uniform(0.9,1.1)
        
        # 暴击判定
        if random.random() < enemy['CTR%']:
            enemy_ctr_multipler = random.uniform(1.5,2.0)
        else:
            enemy_ctr_multipler = 1
        
        # 摇减伤系数
        player_def_reduction = random.uniform(player['DEF_RE%']/2,player['DEF_RE%'])
        
        enemy_damage = calculate_damage(enemy['ATK'], 
                                        enemy_atk_status_multipler,
                                        enemy_ctr_multipler,
                                        player_def_reduction, 
                                        enemy['FIN'])
        
        player['HP'] -= enemy_damage
#         print(f"enemy deal {enemy_damage} DMG, player have {player['HP']} HP left.")
        
        if player['HP'] <= 0:
            return 'Lost'
        rounds +=1

    return 'Draw'


def estimate_win_chance(player_sloot, enemy_sloot, num_simulations=160): 
    player_wins = 0

    for i in range(num_simulations):
        if simulate_battle(player_sloot,enemy_sloot) == 'win':
            player_wins +=1

    return int(player_wins / num_simulations * 100)

"""
def simulate_battle(player_sloot, enemy_sloot):
    player_hp = player_sloot['HP']
    enemy_hp = enemy_sloot['HP']
    player_critical_chance = player_sloot['equipment'][-1][-1] / 100 
    player_critical_multiplier = player_sloot['equipment'][-1][1]
    enemy_critical_chance = enemy_sloot['equipment'][-1][-1] / 100 
    enemy_critical_multiplier = enemy_sloot['equipment'][-1][1]
    
    while player_hp > 0 and enemy_hp > 0:
        # Player's turn 
        if random.random() < player_critical_chance:  
            enemy_hp -= player_sloot['Attack'] * player_critical_multiplier
        else:
            enemy_hp -= player_sloot['Attack']
        
        if enemy_hp <= 0:
            return 1
        
        # Enemy's turn 
        if random.random() < enemy_critical_chance:
            player_hp -= enemy_sloot['Attack'] * enemy_critical_multiplier
        else:
            player_hp -= enemy_sloot['Attack']
        
        if player_hp <= 0:
            return 0
    
    return 2

def estimate_win_chance(player_sloot, enemy_sloot, num_simulations=160): 
    player_wins = 0

    for _ in range(num_simulations):
        if simulate_battle(player_sloot,enemy_sloot) == 'win':
            player_wins +=1

    return int((player_wins / num_simulations) * 100)
"""


"""
def handle_event(player, event):
    if event['type'] == 'treasure':
        if player['INT'] > event['difficulty']:
            # Player succeeds
            pass  # Update game state
        else:
            # Player fails
            pass  # Update game state
    # Handle more event types
    # ...
"""
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import logging


def generate_profile_image(player_data, enemy_data, background_image_path):
    """
    data structure: {
    'address':'0x...',
    'equipment':[
    ['item', level(int), greatness(int)],
    ...],
    'Rating': (int)
    'character':{
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
    }
    """
    img = Image.open(background_image_path)
    logging.info(f"Darwing started")
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype('DePixelHalbfett.ttf', 28)
    text_font = ImageFont.truetype("DePixelKlein.ttf", 25)

    # Draw player's, top-left
    x_player, y_player = 38, 55  
    draw.text((356, 470), f"Rating: {player_data['Rating']}", font=title_font, fill=(0, 0, 0))
    draw.text((583, 476), f"/750 max", font=ImageFont.truetype('DePixelHalbfett.ttf', 20), fill=(0, 0, 0))
    
    for equip in player_data['equipment']:
        draw.text((x_player, y_player), f"Lv.{equip[1]} | ", font=text_font, fill=(0, 0, 0))
        draw.text((x_player + 80, y_player), equip[0], font=text_font, fill=(0, 0, 0))
        draw.text((x_player + 625, y_player), f"{{{equip[2]}}}", font=text_font, fill=(0, 0, 0))
        
        y_player += 50
        
    # Draw enemy's data, bottom-right
    x_enemy, y_enemy = 1410, 735 
    draw.text((786, 327), f"Rating: {enemy_data['Rating']}", font=title_font, fill=(0, 0, 0))
    draw.text((1013, 333), f"/750 max", font=ImageFont.truetype('DePixelHalbfett.ttf', 20), fill=(0, 0, 0))
    
    for equip in enemy_data['equipment']:
        draw.text((786, y_enemy), f"Lv.{equip[1]} | ", font=text_font, fill=(0, 0, 0))
        draw.text((786 + 80, y_enemy), equip[0], font=text_font, fill=(0, 0, 0))
        draw.text((x_enemy, y_enemy), f"{{{equip[2]}}}", font=text_font, fill=(0, 0, 0))
        
        y_enemy -= 50

    logging.info(f"Encoding image")

    #Save image to a BytesIO object
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Encode image to base64 string
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # Embed the base64 string as a data URL
    img_data_url = f"data:image/png;base64,{img_str}"
    
    return img_data_url


def generate_battle_image(player_data, enemy_data, win_chance, background_image_path):
    
    img = Image.open(background_image_path)
    draw = ImageDraw.Draw(img)
    att_font = ImageFont.truetype('PressStart2P.ttf', 55)
    hp_font = ImageFont.truetype('PressStart2P.ttf', 38)

    # Draw player's, top-left
    attack_p = player_data['character']['ATK']
    hp_p = player_data['character']['HP']
    
    apx = len(str(attack_p))-1 #player's attack multiple
    hppx = len(str(hp_p))-2 #player's hp multiple

    draw.text((543-26*apx , 605), f"{attack_p}", font=att_font, fill=(208, 2, 0))
    draw.text((310-20*hppx, 720), f"{hp_p}", font=hp_font, fill=(0, 0, 0))

    # Draw enemy's data, bottom-right
    attack_e = enemy_data['character']['ATK']
    hp_e = enemy_data['character']['HP']
    
    aex = len(str(attack_e))-1 
    hpex = len(str(hp_e))-2
    
    draw.text((910-24*aex, 605), f"{attack_e}", font=att_font, fill=(208, 2, 0))
    draw.text((1120-15*hpex, 720), f"{hp_e}", font=hp_font, fill=(0, 0, 0))
    
    # Draw win_rate
    wcx = len(str(win_chance))-1
   
    draw.text((723-20*wcx, 670), f"{win_chance}%", font=hp_font, fill=(0, 0, 0))
    
    #Save image to a BytesIO object
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    img_data_url = f"data:image/png;base64,{img_str}"
    
    return img_data_url


def generate_result_image(battle_result, win_chance, background_image_path):
    
    img = Image.open(background_image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('LevelUp.otf', 65)
    
    wcx = len(str(win_chance))-1 #win_chance word length multiple
    
    if battle_result == 'win':
        draw.text((596-26*wcx, 360), f"{win_chance}%", font=font, fill=(0, 0, 0))
        
    elif battle_result == 'lose':
        draw.text((180-26*wcx, 485), f"{win_chance}%", font=font, fill=(255, 255, 255))
        
    #Save image to a BytesIO object
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    img_data_url = f"data:image/png;base64,{img_str}"
    
    return img_data_url
    

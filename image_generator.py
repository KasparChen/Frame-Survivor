from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

def generate_profile_image(player_data, enemy_data, background_image_path):
    """
    data structure: {
    'address':'0x...',
    'equipment':[
    ['item', level(int), greatness(int)],
    ...],
    'Attack': (float)
    'HP': (int)
    'Rating': (int)
    }
    """
    img = Image.open(background_image_path)
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
    draw.text((786, 327), f"Rating: {player_data['Rating']}", font=title_font, fill=(0, 0, 0))
    draw.text((1013, 333), f"/750 max", font=ImageFont.truetype('DePixelHalbfett.ttf', 20), fill=(0, 0, 0))
    
    for equip in enemy_data['equipment']:
        draw.text((786, y_enemy), f"Lv.{equip[1]} | ", font=text_font, fill=(0, 0, 0))
        draw.text((786 + 80, y_enemy), equip[0], font=text_font, fill=(0, 0, 0))
        draw.text((x_enemy, y_enemy), f"{{{equip[2]}}}", font=text_font, fill=(0, 0, 0))
        
        y_enemy -= 50
    
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
    font = ImageFont.truetype('PressStart2P.ttf', 28)

    # Draw player's, top-left
    x_player, y_player = 38, 55  
    draw.text((x_player, y_player), f"{player_data['Attack']}", font=font, fill=(208, 2, 0))
    draw.text((x_player, y_player), f"{player_data['HP']}", font=font, fill=(0, 0, 0))

    # Draw enemy's data, bottom-right
    x_enemy, y_enemy = 1410, 735 
    draw.text((x_enemy, y_enemy), f"{enemy_data['Attack']}", font=font, fill=(208, 2, 0))
    draw.text((x_enemy, y_enemy), f"{enemy_data['HP']}", font=font, fill=(0, 0, 0))
    
    # Draw win_rate
    draw.text((200, 200), f"{win_chance}%", font=font, fill=(0, 0, 0))
    
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
    title_font = ImageFont.truetype('DePixelHalbfett.ttf', 28)
    text_font = ImageFont.truetype("DePixelKlein.ttf", 25)

    # Draw player's, top-left
    x_player, y_player = 38, 55  
    draw.text((x_player, y_player), f"{battle_result}", font=title_font, fill=(0, 0, 0))
    draw.text((x_player, y_player), f" {win_chance} ", font=text_font, fill=(0, 0, 0))
    
    #Save image to a BytesIO object
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    img_data_url = f"data:image/png;base64,{img_str}"
    
    return img_data_url
    

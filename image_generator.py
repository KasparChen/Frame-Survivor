from PIL import Image, ImageDraw, ImageFont
import boto3
import base64
from io import BytesIO

def generate_profile_image(player_data, enemy_data, background_image_path): #(s3_bucket_name)
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
    
    """ # Generate image and upload to S3
        
    file_name = f"profile_{player_data['address']}_{enemy_data['address']}.png"
    local_path = f"/tmp/{file_name}"  
    img.save(local_path)
    
    s3 = boto3.client('s3')
    s3.upload_file(local_path, s3_bucket_name, file_name, ExtraArgs={'ACL':'public-read'})
    s3_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{file_name}"
    """
    
    #Save image to a BytesIO object
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Encode image to base64 string
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # Embed the base64 string as a data URL
    img_data_url = f"data:image/png;base64,{img_str}"
    
    return img_data_url


def generate_battle_image(player_data, enemy_data, background_image_path):
    # Load the background image
    img = Image.open(background_image_path)
    draw = ImageDraw.Draw(img)
    
    # Load a font
    font = ImageFont.truetype("arial.ttf", 15)

    # Starting position for the text
    x, y = 50, 50

    # Draw player's and enemy's HP and Attack
    draw.text((x, y), f"Player - HP: {player_data['HP']}, Attack: {player_data['Attack']}", font=font, fill=(255, 255, 255))
    y += 20  # Adjust y coordinate for next line of text
    draw.text((x, y), f"Enemy - HP: {enemy_data['HP']}, Attack: {enemy_data['Attack']}", font=font, fill=(255, 255, 255))

    # Save or return the image
    img_path = f"static/images/battle_{player_data['address']}_{enemy_data['address']}.png"
    img.save(img_path)
    return img_path

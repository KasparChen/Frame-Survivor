from PIL import Image, ImageDraw, ImageFont
import boto3


def generate_profile_image(player_data, enemy_data, background_image_path, s3_bucket_name):
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
    font = ImageFont.truetype("./static/assest/pixel.TTF", 65)
    lv_font = ImageFont.truetype("./static/assest/pixel.TTF", 55)

    # Draw player's data, bottom-left
    x_player, y_player = 50, img.height - 700  
    draw.text((x_player, y_player), f"Player - Rating: {player_data['Rating']}", font=font, fill=(255, 255, 255))
    y_player += 90
    
    for equip in player_data['equipment']:
        draw.text((50, y_player), f"Lv.{equip[1]}", font=lv_font, fill=(255, 255, 255))
        draw.text((200, y_player), equip[0], font=font, fill=(255, 255, 255))
        draw.text((1400, y_player), f"{equip[2]}", font=font, fill=(255, 255, 255))
        
        y_player += 70

    # Draw enemy's data, top-right
    x_enemy, y_enemy = img.width - 800, 50 
    draw.text((x_enemy, y_enemy), f"Enemy - Rating: {enemy_data['Rating']}", font=font, fill=(255, 255, 255))
    y_enemy += 20
    """
    for equip in enemy_data['equipment']:
        draw.text((x_enemy, y_enemy), equip, font=font, fill=(255, 255, 255))
        y_enemy += 20
    """
    
    file_name = f"profile_{player_data['address']}_{enemy_data['address']}.png"
    local_path = f"/tmp/{file_name}"  
    img.save(local_path)
    
    s3 = boto3.client('s3')
    s3.upload_file(local_path, s3_bucket_name, file_name)
    s3_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{file_name}"

    return s3_url


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

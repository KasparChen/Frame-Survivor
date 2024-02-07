from flask import Flask, request, jsonify, Response
from datetime import datetime
from sloot_data import fetch_sloot_data, generate_random_addresses
from image_generator import generate_profile_image, generate_battle_image, generate_result_image
from battle import simulate_battle, estimate_win_chance
import re
import pytz
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from time import time


dictConfig({
        "version": 1,
        "disable_existing_loggers": False,  
        "formatters": {  
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",  # Console output 
                "level": "DEBUG",
                "formatter": "default",
            },
            "log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "default",   
                "filename": "/home/ec2-user/logs/fs-app.log",  
                "maxBytes": 20*1024*1024,   # 20M max
                "backupCount": 10,          # 10 files max
                "encoding": "utf8",        
            },

        },
        "root": {
            "level": "DEBUG",  # level in handler will cover this level
            "handlers": ["console", "log_file"],
        },
    }
)


app = Flask(__name__)

game_state = {}

profile_bg_path = "./static/asset/profile_bg.png"
battle_bg_path = "./static/asset/battle_bg.png"
win_bg_path = "./static/asset/win_bg.png"
loss_bg_path = "./static/asset/loss_bg.png"
draw_path = "./static/asset/draw.png"

""" 
# Example of Farcaster Signature Packet json
{
  "untrustedData": {
    "fid": 2,
    "url": "https://fcpolls.com/polls/1",
    "messageHash": "0xd2b1ddc6c88e865a33cb1a565e0058d757042974",
    "timestamp": 1706243218,
    "network": 1,
    "buttonIndex": 2,
    "inputText": "hello world", // "" if requested and no input, undefined if input not requested
    "castId": {
      "fid": 226,
      "hash": "0xa48dd46161d8e57725f5e26e34ec19c13ff7f3b9"
    }
  },
  "trustedData": {
    "messageBytes": "d2b1ddc6c88e865a33cb1a565e0058d757042974..."
  }
}

# Structure of game_state
{
    fid:{ 
    'starting_hash': '',
    'player_sloot': [],
    'enemies_sloot': [],
    'profile_pic_urls': [],
    'current_enemy_index': 0,
    'win_chance': 0,
    'explore_times': 0,
    'battles': 0,
    'wins':0,
    'draws':0,
    'last_enter_time':
    }
}
"""

@app.route('/start', methods=['POST'])
def start():
    start_time = time() #-----
    
    # Get the msg hash as player's starting seed
    signature_packet = request.json
    logging.info(f"{signature_packet}") #-----

    starting_hash = signature_packet.get('untrustedData')['messageHash']   
    logging.info(f"fetching hash: {starting_hash}") #-----

    
    fid = signature_packet.get('untrustedData')['fid']   
    logging.info(f"fetching fid: {fid}") #-----

    
    fetch_start_time = time() #-----
    # Fetch player sloot data and generate enemies (involve outer API)
    player_sloot = fetch_sloot_data(starting_hash)
    logging.info(f"player sloot: {player_sloot}") #-----
    
    fetch_start_time = time() #-----
    enemies_sloot = [fetch_sloot_data(address) for address in generate_random_addresses(5)]
    fetch_time = time() - fetch_start_time #-----
    logging.info(f"Time taken to fetch enemy data: {fetch_time:.2f} seconds") #-----
    logging.info(f"Game state updated: {enemies_sloot}") #-----

    
    # 0.1.2 try to pre-generate all battle data before
    win_chance = [estimate_win_chance(player_sloot, enemy) for enemy in enemies_sloot]
    logging.info(f"win chance {win_chance}") #-----
    logging.info(f"player sloot: {player_sloot}") #-----
    
    image_gen_start_time = time() #-----
    # Generate profile images and store URLs
    profile_pic_urls = [generate_profile_image(player_sloot, enemy, profile_bg_path) for enemy in enemies_sloot]
    image_gen_time = time() - image_gen_start_time #-----
    logging.info(f"Time taken to generate profile images: {image_gen_time:.2f} seconds") #-----
    
    # Initialize 'explore_times' 
    if fid not in game_state:
        game_state[fid] = {
            'explore_times': 0,
            'battles': 0,
            'wins':0,
            'draws':0,
        }
    game_state[fid]['explore_times'] += 1
    
    current_time = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%Y/%m/%d %H:%M:%S")

    # Storing game data
    game_state[fid].update({
        'starting_hash': starting_hash,
        'player_sloot': player_sloot,
        'enemies_sloot': enemies_sloot,
        'current_enemy_index': 0,
        'profile_pic_urls': profile_pic_urls,
        'last_enter_time': current_time,
        'win_chance': win_chance,
    })
    
    total_time = time() - start_time #-----
    logging.info(f"Total processing time for /start: {total_time:.2f} seconds") #-----
    logging.info(f"Game state updated: {game_state[fid]['player_sloot']}") #-----
    logging.info(f"Game state updated: {game_state[fid]['enemies_sloot']}") #-----
    logging.info(f"Game state updated: {game_state[fid]['win_chance']}") #-----
     
    # Generate Frame data
    response_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="fc:frame" content="vNext" />
        <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/explore" />
        <meta property="fc:frame:image" content="{profile_pic_urls[0]}" />
        <meta property="fc:frame:button:1" content="◀︎ Previous Enemy" />
        <meta property="fc:frame:button:2" content="◉ Battle" />
        <meta property="fc:frame:button:3" content="▶︎ Next Enemy" />
    </head>
    </html>"""
    
    #response = make_response(response_html, 200)
    logging.info("Response for /start is composed") 
    return Response(response_html, status=200, mimetype='text/html')


@app.route('/explore', methods=['POST'])
def explore():

    start_time = time() #-----
    signature_packet = request.json
    logging.info(f"{signature_packet}") #-----
    
    #request.get_json
    fid = signature_packet.get('untrustedData')['fid']
    logging.info(f"fetching fid: {fid}")
    
    button_index = signature_packet.get('untrustedData')['buttonIndex']
    
    logging.info(f"fetching button: {button_index}")
    
    logging.info(f"detemiation...")

    # if fid not in game_state or 'enemies_sloot' not in game_state[fid]:
    #     return Response("Game is not started. /nEntering from the Warcaster, SNEAKY! ", 400)

    logging.info(f"fetching game state...")

    current_enemy_index = game_state[fid]['current_enemy_index']
    enemies_sloot = game_state[fid]['enemies_sloot']
    player_sloot = game_state[fid]['player_sloot']
    win_chance = game_state[fid]['win_chance']
    
    logging.info(f"Received button_index: {button_index}")  #-----
    logging.info(f"Latest current_enemy_index: {current_enemy_index}") #-----
    logging.info(f"Corresponding enemy sloot: {enemies_sloot[current_enemy_index]}") #-----
    logging.info(f"Corresponding win chance: {win_chance[current_enemy_index]}") #-----
    
    # Compute current enemy index posi
    if button_index == 1:  # Previous Enemy
        if current_enemy_index > 0:
            current_enemy_index -= 1
        else: 
            return 
    elif button_index == 3:
        if current_enemy_index < len(enemies_sloot)-1:
            current_enemy_index += 1
            game_state[fid]['current_enemy_index'] = current_enemy_index
            
    # Generating enemy logic:
    # elif button_index == 3:  # Next Enemy
    #     if current_enemy_index < len(enemies_sloot) - 1:
    #         current_enemy_index += 1
    #     elif len(enemies_sloot) < 10:  # Generate new enemy if less than 10 enemies            
    #         new_enemy_sloot = fetch_sloot_data(generate_random_addresses(1)[0])
    #         enemies_sloot.append(new_enemy_sloot)
    #         new_profile_pic_url = generate_profile_image(player_sloot, new_enemy_sloot, profile_bg_path)
            
    #         game_state[fid]['profile_pic_urls'].append(new_profile_pic_url)
    #         current_enemy_index += 1
    elif button_index == 2:  # Battle
        enemy_sloot = enemies_sloot[current_enemy_index]
        win_chance = win_chance[current_enemy_index]
        battle_image = generate_battle_image(player_sloot, enemy_sloot, win_chance, battle_bg_path)
        enter_battle_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="fc:frame" content="vNext" />
            <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/battle" />
            <meta property="fc:frame:image" content="{battle_image}" />
            <meta property="fc:frame:button:1" content="Get the hell out of here!(WIP)" />
            <meta property="fc:frame:button:2" content="Fight like a MAN!" />
        </head>
        </html>
        """
        #battle_response = make_response(enter_battle_response, 200)
        
        compute_time = time() - start_time #-----
        logging.info(f"computation time: {compute_time:.2f} seconds") #-----
        logging.info("Response for /explore to enter battle is composed")

        return Response(enter_battle_response, status=200, mimetype='text/html')
    
    
    # Determine Button presence
    buttons_html = ""
    if current_enemy_index < len(enemies_sloot)-1:
        buttons_html = '<meta property="fc:frame:button:3" content="▶︎ Next Enemy" />'
        
    # Create final response
    response_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="fc:frame" content="vNext" />
        <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/explore" />
        <meta property="fc:frame:image" content="{game_state[fid]['profile_pic_urls'][current_enemy_index]}" />
        <meta property="fc:frame:button:1" content="◀︎ Previous Enemy" />
        <meta property="fc:frame:button:2" content="◉ Battle" />
        {buttons_html}
    </head>
    </html>
    """
    #response = make_response(response_html, 200)
    compute_time = time() - start_time #-----
    logging.info(f"computation time: {compute_time:.2f} seconds") #-----
    logging.info("Response for /explore to switch enemies is composed")
    return Response(response_html, status=200, mimetype='text/html')

@app.route('/battle', methods=['POST'])
def battle():
    
    start_time = time() #-----
    
    signature_packet = request.json
    logging.info(f"{signature_packet}") #-----

    fid = signature_packet.get('untrustedData')['fid']
    button_index = signature_packet.get('untrustedData')['buttonIndex']
    logging.info(f"{game_state}") #-----

    
    # if fid not in game_state or 'player_sloot' not in game_state[fid] or 'enemies_sloot' not in game_state[fid]:
    #     return Response("Game is not started or player/enemy data is missing. \nEntering from the Warcaster, SNEAKY! ", 400)

    current_enemy_index = game_state[fid]['current_enemy_index']
    player_sloot = game_state[fid]['player_sloot']
    enemy_sloot = game_state[fid]['enemies_sloot'][current_enemy_index]
    win_chance = game_state[fid]['win_chance'][current_enemy_index]
    
    fetching_time = time() - start_time #-----
    logging.info(f"Fetching time: {fetching_time:.2f} seconds") #-----
    logging.info(f"Input current_enemy_index: {current_enemy_index}") #-----

    
    if button_index == 2:  # Fight
        # Simulate the battle, get final result
        simulate_start_time = time() #-----
        battle_result = simulate_battle(player_sloot, enemy_sloot)
        game_state[fid]['battles'] += 1
        
        simulate_time = time() - simulate_start_time #-----
        logging.info(f"Time taken to simulate battle: {simulate_time:.2f} seconds") #-----
        logging.info(f"battle: {battle_result}") #-----


        if battle_result == 1:
            game_state[fid]['wins'] += 1
            button_text = "Doubt You Can Survive Again!"
            result_image = generate_result_image('win',win_chance,win_bg_path)
        elif battle_result == 0:
            button_text = "You'll Make it This Time"
            result_image = generate_result_image('loss',win_chance,loss_bg_path)
        else:
            button_text = "That..is..Unbelivable"
            result_image = draw_path
            game_state[fid]['draws'] += 1

        # Clear other data in the game_state
        game_state[fid].pop('player_sloot', None)
        game_state[fid].pop('enemies_sloot', None)
        game_state[fid].pop('profile_pic_urls', None)
        game_state[fid].pop('current_enemy_index', None)
        game_state[fid].pop('starting_hash', None)
        game_state[fid].pop('character', None)
        
        logging.info(f"data clear") #-----

        # Generate response HTML
        response_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="fc:frame" content="vNext" />
            <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/start" />
            <meta property="fc:frame:image" content="{result_image}" />
            <meta property="fc:frame:button:1" content="{button_text}" />
        </head>
        </html>
        """
        total_time = time() - start_time #-----
        logging.info(f"Total processing time for /battle: {total_time:.2f} seconds") #-----
        logging.info(f"{response_html}") #-----
        #response = make_response(response_html, 200)
        logging.info("Response for result is composed")
        return Response(response_html, status=200, mimetype='text/html')
        
    
    #elif button_index == 1:  # escape (wip)
    
    return

@app.route('/get_sloot', methods=['GET'])
def get_sloot():
    address = request.args.get('address')

    # Validation for Ethereum addresses
    if not address or not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return jsonify({'error': 'Invalid address provided'}), 400

    try:
        sloot_data = fetch_sloot_data(address)
        return jsonify(sloot_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
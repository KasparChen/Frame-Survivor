from flask import Flask, request, jsonify, make_response
from datetime import datetime
from sloot_data import fetch_sloot_data, generate_random_addresses
from image_generator import generate_profile_image, generate_battle_image, generate_result_image
from battle import simulate_battle, estimate_win_chance
import re
import pytz
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

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
    # Get the msg hash as player's starting seed
    signature_packet = request.json
    starting_hash = signature_packet.get('untrustedData')['messageHash']   
    fid = signature_packet.get('untrustedData')['fid']   
    
    # Fetch player sloot data and generate enemies (involve outer API)
    player_sloot = fetch_sloot_data(starting_hash)
    enemies_sloot = [fetch_sloot_data(address) for address in generate_random_addresses(1)]
    
    # Generate profile images and store URLs
    profile_pic_urls = [generate_profile_image(player_sloot, enemy, profile_bg_path) for enemy in enemies_sloot]
    
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
    })
    
    # Generate Frame data
    response_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="fc:frame" content="vNext" />
        <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/explore" />
        <meta property="fc:frame:image" content="{profile_pic_urls[0]}" />
        <meta property="fc:frame:button:2" content="◉ Battle" />
        <meta property="fc:frame:button:3" content="▶︎ Next Enemy" />
    </head>
    </html>"""
    
    return make_response(response_html, 200)


@app.route('/explore', methods=['POST'])
def explore():
    signature_packet = request.json
    fid = signature_packet.get('untrustedData')['fid']
    button_index = signature_packet.get('untrustedData')['buttonIndex']
    
    if fid not in game_state or 'enemies_sloot' not in game_state[fid]:
        return make_response("Game is not started. /nEntering from the Warcaster, SNEAKY! ", 400)

    current_enemy_index = game_state[fid]['current_enemy_index']
    enemies_sloot = game_state[fid]['enemies_sloot']
    player_sloot = game_state[fid]['player_sloot']
    
    if button_index == 1:  # Previous Enemy
        if current_enemy_index > 0:
            current_enemy_index -= 1
            
    elif button_index == 3:  # Next Enemy
        if current_enemy_index < len(enemies_sloot) - 1:
            current_enemy_index += 1
        elif len(enemies_sloot) < 10:  # Generate new enemy if less than 10 enemies
            new_enemy_sloot = fetch_sloot_data(generate_random_addresses(1)[0])
            enemies_sloot.append(new_enemy_sloot)
            new_profile_pic_url = generate_profile_image(player_sloot, new_enemy_sloot, profile_bg_path)
            game_state[fid]['profile_pic_urls'].append(new_profile_pic_url)
            current_enemy_index += 1
            
    elif button_index == 2:  # Battle
        enemy_sloot = enemies_sloot[current_enemy_index]
        game_state[fid]['win_chance'] = win_chance = estimate_win_chance(enemy_sloot, player_sloot)
        battle_image = generate_battle_image(player_sloot, enemy_sloot, win_chance, battle_bg_path)
        enter_battle_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="fc:frame" content="vNext" />
            <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/battle" />
            <meta property="fc:frame:image" content="{battle_image}" />
            <meta property="fc:frame:button:1" content="✈︎ Get the hell out of here!(WIP)" />
            <meta property="fc:frame:button:2" content="♔ Fight like a MAN!" />
        </head>
        </html>
        """
        return make_response(enter_battle_response, 200)

    game_state[fid]['current_enemy_index'] = current_enemy_index
    
    # Determine Button presence
    buttons_html = ""
    if current_enemy_index > 0:
        buttons_html += '<meta property="fc:frame:button:1" content="◀︎ Previous Enemy" />\n'
    buttons_html += '<meta property="fc:frame:button:2" content="◉ Battle" />\n'
    if current_enemy_index < 9:
        buttons_html += '<meta property="fc:frame:button:3" content="▶︎ Next Enemy" />\n'
        
    # Create final response
    response_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="fc:frame" content="vNext" />
        <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/explore" />
        <meta property="fc:frame:image" content="{game_state[fid]['profile_pic_urls'][current_enemy_index]}" />
        {buttons_html}
    </head>
    </html>
    """
    
    return make_response(response_html, 200)

@app.route('/battle', methods=['POST'])
def battle():
    signature_packet = request.json
    fid = signature_packet.get('untrustedData')['fid']
    button_index = signature_packet.get('untrustedData')['buttonIndex']
    
    if fid not in game_state or 'player_sloot' not in game_state[fid] or 'enemies_sloot' not in game_state[fid]:
        return make_response("Game is not started or player/enemy data is missing. /nEntering from the Warcaster, SNEAKY! ", 400)

    current_enemy_index = game_state[fid]['current_enemy_index']
    player_sloot = game_state[fid]['player_sloot']
    enemy_sloot = game_state[fid]['enemies_sloot'][current_enemy_index]
    win_chance = game_state[fid]['win_chance']
    
    if button_index == 2:  # Fight
        # Simulate the battle, get final result
        battle_result = simulate_battle(player_sloot, enemy_sloot)
        game_state[fid]['battles'] += 1

        if battle_result == 'win':
            game_state[fid]['wins'] += 1
            button_text = "Doubt You Can Survive Again!"
            result_image = generate_result_image('win',win_chance,win_bg_path)
        elif battle_result == 'lost':
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
        
        return make_response(response_html, 200)
    
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
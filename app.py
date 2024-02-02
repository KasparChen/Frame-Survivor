from flask import Flask, request, jsonify
from sloot_data import fetch_sloot_data, generate_random_addresses, level_mapping
from image_generator import generate_profile_image, generate_battle_image
import re
import os

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

game_state = {}

@app.route('/enter', methods=['POST'])
def enter():
    user_data = request.json
    user_address = user_data.get('untrustedData')['messageHash']      
    player_sloot = fetch_sloot_data(user_address)
    enemies_sloot = [fetch_sloot_data(address) for address in generate_random_addresses(10)]

    # Generate profile images and store URLs
    background_image_path = "static/images/bg.png"
    profile_pic_urls = [generate_profile_image(player_sloot, enemy, background_image_path) for enemy in enemies_sloot]
    
    # Storing player, enemies data, and profile pic URLs
    game_state[user_address] = {
        'player_sloot': player_sloot,
        'enemies_sloot': enemies_sloot,
        'current_enemy_index': 0,
        'profile_pic_urls': profile_pic_urls,
        'has_entered': True  # Flag to track if user has clicked "Enter"
    }
    
    # Return the first enemy's profile image URL
    first_enemy_image_url = profile_pic_urls[0]
    
    # If user clicked "Enter", show battle-related buttons
    if game_state[user_address]['has_entered']:
        buttons_meta = [
            {'property': 'fc:frame:button:2', 'content': 'Previous Enemy'},
            {'property': 'fc:frame:button:3', 'content': 'Battle'},
            {'property': 'fc:frame:button:4', 'content': 'Next Enemy'},
        ]
    else:
        buttons_meta = [{'property': 'fc:frame:button:1', 'content': 'Enter'}]
    
    return jsonify({
        'meta': [
            {'property': 'fc:frame:image', 'content': first_enemy_image_url}
        ] + buttons_meta
    })


# need to revise
"""
@app.route('/battle', methods=['POST'])
def battle():
    user_data = request.json
    user_address = user_data.get('address')
    
    # Retrieve the game state for the user
    if user_address in game_state:
        player_sloot = game_state[user_address]['player_sloot']
        current_enemy_index = game_state[user_address]['current_enemy_index']
        enemy_sloot = game_state[user_address]['enemies_sloot'][current_enemy_index]
        
        # Battle logic, compare player_sloot and enemy_sloot stats
        # ...
        
        # Update game state if needed (e.g., move to next enemy)
        # game_state[user_address]['current_enemy_index'] += 1
        
        # Return the result and update the frame  
        # ...
    
        # Generate battle image
        battle_image_url = generate_battle_image(player_sloot, enemy_sloot, 'battle_template_path')

        # Update the frame with the battle result
        return jsonify({
            'meta': [
                {'property': 'fc:frame:image', 'content': battle_image_url}
                # ... other meta tags for the battle result ...
                    ]
            else:
            return jsonify({'error': 'User state not found'}), 404
            })
"""

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


log_handler = RotatingFileHandler('logs/fs-app.log', maxBytes=100000, backupCount=1)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)
    
@app.route('/test', methods=['POST'])
def test():
    received_data = request.get_json() or request.data or request.form
    if isinstance(received_data, bytes):
        received_data = received_data.decode('utf-8')  # Decoding bytes to str
    app.logger.info('Received data: %s', received_data)
    return jsonify({'status': 'success', 'data': received_data})
from flask import Flask, request, jsonify, make_response
from sloot_data import fetch_sloot_data, generate_random_addresses, level_mapping
from image_generator import generate_profile_image, generate_battle_image
import re
import os
import time
import pytz
from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig


dictConfig({
        "version": 1,
        "disable_existing_loggers": False,  # 不覆盖默认配置
        "formatters": {  # 日志输出样式
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",  # 控制台输出
                "level": "DEBUG",
                "formatter": "default",
            },
            "log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",   # 日志输出样式对应formatters
                "filename": "/home/ec2-user/logs/fs-app.log",  # 指定log文件目录
                "maxBytes": 20*1024*1024,   # 文件最大20M
                "backupCount": 10,          # 最多10个文件
                "encoding": "utf8",         # 文件编码
            },

        },
        "root": {
            "level": "DEBUG",  # # handler中的level会覆盖掉这里的level
            "handlers": ["console", "log_file"],
        },
    }
)


app = Flask(__name__)

game_state = {}

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
			"castId": {
				fid: 226,
				hash: "0xa48dd46161d8e57725f5e26e34ec19c13ff7f3b9",
			}
		},
		"trustedData": {
			"messageBytes": "d2b1ddc6c88e865a33cb1a565e0058d757042974...",
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
    background_image_path = "./static/asset/profile_bg2.png"
    profile_pic_urls = [generate_profile_image(player_sloot, enemy, background_image_path) for enemy in enemies_sloot]
    
    # Initialize 'explore_times' 
    if fid not in game_state:
        game_state[fid] = {
            'explore_times': 0
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
        <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/explore" /> #需要后面做成一整个逻辑，通过["untrustedData"]["buttonIndex"]来识别功能
        <meta property="fc:frame:image" content="{profile_pic_urls[0]}" />
        <meta property="fc:frame:button:2" content="Battle" />
        <meta property="fc:frame:button:3" content="Next Enemy" />
    </head>
    </html>"""
    return make_response(response_html, 200)


app.route('/explore', methods=['POST'])
def explore():
    signature_packet = request.json
    fid = signature_packet.get('untrustedData')['fid']
    button_index = signature_packet.get('untrustedData')['buttonIndex']
    
    if fid not in game_state or 'enemies_sloot' not in game_state[fid]:
        return make_response("Game is not started.", 400)

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
            new_profile_pic_url = generate_profile_image(player_sloot, new_enemy_sloot, "./static/asset/profile_bg2.png")
            game_state[fid]['profile_pic_urls'].append(new_profile_pic_url)
            current_enemy_index += 1
    elif button_index == 2:  # Battle
        enemy_sloot = enemies_sloot[current_enemy_index]
        battle_image = generate_battle_image(player_sloot, enemy_sloot)
        enter_battle_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="fc:frame" content="vNext" />
            <meta property="fc:frame:post_url" content="http://vanishk.xyz/games/frame-survivor/battle" />
            <meta property="fc:frame:image" content="{battle_image}" />
            <meta property="fc:frame:button:1" content="Fight like a MAN!" />
        </head>
        </html>
        """
        return make_response(enter_battle_response, 200)

    game_state[fid]['current_enemy_index'] = current_enemy_index
    
    # Determine Button presence
    buttons_html = ""
    
    if current_enemy_index > 0:
        buttons_html += '<meta property="fc:frame:button:1" content="Previous Enemy" />\n'
    
    buttons_html += '<meta property="fc:frame:button:2" content="Battle" />\n'
    
    if current_enemy_index < 9:
        buttons_html += '<meta property="fc:frame:button:3" content="Next Enemy" />\n'
        
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

#app.route('/battle', methods=['POST'])
#def battle():
    



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
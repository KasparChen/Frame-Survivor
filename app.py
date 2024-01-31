from flask import Flask, request, jsonify
from utils import level_mapping, generate_random_addresses
from sloot_data import fetch_sloot_data
from image_generator import generate_profile_image, generate_battle_image
import os

app = Flask(__name__)

game_state = {}

# Flask routes (/enter, /battle, /previous_enemey, /next_enemey.)

#need to revise
@app.route('/enter', methods=['POST'])
 
def enter():
    user_data = request.json
    user_address = user_data.get('address')
    player_sloot = fetch_sloot_data(user_address)
    enemies_sloot = [fetch_sloot_data(generate_random_addresses()) for _ in range(10)]
    
    # Storing player and enemies data
    game_state[user_address] = {
        'player_sloot': player_sloot,
        'enemies_sloot': enemies_sloot,
        'current_enemy_index': 0  # Index of the current enemy
    }
    
    # Return the first enemy's details and update the frame
    first_enemy = enemies_sloot[0]
    return jsonify({
            'meta': [
                {'property': 'fc:frame:image', 'content': first_enemy['image_url']}
                # ... other meta tags for the first enemy ...
            ]
        })


# need to revise
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

    
@app.route('/generate_sloot', methods=['GET'])
def generate_sloot():
    addresses = generate_random_addresses(10)
    sloot_data = [fetch_sloot_data(address) for address in addresses]
    return jsonify(sloot_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Use PORT environment variable if it's set, else default to 8000
    app.run(host='0.0.0.0', port=port, debug=True)  # Run on all available IPs and the defined port

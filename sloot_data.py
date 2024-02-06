import requests
import base64
import json
from bs4 import BeautifulSoup
from eth_account import Account
from web3 import Web3
from battle import initialize_character

# Equipment Level Mapping
level_mapping = {
    # Weapons
    "Warhammer": 5, "Quarterstaff": 4, "Maul": 3, "Mace": 2, "Club": 1, 
    "Katana": 5, "Falchion": 4, "Scimitar": 3, "Long Sword": 2, "Short Sword": 1,
    "Ghost Wand": 5, "Grave Wand": 4, "Bone Wand": 3, "Wand": 2,
    "Grimoire": 5, "Chronicle": 4, "Tome": 3, "Book": 2,
    # Chest
    "Divine Robe": 5, "Silk Robe": 4, "Linen Robe": 3, "Robe": 2, "Shirt": 1,
    "Demon Husk": 5, "Dragonskin Armor": 4, "Studded Leather Armor": 3, "Hard Leather Armor": 2, "Leather Armor": 1,
    "Holy Chestplate": 5, "Ornate Chestplate": 4, "Plate Mail": 3, "Chain Mail": 2, "Ring Mail": 1,
    # Head
    "Ancient Helm": 5, "Ornate Helm": 4, "Great Helm": 3, "Full Helm": 2, "Helm": 1,
    "Demon Crown": 5, "Dragon's Crown": 4, "War Cap": 3, "Leather Cap": 2, "Cap": 1,
    "Crown": 5, "Divine Hood": 4, "Silk Hood": 3, "Linen Hood": 2, "Hood": 1,
    # Waist
    "Ornate Belt": 5, "War Belt": 4, "Plated Belt": 3, "Mesh Belt": 2, "Heavy Belt": 1,
    "Demonhide Belt": 5, "Dragonskin Belt": 4, "Studded Leather Belt": 3, "Hard Leather Belt": 2, "Leather Belt": 1,
    "Brightsilk Sash": 5, "Silk Sash": 4, "Wool Sash": 3, "Linen Sash": 2, "Sash": 1,
    # Foot
    "Holy Greaves": 5, "Ornate Greaves": 4, "Greaves": 3, "Chain Boots": 2, "Heavy Boots": 1,
    "Demonhide Boots": 5, "Dragonskin Boots": 4, "Studded Leather Boots": 3, "Hard Leather Boots": 2, "Leather Boots": 1,
    "Divine Slippers": 5, "Silk Slippers": 4, "Wool Shoes": 3, "Linen Shoes": 2, "Shoes": 1,
    # Hand
    "Holy Gauntlets": 5, "Ornate Gauntlets": 4, "Gauntlets": 3, "Chain Gloves": 2, "Heavy Gloves": 1,
    "Demon's Hands": 5, "Dragonskin Gloves": 4, "Studded Leather Gloves": 3, "Hard Leather Gloves": 2, "Leather Gloves": 1,
    "Divine Gloves": 5, "Silk Gloves": 4, "Wool Gloves": 3, "Linen Gloves": 2, "Gloves": 1,
    # Neck
    "Necklace": 3, "Amulet": 3, "Pendant": 3,
    # Ring
    "Gold Ring": 3, "Platinum Ring": 3, "Titanium Ring": 3, "Silver Ring": 2, "Bronze Ring": 1,
}

def generate_random_addresses(n):
    return [Account.create().address for _ in range(n)]

def calculate_greatness(wallet_address, key_prefix):
    if wallet_address.startswith('0x'):
        wallet_address = wallet_address[2:]
    address_bytes = bytes.fromhex(wallet_address)
    input_bytes = key_prefix.encode('utf-8') + address_bytes
    hashed = Web3.keccak(input_bytes)
    random_number = int.from_bytes(hashed, byteorder='big')
    greatness = random_number % 21
    return greatness

def get_level(item_name):
    for key in level_mapping:
        if key in item_name:
            return level_mapping[key]
    return 1  # Default level if not found

def fetch_sloot_data(address):
    response = requests.get(f"https://tanishq.xyz/api/getSyntheticLoot?address={address}")
    data = response.json()
    decoded_data = base64.b64decode(data['TokenURI'].split(',')[1]).decode('utf-8')
    json_data = json.loads(decoded_data)
    svg_data = base64.b64decode(json_data['image'].split(',')[1]).decode('utf-8')
    soup = BeautifulSoup(svg_data, 'html.parser')
    equipment_list = [text.get_text() for text in soup.find_all('text')]
    
    equipment_types = ["WEAPON", "CHEST", "HEAD", "WAIST", "FOOT", "HAND", "NECK", "RING"]
    full_equipment_list = []
    rating = 0
    for idx, equipment in enumerate(equipment_list):
        equipment_greatness = calculate_greatness(address, equipment_types[idx % len(equipment_types)])
        equipment_level = get_level(equipment)
        full_equipment_list.append([equipment, equipment_level, equipment_greatness])
        rating += equipment_level * equipment_greatness
    
    sloot = {'address': address, 'equipment': full_equipment_list, 'Rating':rating}
    
    sloot.update({'character':initialize_character(sloot)})
    
    return sloot

"""
Test script to verify LearnMovePhase handling works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from DataExtraction.create_input_0912_learningmove import create_input_vector
import json

# Load embeddings
with open("Embeddings/Pokemon/pokemon_embeddings.json", "r") as f:
    pokemon_embeddings_data = json.loads(f.read())
with open("Embeddings/moves/move_embeddings.json", "r") as f:
    move_embeddings_data = json.loads(f.read())

# Test Case 1: Pokemon with 2 moves learning a new move (should NOT force forgetting)
test_data_2_moves = {
    'phase': {'phaseName': 'LearnMovePhase'},
    'metaData': {'waveIndex': 1, 'isDoubleFight': False},
    'shopItems': [],
    'enemy': [{'dex_nr': 263, 'formIndex': 0, 'hp': 14, 'stats': [14, 5, 6, 6, 6, 8], 'id': 'enemy_1'}],
    'player': [
        {
            'dex_nr': 702, 'formIndex': 0, 'hp': 22, 
            'moveset': [
                {'id': 39},    # Move 1
                {'id': 609},   # Move 2
                # No move 3 and 4 - only knows 2 moves
            ],
            'stats': [22, 12, 11, 14, 13, 16],
            'visible': True,
            'id': 'player_1'
        }
    ]
}

# Test Case 2: Pokemon with 4 moves learning a new move (SHOULD force forgetting)
test_data_4_moves = {
    'phase': {'phaseName': 'LearnMovePhase'},
    'metaData': {'waveIndex': 1, 'isDoubleFight': False},
    'shopItems': [],
    'enemy': [{'dex_nr': 263, 'formIndex': 0, 'hp': 14, 'stats': [14, 5, 6, 6, 6, 8], 'id': 'enemy_1'}],
    'player': [
        {
            'dex_nr': 702, 'formIndex': 0, 'hp': 22,
            'moveset': [
                {'id': 39},    # Move 1
                {'id': 609},   # Move 2
                {'id': 33},    # Move 3
                {'id': 586},   # Move 4 - knows 4 moves
            ],
            'stats': [22, 12, 11, 14, 13, 16],
            'visible': True,
            'id': 'player_1'
        }
    ]
}

print("=" * 60)
print("Testing LearnMovePhase Logic")
print("=" * 60)

# Test 1
print("\n[TEST 1] Pokemon with 2 moves learning")
try:
    _, meta_data_1 = create_input_vector(test_data_2_moves, pokemon_embeddings_data, move_embeddings_data)
    print(f"✓ Phase: {meta_data_1['phaseName']}")
    print(f"✓ Learning Pokemon: {meta_data_1['learning_pokemon']}")
    print(f"✓ Current Move Count: {meta_data_1['current_moves_count']}")
    print(f"  → Expected: 2, Got: {meta_data_1['current_moves_count']}")
    if meta_data_1['current_moves_count'] == 2:
        print("  ✓ CORRECT: Should NOT force forgetting (< 4 moves)")
    else:
        print("  ✗ WRONG: Move count incorrect")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 2
print("\n[TEST 2] Pokemon with 4 moves learning")
try:
    _, meta_data_2 = create_input_vector(test_data_4_moves, pokemon_embeddings_data, move_embeddings_data)
    print(f"✓ Phase: {meta_data_2['phaseName']}")
    print(f"✓ Learning Pokemon: {meta_data_2['learning_pokemon']}")
    print(f"✓ Current Move Count: {meta_data_2['current_moves_count']}")
    print(f"  → Expected: 4, Got: {meta_data_2['current_moves_count']}")
    if meta_data_2['current_moves_count'] == 4:
        print("  ✓ CORRECT: Should force forgetting (== 4 moves)")
    else:
        print("  ✗ WRONG: Move count incorrect")
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

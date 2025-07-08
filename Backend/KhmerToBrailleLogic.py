import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from gcc_segmentation import GCCSegmentation
from spellchecker import SpellChecker
import re

app = Flask(__name__)
CORS(app)

# Global setup
spell = SpellChecker()
segmenter = GCCSegmentation()

# Load dictionaries once
with open('./dictionary/khmer_to_english_dictionary.json', 'r', encoding='utf-8') as f:
    khmer_to_english_dictionary = json.load(f)

with open('./dictionary/english_to_braille_dictionary.json', 'r', encoding='utf-8') as f:
    english_to_braille_dictionary = json.load(f)

COENG = '្'
RO = 'រ'
VOWEL_SIGNS = ['េ', 'ែ', 'ៃ', 'ើ']

def reorder_khmer_characters(word_list):
    """
    - This function reorders Khmer characters in a list of words based on specific rules:
    - If a word contains a vowel sign followed by the coeng and ro, it moves the vowel sign to the front.
    - If a word contains only the coeng and ro, it moves them to the front.
    - If a word contains only a vowel sign, it moves that vowel sign to the front.
    - Remaining characters are appended in their original order.
    """
    reordered_words = []
    for word in word_list:
        chars = list(word)
        processed_chars = []
        processed_indices = set()

        # Find vowel sign and coeng+ro
        vowel_sign_index = next((i for i in range(len(chars)) if chars[i] in VOWEL_SIGNS), None)
        coeng_ro_indices = next(((i, i+1) for i in range(len(chars) - 1)
                                 if chars[i] == COENG and chars[i+1] == RO), None)

        # Condition 2: vowel + coeng ro
        if vowel_sign_index is not None and coeng_ro_indices:
            processed_chars.append(chars[vowel_sign_index])
            processed_indices.add(vowel_sign_index)
            processed_chars += [chars[i] for i in coeng_ro_indices]
            processed_indices.update(coeng_ro_indices)

        # Condition 1: only coeng ro
        elif coeng_ro_indices:
            processed_chars += [chars[i] for i in coeng_ro_indices]
            processed_indices.update(coeng_ro_indices)

        # Condition 3: only vowel — move to front
        elif vowel_sign_index is not None:
            processed_chars.append(chars[vowel_sign_index])
            processed_indices.add(vowel_sign_index)

        # Add remaining unprocessed characters
        for i, char in enumerate(chars):
            if i not in processed_indices:
                processed_chars.append(char)

        reordered_words.append("".join(processed_chars))
    return reordered_words


def khmer_to_braille(khmer_sentence):
    """
    - This function translates a Khmer sentence into Braille.
    - It segments the sentence into Khmer character clusters, processes each token according to specific rules,
    - and converts the processed tokens into English text.
    - It handles special cases like numbers, uppercase English words, and characters with quotes.
    - Finally, it converts the English text into Braille using a predefined dictionary.
    """
    segments = segmenter.seg_gcc(khmer_sentence)
    khmer_text = []
    skip = 0
    
    for i in range(len(segments)):
        if skip:
            skip -= 1
            continue
        token = segments[i]

        # Case 0.5: Float split into two tokens like ['13', '.45']
        if (
            i + 1 < len(segments)
            and segments[i].isdigit()
            and segments[i + 1].startswith('.')
            and segments[i + 1][1:].isdigit()
        ):
            khmer_text.append(f"#{segments[i]}{segments[i + 1]}")
            skip = 1
            continue

        # Case: Number formatting
        if token.isnumeric() and token not in ['⑤', '🅐']:
            khmer_text.append(f"#{token}")
            continue

        # Case: All uppercase English word
        if token.isupper() and token in spell and len(token) >= 2:
            khmer_text.append(",,{}".format(token.lower()))
            continue
        
        if '"' in token:
            for ch in token:
                if ch == '"':
                    khmer_text.append('"')
                else:
                    khmer_text.append(ch)
            continue

        # Case: Word with some uppercase letters
        eng_word = ''.join(["," + c.lower() if c.isupper() else c for c in token])
        khmer_text.append(eng_word)
            

    khmer_text = reorder_khmer_characters(khmer_text)

    english_text = ''
    braille_text = ''
    combos = [
        ('ោ', 'ះ', 'ោះ'),
        ('ុ', 'ះ', 'ុះ'),
        ('េ', 'ះ', 'េះ'),
        ('ំ', 'ុ', 'ុំ'),
        ('ា', 'ំ', 'ាំ'),
        # ('Ǝ', "'", 'Ǝ|')
    ]
    print(khmer_text)
    quote_open = False
    for kcc in khmer_text:    
        chars = list(kcc)
        for a, b, combo in combos:
            if a in chars and b in chars:
                chars.remove(a)
                chars.remove(b)
                chars.append(combo)
        
        for c in chars:
            c = "v" if c == COENG else c
            english_text += khmer_to_english_dictionary.get(c, '8 gyhcs 0')
    print(english_text)
    for e in english_text:
        braille_text += english_to_braille_dictionary.get(e, '')
    return braille_text

@app.route('/translationKhmer', methods=['POST'])
def translate_khmer_to_braille():
    data = request.get_json()
    text = data.get('text', '')
    braille_result = khmer_to_braille(text)
    return jsonify({'braille': braille_result})

if __name__ == '__main__':
    app.run(debug=True)




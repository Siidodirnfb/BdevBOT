#!/usr/bin/env python3

import re
from rapidfuzz import fuzz

def extract_game_name(text):
    patterns = [
        r'Игра:\s*(.+?)(?:\n|$)',
        r'Game:\s*(.+?)(?:\n|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_lua_script(text):
    lua_patterns = [
        r'```lua\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
        r'loadstring\(game:HttpGet\("([^"]+)"\)\)\(\)',
        r'--.*?function.*?end',
    ]

    for pattern in lua_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            if 'HttpGet' in pattern and matches:
                return f"loadstring(game:HttpGet(\"{matches[0]}\"))()"
            return '\n'.join(matches)

    lines = text.split('\n')
    lua_lines = []

    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['local', 'function', 'end', 'if', 'then', 'else', 'for', 'while', 'repeat', 'until', 'loadstring', 'HttpGet']):
            lua_lines.append(line)

    return '\n'.join(lua_lines) if lua_lines else None

def fuzzy_match_game_name(requested_name, found_name):
    if not found_name:
        return False

    requested_clean = re.sub(r'[^\w\s]', '', requested_name.lower())
    found_clean = re.sub(r'[^\w\s]', '', found_name.lower())

    ratio = fuzz.ratio(requested_clean, found_clean)
    partial_ratio = fuzz.partial_ratio(requested_clean, found_clean)
    token_sort_ratio = fuzz.token_sort_ratio(requested_clean, found_clean)

    return max(ratio, partial_ratio, token_sort_ratio) > 70

def test_extract_game_name():
    test_cases = [
        ("Игра: Blade Ball\nSome other text", "Blade Ball"),
        ("Game: Phantom Forces\nMore text", "Phantom Forces"),
        ("Игра:Arsenal", "Arsenal"),
        ("No game name here", None),
    ]

    print("Testing extract_game_name:")
    for text, expected in test_cases:
        result = extract_game_name(text)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: '{text}' -> '{result}' (expected: '{expected}')")
    print()

def test_extract_lua_script():
    test_cases = [
        ("```lua\nlocal player = game.Players.LocalPlayer\nprint('Hello')\n```", "local player = game.Players.LocalPlayer\nprint('Hello')"),
        ("```\nfunction test()\nend\n```", "function test()\nend"),
        ("Игра: Mine a Brainrot\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/gumanba/Scripts/main/MineaBrainrot\"))()", "loadstring(game:HttpGet(\"https://raw.githubusercontent.com/gumanba/Scripts/main/MineaBrainrot\"))()"),
        ("Some text\nlocal x = 1\nif x then\nend", "local x = 1\nif x then\nend"),
        ("No code here", None),
    ]

    print("Testing extract_lua_script:")
    for text, expected in test_cases:
        result = extract_lua_script(text)
        status = "PASS" if (result == expected or (result and expected in result)) else "FAIL"
        print(f"{status}: Code extracted: {bool(result)} (expected: {bool(expected)})")
    print()

def test_fuzzy_match():
    test_cases = [
        ("Blade Ball", "Blade Ball", True),
        ("Blade Ball", "blAde Ball", True),
        ("Blade Ball", "BladeBall", True),
        ("Phantom Forces", "Phantom Force", True),
        ("Arsenal", "Arsenall", True),
        ("Blade Ball", "Phantom Forces", False),
    ]

    print("Testing fuzzy_match_game_name:")
    for requested, found, expected in test_cases:
        result = fuzzy_match_game_name(requested, found)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: '{requested}' vs '{found}' -> {result} (expected: {expected})")
    print()

if __name__ == "__main__":
    print("Testing bot functions...\n")
    test_extract_game_name()
    test_extract_lua_script()
    test_fuzzy_match()
    print("Tests completed!")
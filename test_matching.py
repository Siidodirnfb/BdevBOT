#!/usr/bin/env python3

import re
from rapidfuzz import fuzz

def fuzzy_match_game_name(requested_name, found_name):
    if not found_name:
        return False

    requested_clean = re.sub(r'[^\w\s]', '', requested_name.lower())
    found_clean = re.sub(r'[^\w\s]', '', found_name.lower())

    ratio = fuzz.ratio(requested_clean, found_clean)
    partial_ratio = fuzz.partial_ratio(requested_clean, found_clean)
    token_sort_ratio = fuzz.token_sort_ratio(requested_clean, found_clean)
    token_set_ratio = fuzz.token_set_ratio(requested_clean, found_clean)

    strict_match = (
        ratio > 70 and
        partial_ratio > 70 and
        token_sort_ratio > 70
    ) or token_sort_ratio > 80

    common_words = ['break', 'block', 'ball', 'battle', 'grounds', 'game', 'play']
    requested_words = set(requested_clean.split())
    found_words = set(found_clean.split())

    if (requested_words.intersection(common_words) and found_words.intersection(common_words) and
        token_sort_ratio < 85):
        significant_requested = requested_words - set(common_words)
        significant_found = found_words - set(common_words)

        if not significant_requested.intersection(significant_found) and token_sort_ratio < 70:
            return False

    return strict_match

def test_match(requested, found, expected):
    result = fuzzy_match_game_name(requested, found)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: '{requested}' vs '{found}' -> {result} (expected: {expected})")

    requested_clean = re.sub(r'[^\w\s]', '', requested.lower())
    found_clean = re.sub(r'[^\w\s]', '', found.lower())

    ratio = fuzz.ratio(requested_clean, found_clean)
    partial_ratio = fuzz.partial_ratio(requested_clean, found_clean)
    token_sort_ratio = fuzz.token_sort_ratio(requested_clean, found_clean)
    token_set_ratio = fuzz.token_set_ratio(requested_clean, found_clean)

    print(f"      Scores - ratio: {ratio:.1f}, partial: {partial_ratio:.1f}, token_sort: {token_sort_ratio:.1f}, token_set: {token_set_ratio:.1f}")
    return result == expected

if __name__ == "__main__":
    print("Testing fuzzy matching improvements...\n")

    test_cases = [
        ("Break In 2", "Break In 2", True),
        ("Break In 2", "Break a Lucky Block", False),
        ("Blade Ball", "Blade Ball", True),
        ("Blade Ball", "blAde Ball", True),
        ("Blade Ball", "Phantom Forces", False),
        ("Break In", "Break In 2", True),
        ("Lucky Block", "Break a Lucky Block", True),
        ("Block", "Break a Lucky Block", False),
    ]

    passed = 0
    total = len(test_cases)

    for requested, found, expected in test_cases:
        if test_match(requested, found, expected):
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! Fuzzy matching improved.")
    else:
        print("Some tests failed. Need more tuning.")
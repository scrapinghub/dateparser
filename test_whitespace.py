#!/usr/bin/env python3
"""Test script to check current whitespace behavior"""

from dateparser.languages import default_loader
from dateparser.conf import settings


def test_current_behavior():
    locale = default_loader.get_locale("fi")

    # Test 1: Single spaces
    input1 = "28 maalis klo 9:37"
    result1 = locale.translate(input1, settings=settings)
    print(f"Input1:    |{input1}|")
    print(f"Result1:   |{result1}|")
    print("Expected1: |28 march 9:37|")
    print(f"Match: {result1 == '28 march 9:37'}")
    print()

    # Test 2: Double spaces
    input2 = "28  maalis  klo  9:37"
    result2 = locale.translate(input2, settings=settings)
    print(f"Input2:    |{input2}|")
    print(f"Result2:   |{result2}|")
    print("Expected2: |28  march  9:37|")
    print(f"Match: {result2 == '28  march  9:37'}")
    print()

    # Test 3: Triple spaces
    input3 = "28   maalis   klo   9:37"
    result3 = locale.translate(input3, settings=settings)
    print(f"Input3:    |{input3}|")
    print(f"Result3:   |{result3}|")
    print("Expected3: |28   march   9:37|")
    print(f"Match: {result3 == '28   march   9:37'}")
    print()


if __name__ == "__main__":
    test_current_behavior()

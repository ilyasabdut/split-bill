#!/usr/bin/env python3
"""
Summary of backend unit tests created for 90%+ coverage.
"""

import re
from pathlib import Path


def count_tests_in_file(file_path):
    """Count test cases in a Python test file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Count test functions (def test_*)
    test_functions = len(re.findall(r'def test_\w+\(', content))

    # Count async test functions (async def test_*)
    async_test_functions = len(re.findall(r'async def test_\w+\(', content))

    # Count test classes (class Test\w+)
    test_classes = len(re.findall(r'class Test\w+\(', content))

    return {
        'test_functions': test_functions,
        'async_test_functions': async_test_functions,
        'total_tests': test_functions + async_test_functions,
        'test_classes': test_classes,
    }


def main():
    """Main function to count tests."""
    tests_dir = Path(__file__).parent

    # Count all test files
    test_files = list(tests_dir.rglob('test_*.py'))
    test_files.extend(list(tests_dir.rglob('**/test_*.py')))

    total_tests = 0
    total_async_tests = 0
    total_classes = 0
    total_files = 0

    print("Backend Unit Tests Summary")
    print("=" * 60)

    for test_file in sorted(test_files):
        relative_path = test_file.relative_to(tests_dir.parent)
        stats = count_tests_in_file(test_file)

        if stats['total_tests'] > 0:
            print(f"\n{relative_path}")
            print(f"  Test Functions: {stats['test_functions']}")
            print(f"  Async Test Functions: {stats['async_test_functions']}")
            print(f"  Test Classes: {stats['test_classes']}")
            print(f"  Total Tests: {stats['total_tests']}")

            total_tests += stats['total_tests']
            total_async_tests += stats['async_test_functions']
            total_classes += stats['test_classes']
            total_files += 1

    print("\n" + "=" * 60)
    print(f"Total Test Files: {total_files}")
    print(f"Total Test Classes: {total_classes}")
    print(f"Total Test Functions: {total_tests}")
    print(f"Total Async Test Functions: {total_async_tests}")
    print(f"Total Test Cases: {total_tests + total_async_tests}")
    print("=" * 60)


if __name__ == "__main__":
    main()

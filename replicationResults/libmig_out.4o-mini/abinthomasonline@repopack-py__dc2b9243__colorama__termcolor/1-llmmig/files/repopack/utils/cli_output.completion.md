### Explanation of Changes
To migrate the code from using the `colorama` library to the `termcolor` library, the following changes were made:

1. **Import Statements**: The import statements were updated to import `colored` from `termcolor` instead of `Fore` and `Style` from `colorama`.
2. **Color Formatting**: The color formatting was changed from using `Fore` and `Style` to using the `colored` function from `termcolor`. The `colored` function allows for both foreground and background colors to be specified in a single call.

### Modified Code
Here is the modified code after migrating to `termcolor`:

```python
from typing import Dict, List, Tuple
from termcolor import colored

def print_top_files(file_char_counts: Dict[str, int], top_files_length: int) -> None:
    """
    Print the top files by character count.

    Args:
        file_char_counts (Dict[str, int]): A dictionary of file paths and their character counts.
        top_files_length (int): The number of top files to display.
    """
    print(f"\n{colored('📈 Top ' + str(top_files_length) + ' Files by Character Count:', 'cyan')}")
    print(colored('──────────────────────────────────', 'cyan'))

    sorted_files: List[Tuple[str, int]] = sorted(
        file_char_counts.items(), key=lambda x: x[1], reverse=True
    )
    for i, (file_path, char_count) in enumerate(sorted_files[:top_files_length], 1):
        print(f"{colored(str(i) + '. ' + file_path, 'white')} {colored('(' + str(char_count) + ' chars)', 'white', attrs=['dim'])}")


def print_summary(
    total_files: int,
    total_characters: int,
    output_path: str,
    file_char_counts: Dict[str, int],
    top_files_length: int,
) -> None:
    """
    Print a summary of the repository packing process.

    Args:
        total_files (int): The total number of files processed.
        total_characters (int): The total number of characters in all files.
        output_path (str): The path where the output file is saved.
        file_char_counts (Dict[str, int]): A dictionary of file paths and their character counts.
        top_files_length (int): The number of top files to display.
    """
    print(f"\n{colored('📊 Pack Summary:', 'cyan')}")
    print(colored('────────────────', 'cyan'))
    print(colored('Total Files: ' + str(total_files), 'white'))
    print(colored('Total Chars: ' + str(total_characters), 'white'))
    print(colored('     Output: ' + output_path, 'white'))

    if top_files_length > 0:
        print_top_files(file_char_counts, top_files_length)


def print_completion() -> None:
    """
    Print a completion message indicating that the repository has been successfully packed.
    """
    print(f"\n{colored('🎉 All Done!', 'green')}")
    print(colored('Your repository has been successfully packed.', 'white'))
``` 

This code now uses the `termcolor` library for colored terminal output, maintaining the original functionality and structure.
from typing import Dict, List, Tuple
from rich.console import Console
from rich.text import Text

# Initialize rich console for colored terminal output
console = Console()


def print_top_files(file_char_counts: Dict[str, int], top_files_length: int) -> None:
    """
    Print the top files by character count.

    Args:
        file_char_counts (Dict[str, int]): A dictionary of file paths and their character counts.
        top_files_length (int): The number of top files to display.
    """
    console.print(Text("\n📈 Top {} Files by Character Count:".format(top_files_length), style="cyan"))
    console.print(Text("──────────────────────────────────", style="cyan"))

    sorted_files: List[Tuple[str, int]] = sorted(
        file_char_counts.items(), key=lambda x: x[1], reverse=True
    )
    for i, (file_path, char_count) in enumerate(sorted_files[:top_files_length], 1):
        console.print(Text(f"{i}. {file_path} ", style="white") + Text(f"({char_count} chars)", style="dim"))


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
    console.print(Text("\n📊 Pack Summary:", style="cyan"))
    console.print(Text("────────────────", style="cyan"))
    console.print(Text(f"Total Files: {total_files}", style="white"))
    console.print(Text(f"Total Chars: {total_characters}", style="white"))
    console.print(Text(f"     Output: {output_path}", style="white"))

    if top_files_length > 0:
        print_top_files(file_char_counts, top_files_length)


def print_completion() -> None:
    """
    Print a completion message indicating that the repository has been successfully packed.
    """
    console.print(Text("\n🎉 All Done!", style="green"))
    console.print(Text("Your repository has been successfully packed.", style="white"))

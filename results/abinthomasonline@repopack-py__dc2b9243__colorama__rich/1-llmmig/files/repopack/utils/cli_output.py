from typing import Dict, List, Tuple
from rich import print
from rich.text import Text


def print_top_files(file_char_counts: Dict[str, int], top_files_length: int) -> None:
    """
    Print the top files by character count.

    Args:
        file_char_counts (Dict[str, int]): A dictionary of file paths and their character counts.
        top_files_length (int): The number of top files to display.
    """
    print(f"\n[cyan]📈 Top {top_files_length} Files by Character Count:[/cyan]")
    print(f"[cyan]──────────────────────────────────[/cyan]")

    sorted_files: List[Tuple[str, int]] = sorted(
        file_char_counts.items(), key=lambda x: x[1], reverse=True
    )
    for i, (file_path, char_count) in enumerate(sorted_files[:top_files_length], 1):
        print(f"[white]{i}. {file_path} [dim]({char_count} chars)[/dim]")


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
    print(f"\n[cyan]📊 Pack Summary:[/cyan]")
    print(f"[cyan]────────────────[/cyan]")
    print(f"[white]Total Files: {total_files}[/white]")
    print(f"[white]Total Chars: {total_characters}[/white]")
    print(f"[white]     Output: {output_path}[/white]")

    if top_files_length > 0:
        print_top_files(file_char_counts, top_files_length)


def print_completion() -> None:
    """
    Print a completion message indicating that the repository has been successfully packed.
    """
    print(f"\n[green]🎉 All Done![/green]")
    print(f"[white]Your repository has been successfully packed.[/white]")

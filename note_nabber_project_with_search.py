#!/usr/bin/env python3
import os
import sys
import re
import shutil
import time
from pathlib import Path
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

console = Console()

def natural_sort_key(s: str):
    """
    Generate a natural sort key by splitting the string into text and number chunks.
    Example: "file10.txt" -> ['file', 10, '.txt']
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# === Animated Moonwalk Functions ===

def animate_moonwalk_art():
    """
    Animate a simple moonwalk ASCII art that alternates between two frames.
    """
    frames = [
r"""
           (O*)
            /|
             |
          <    \
   ~ Michael Jackson Moonwalk ~
""",
r"""
           (*O)
             |\
             |
          <    \
   ~ Michael Jackson Moonwalk ~
""",
r"""
           \O_*
             |
             |
            /  >
   ~ Michael Jackson Moonwalk ~
""",
r"""
           *_O/
             |
             |
            /  >
   ~ Michael Jackson Moonwalk ~
"""
    ]
    with Live(refresh_per_second=2, transient=True) as live:
        for i in range(20):
            frame = frames[i % len(frames)]
            live.update(Text(frame, style="bold magenta"))
            time.sleep(0.5)

def animate_moonwalk_across():
    """
    Animate Michael Jackson moonwalking across the screen from left to right.
    The ASCII art is shifted by adding increasing left padding on each frame.
    """
    frames = [
r"""
           _O/
            /|
             |
            / \
   ~ Michael Jackson Moonwalk ~
""",
r"""
           \O_
            /|
             |
            / \
   ~ Michael Jackson Moonwalk ~
"""
    ]
    terminal_width = console.size.width
    total_shifts = terminal_width + 30  # extra padding so it fully disappears
    with Live(refresh_per_second=10, transient=True) as live:
        for offset in range(total_shifts):
            frame = frames[offset % len(frames)]
            padded_frame = "\n".join(" " * offset + line for line in frame.splitlines())
            live.update(Text(padded_frame, style="bold magenta"))
            time.sleep(0.1)

# === Note Parsing / Writing Functions ===

def parse_notes(file_path: Path):
    """
    Parse a text file for notes.
    Each note starts with a header line "nab : <note_name>"
    and its content continues until a line containing exactly "^^^"
    which marks the end of the note.
    Any text outside of a note block is ignored.
    """
    notes = {}
    current_note_name = None
    current_lines = []
    note_started = False
    header_pattern = re.compile(r'^nab\s*:\s*(.+)$', re.IGNORECASE)
    
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not note_started:
                match = header_pattern.match(line)
                if match:
                    current_note_name = match.group(1).strip()
                    current_lines = []
                    note_started = True
            else:
                if line.strip() == "^^^":
                    if current_note_name is not None:
                        notes[current_note_name] = "\n".join(current_lines).strip()
                    note_started = False
                    current_note_name = None
                    current_lines = []
                else:
                    current_lines.append(line)
    return notes

def write_note(note_name: str, note_content: str, notes_dir: Path, backup_dir: Path):
    """
    Save a note's content to a file in both notes and backup directories.
    """
    note_file = notes_dir / f"{note_name}.txt"
    backup_file = backup_dir / f"{note_name}.txt"
    
    note_file.write_text(note_content, encoding="utf-8")
    backup_file.write_text(note_content, encoding="utf-8")
    
    console.log(f"[green]Note '{note_name}' saved successfully.[/green]")
    return note_file, backup_file

# === Note Processing Workflow ===

def choose_input_file() -> Path:
    """
    Ensure there's an 'input' directory and prompt the user to select a text file.
    """
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    while True:
        files = sorted(list(input_dir.glob("*.txt")), key=lambda f: natural_sort_key(f.name))
        if not files:
            console.print("[yellow]No input files found in the 'input' directory.[/yellow]")
            console.print("Please add your text file(s) to the 'input' directory and press Enter to continue...")
            input()
        else:
            break

    if len(files) == 1:
        file = files[0]
        confirm = Prompt.ask(f"Do you want to work on '{file.name}'? (y/n)", choices=["y", "n"], default="y")
        if confirm.lower() == "y":
            return file
        else:
            console.print("[red]Operation cancelled.[/red]")
            sys.exit(0)
    else:
        console.print("Multiple input files found in the 'input' directory:")
        for i, f in enumerate(files, start=1):
            console.print(f"{i}. {f.name}")
        while True:
            choice = Prompt.ask("Enter the number of the file you want to process", default="1")
            try:
                index = int(choice)
                if 1 <= index <= len(files):
                    return files[index-1]
                else:
                    console.print(f"[red]Invalid selection. Choose a number between 1 and {len(files)}.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

def process_notes_file():
    """Process an input notes file and create individual note files."""
    console.rule("[bold red]Note Nabber v2[/bold red]")
    input_path = choose_input_file()
    console.print(f"[cyan]Processing file:[/cyan] {input_path.name}")
    
    output_dir = Path("notes")
    backup_dir = Path("backup")
    output_dir.mkdir(exist_ok=True)
    backup_dir.mkdir(exist_ok=True)
    
    notes = parse_notes(input_path)
    if not notes:
        console.print("[yellow]No notes found in the file.[/yellow]")
        return
    
    # Display parsed notes
    table = Table(title="Parsed Notes")
    table.add_column("Note Name", style="cyan", no_wrap=True)
    table.add_column("Content Length", justify="right", style="magenta")
    for note_name, content in notes.items():
        table.add_row(note_name, str(len(content)))
    console.print(table)
    
    # Save?
    confirm = Prompt.ask("Do you want to save these notes? (y/n)", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print("[red]Operation cancelled.[/red]")
        return
    
    for note_name, content in sorted(notes.items(), key=lambda item: natural_sort_key(item[0])):
        write_note(note_name, content, output_dir, backup_dir)
    console.print("[bold green]All notes have been saved successfully![/bold green]")

# === File Management (CRUD, Move, Directory Creation, Directory Listing) ===

def list_files(directory: Path):
    """List all files in a directory and display them in a table."""
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist.[/red]")
        return []
    files = sorted([f for f in directory.iterdir() if f.is_file()], key=lambda f: natural_sort_key(f.name))
    if not files:
        console.print(f"[yellow]No files found in directory {directory}.[/yellow]")
    else:
        table = Table(title=f"Files in {directory}")
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Filename", style="magenta")
        for i, f in enumerate(files, start=1):
            table.add_row(str(i), f.name)
        console.print(table)
    return files

def list_directories(directory: Path):
    """List all subdirectories in a directory and display them in a table."""
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist.[/red]")
        return []
    dirs = sorted([d for d in directory.iterdir() if d.is_dir()], key=lambda d: natural_sort_key(d.name))
    if not dirs:
        console.print(f"[yellow]No subdirectories found in {directory}.[/yellow]")
    else:
        table = Table(title=f"Directories in {directory}")
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Directory Name", style="magenta")
        for i, d in enumerate(dirs, start=1):
            table.add_row(str(i), d.name)
        console.print(table)
    return dirs

def choose_file_from_list(files):
    """Prompt the user to choose a single file from a list."""
    if not files:
        return None
    files = sorted(files, key=lambda f: natural_sort_key(f.name))
    if len(files) == 1:
        return files[0]
    table = Table(title="Select a File")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Filename", style="magenta")
    for i, f in enumerate(files, start=1):
        table.add_row(str(i), f.name)
    console.print(table)
    while True:
        choice = Prompt.ask("Enter the file number", default="1")
        try:
            index = int(choice)
            if 1 <= index <= len(files):
                return files[index - 1]
            else:
                console.print(f"[red]Invalid selection. Choose a number between 1 and {len(files)}.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")

def choose_multiple_files_from_list(files):
    """
    Prompt the user to choose multiple files from a list.
    Enter comma-separated numbers (e.g., "1,3,5").
    Returns a list of selected files.
    """
    if not files:
        return []
    files = sorted(files, key=lambda f: natural_sort_key(f.name))
    table = Table(title="Select Files (comma-separated indices)")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Filename", style="magenta")
    for i, f in enumerate(files, start=1):
        table.add_row(str(i), f.name)
    console.print(table)
    
    while True:
        indices_input = Prompt.ask("Enter the file numbers (comma-separated)")
        try:
            indices = [int(x.strip()) for x in indices_input.split(",") if x.strip()]
            if all(1 <= idx <= len(files) for idx in indices):
                return [files[idx - 1] for idx in indices]
            else:
                console.print("[red]One or more numbers are out of range. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter valid numbers separated by commas.[/red]")

def view_file(filepath: Path):
    """Display the content of a file."""
    if not filepath.exists():
        console.print(f"[red]File {filepath} does not exist.[/red]")
        return
    content = filepath.read_text(encoding="utf-8")
    console.rule(f"[bold green]Content of {filepath.name}[/bold green]")
    console.print(content)

def create_file(directory: Path):
    """Create a new file in a given directory."""
    filename = Prompt.ask("Enter new file name (with extension, e.g. 'example.txt')")
    filepath = directory / filename
    if filepath.exists():
        console.print(f"[red]File {filepath} already exists.[/red]")
        return
    content = Prompt.ask("Enter content for the new file (leave blank for empty)", default="")
    filepath.write_text(content, encoding="utf-8")
    console.print(f"[green]File {filepath} created successfully.[/green]")

def edit_file(filepath: Path):
    """Edit a file using an external editor (defaults to nano)."""
    if not filepath.exists():
        console.print(f"[red]File {filepath} does not exist.[/red]")
        return
    editor = os.environ.get("EDITOR", "nano")
    console.print(f"Opening {filepath} in editor [bold]{editor}[/bold]...")
    os.system(f"{editor} {filepath}")

def delete_file(filepath: Path):
    """Delete a file after user confirmation."""
    if not filepath.exists():
        console.print(f"[red]File {filepath} does not exist.[/red]")
        return
    confirm = Prompt.ask(f"Are you sure you want to delete {filepath.name}? (y/n)", choices=["y", "n"], default="n")
    if confirm.lower() == "y":
        filepath.unlink()
        console.print(f"[green]File {filepath.name} deleted successfully.[/green]")
    else:
        console.print("[yellow]Deletion cancelled.[/yellow]")

def move_file(filepath: Path, target_directory: Path):
    """Move a single file to a target directory."""
    if not filepath.exists():
        console.print(f"[red]File {filepath} does not exist.[/red]")
        return
    if not target_directory.exists():
        console.print(f"[red]Target directory {target_directory} does not exist.[/red]")
        return
    new_path = target_directory / filepath.name
    shutil.move(str(filepath), str(new_path))
    console.print(f"[green]File {filepath.name} moved to {target_directory} successfully.[/green]")

def create_directory():
    """Create a new directory by specifying a parent path and a new directory name."""
    parent_input = Prompt.ask("Enter the parent directory path (default is current directory)", default=".")
    parent_directory = Path(parent_input)
    if not parent_directory.exists():
        console.print(f"[red]Parent directory {parent_directory} does not exist.[/red]")
        return
    new_dir_name = Prompt.ask("Enter the name for the new directory")
    new_directory = parent_directory / new_dir_name
    if new_directory.exists():
        console.print(f"[red]Directory {new_directory} already exists.[/red]")
        return
    new_directory.mkdir(parents=True, exist_ok=False)
    console.print(f"[green]Directory {new_directory} created successfully.[/green]")

def file_management_menu():
    """File management submenu offering CRUD, move, directory creation and listing."""
    base_directory = Path("notes")
    base_directory.mkdir(exist_ok=True)
    while True:
        console.rule("[bold blue]File Management Menu[/bold blue]")
        console.print("1. List files")
        console.print("2. List directories")
        console.print("3. View file content")
        console.print("4. Create a new file")
        console.print("5. Edit a file")
        console.print("6. Delete a file")
        console.print("7. Move file(s)")
        console.print("8. Create a new directory")
        console.print("9. Return to Main Menu")
        choice = Prompt.ask("Enter your choice", choices=[str(i) for i in range(1,10)], default="9")
        
        if choice == "1":
            list_files(base_directory)
        elif choice == "2":
            list_directories(base_directory)
        elif choice == "3":
            files = list_files(base_directory)
            if files:
                file = choose_file_from_list(files)
                if file:
                    view_file(file)
        elif choice == "4":
            create_file(base_directory)
        elif choice == "5":
            files = list_files(base_directory)
            if files:
                file = choose_file_from_list(files)
                if file:
                    edit_file(file)
        elif choice == "6":
            files = list_files(base_directory)
            if files:
                file = choose_file_from_list(files)
                if file:
                    delete_file(file)
        elif choice == "7":
            files = list_files(base_directory)
            if files:
                selected_files = choose_multiple_files_from_list(files)
                if selected_files:
                    target_dir_input = Prompt.ask("Enter target directory path", default=str(base_directory))
                    target_directory = Path(target_dir_input)
                    for f in selected_files:
                        move_file(f, target_directory)
        elif choice == "8":
            create_directory()
        elif choice == "9":
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

# === NEW SEARCH FEATURE: Lines that Contain the Search Term + Backup Dedup ===

def search_in_project(root_dir: Path, search_term: str):
    """
    Recursively search all files under 'root_dir' (excluding .py, .bat, and venv/).
    Return a dict keyed by file_path -> list of lines (with highlights) that contain the search term.
    
    We'll do a line-by-line search (case-insensitive).
    """
    results = defaultdict(list)
    search_term_lower = search_term.lower()
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip any directory named 'venv'
        if 'venv' in dirpath.split(os.sep):
            continue
        
        for filename in filenames:
            # Skip .py and .bat
            if filename.endswith('.py') or filename.endswith('.bat'):
                continue

            full_path = Path(dirpath) / filename
            
            # Read file line by line
            try:
                with full_path.open('r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Check if search term is in this line (case-insensitive)
                        if search_term_lower in line.lower():
                            # Create a Rich Text for the line, highlight all matches
                            line_text = Text(line.rstrip("\n"))
                            line_text.highlight_words([search_term], style="reverse red", case_sensitive=False)
                            
                            results[full_path].append(line_text)
            except Exception as e:
                console.log(f"[red]Could not read file: {full_path}[/red], reason: {e}")
                continue

    return results  # {Path: [Text(line_with_highlights), ...]}

def filter_backup_duplicates(raw_results: dict[Path, list[Text]]):
    """
    raw_results is a dict: {file_path: [list of highlighted lines]}
    
    For each filename, if there's a match outside 'backup' and also in 'backup',
    keep only the non-backup results. Otherwise, keep the backup results.
    """
    # Group paths by filename
    paths_by_filename = defaultdict(list)
    for p in raw_results.keys():
        paths_by_filename[p.name].append(p)

    # We'll build a new dict of final results
    final_results = {}
    
    for fname, paths in paths_by_filename.items():
        # Check if any path for this fname is outside backup
        has_non_backup = any("backup" not in path.parts for path in paths)
        
        if has_non_backup:
            # Keep only those outside 'backup'
            chosen_paths = [p for p in paths if "backup" not in p.parts]
        else:
            # Keep all in backup (since there's no outside-backup match)
            chosen_paths = paths

        # Add them to final_results
        for cp in chosen_paths:
            final_results[cp] = raw_results[cp]
            
    return final_results

def search_project_menu():
    """
    Prompt for a search term, do a line-based search, highlight matches,
    filter out duplicates in backup. Then display lines containing the search term.
    
    We show one row per file. In that row, we only show lines that matched
    (each line on a new line in the Rich text).
    """
    console.rule("[bold yellow]Search Project Files[/bold yellow]")
    search_term = Prompt.ask("Enter the search term")
    if not search_term.strip():
        console.print("[red]Search term cannot be empty.[/red]")
        return
    
    project_root = Path.cwd()  # or Path(__file__).parent if you prefer
    raw_results = search_in_project(project_root, search_term)
    if not raw_results:
        console.print("[yellow]No matches found.[/yellow]")
        return
    
    # Filter out backup duplicates
    deduped_results = filter_backup_duplicates(raw_results)
    if not deduped_results:
        console.print("[yellow]No matches found (after backup filtering).[/yellow]")
        return

    # Display results
    table = Table(title="Search Results (Lines Containing Your Term)")
    table.add_column("File (click to open if supported)", style="cyan", no_wrap=True)
    table.add_column("Matching Lines", style="white")

    for file_path, lines_list in sorted(deduped_results.items(), key=lambda x: natural_sort_key(str(x[0]))):
        # Build file link
        file_link = f"[link=file://{file_path.resolve()}]{file_path}[/link]"
        
        # Combine all matched lines into one Text object, each line on its own line
        combined_text = Text()
        for i, line_text in enumerate(lines_list):
            if i > 0:
                combined_text.append("\n")  # newline between lines
            combined_text.append(line_text)
        
        table.add_row(file_link, combined_text)

    console.print(table)

# === MAIN MENU ===

def main_menu():
    """Display the main menu for the script."""
    console.print("[bold green]Welcome to Note Nabber v2![/bold green]")
    while True:
        console.rule("[bold yellow]Main Menu[/bold yellow]")
        console.print("1. Process input notes file")
        console.print("2. File management (CRUD, Move, Directory Creation & Listing)")
        console.print("3. Display Animated Moonwalk")
        console.print("4. Display Moonwalk Across Screen")
        console.print("5. Exit")
        console.print("[cyan]6. Search Project Files[/cyan]")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6"], default="5")
        
        if choice == "1":
            process_notes_file()
        elif choice == "2":
            file_management_menu()
        elif choice == "3":
            animate_moonwalk_art()
        elif choice == "4":
            animate_moonwalk_across()
        elif choice == "5":
            console.print("[bold green]Goodbye![/bold green]")
            break
        elif choice == "6":
            search_project_menu()
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

if __name__ == "__main__":
    main_menu()

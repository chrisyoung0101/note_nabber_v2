#!/usr/bin/env python3
import os
import sys
import re
import shutil
import time
from pathlib import Path

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
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

# === Animated Moonwalk Functions ===

def animate_moonwalk_art():
    """
    Animate a simple moonwalk ASCII art that alternates between two frames.
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

# === Note Processing Functions ===

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
    
    table = Table(title="Parsed Notes")
    table.add_column("Note Name", style="cyan", no_wrap=True)
    table.add_column("Content Length", justify="right", style="magenta")
    for note_name, content in notes.items():
        table.add_row(note_name, str(len(content)))
    console.print(table)
    
    confirm = Prompt.ask("Do you want to save these notes? (y/n)", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print("[red]Operation cancelled.[/red]")
        return
    
    for note_name, content in sorted(notes.items(), key=lambda item: natural_sort_key(item[0])):
        write_note(note_name, content, output_dir, backup_dir)
    console.print("[bold green]All notes have been saved successfully![/bold green]")

# === File Management Functions (CRUD, Move, Directory Creation, Directory Listing) ===

def list_files(directory: Path):
    """List all files in a directory and display them in a table."""
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist.[/red]")
        return []
    files = sorted([f for f in directory.iterdir() if f.is_file()], key=lambda f: natural_sort_key(f.name))
    if not files:
        console.print(f

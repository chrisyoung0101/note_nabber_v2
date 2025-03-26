#!/usr/bin/env python3
from pathlib import Path
import random
import lorem
from rich.prompt import Prompt
from rich.console import Console

console = Console()

def generate_notes(note_count: int, file_path: Path):
    titles = [lorem.sentence().split()[0].capitalize() + str(random.randint(1,1000)) for _ in range(note_count)]
    with file_path.open("w", encoding="utf-8") as file:
        for title in titles:
            file.write(f"nab : {title}\n")
            # Generate between 2-5 paragraphs per note
            paragraphs = random.randint(2, 5)
            for _ in range(paragraphs):
                file.write(lorem.paragraph() + "\n\n")
    console.print(f"[green]Successfully created [bold]{note_count}[/bold] notes in [bold]{file_path}[/bold][/green]")

def main():
    console.print("[bold blue]Test Note Generator for Note Nabber[/bold blue]")
    note_count = Prompt.ask("How many test notes would you like to generate?", default="10")
    
    try:
        note_count = int(note_count)
    except ValueError:
        console.print("[red]Please enter a valid number![/red]")
        return
    
    output_file = Path("input/test_notes.txt")
    output_file.parent.mkdir(exist_ok=True)
    
    generate_notes(note_count, output_file)

if __name__ == "__main__":
    main()

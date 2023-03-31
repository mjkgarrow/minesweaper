A minesweaper clone made with Pygame.

![Minesweaper](./minesweaper%20screenshot.png)

## Usage
Clone repo and create a virtual environment, install requirements:
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`

Run game:  
`python minesweaper.py`

## Rules
Minesweeper is a game where mines are hidden in a grid of squares. Safe squares have numbers telling you how many mines are within the 3x3 grid around the square. You can use the number clues to solve the game by opening all of the safe squares. 

You can flag mines with the right mouse button.

If you click on a mine you lose the game!


## Current issues
- Game currently doesn't finish when you find all the mines.
- The game clock doesn't reset.
- The mine counter is a bit buggy and doesn't reset or show the correct number of mines
- First click isn't automatically safe, so sometimes you will lose without even doing anything

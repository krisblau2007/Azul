# Pygame Starter (Multiplayer, Turn-Based)

A barebones turn-based prototype: 2-4 players, no enemies — everyone
plays by the same rules. Each player has their own board to mark, and
a "Pass Turn" button is the only thing that advances whose turn it is.
It's meant to be *deleted into* — replace the placeholder bits with
your actual game.

## Structure

```
main.py                    # entry point — just calls App().run()
game/
  settings.py               # players, board size, colors, computed layout
  app.py                     # owns the window/clock, drives the loop
  states/
    base_state.py            # interface every state implements
    menu_state.py             # title screen + player-count picker
    play_state.py             # turn engine + board rendering/clicks (takes num_players)
  entities/
    player.py                 # identity + that player's board state
```

## A note on Python 3.14

If you're on Python 3.14+: the original `pygame` package doesn't have
3.14 wheels yet (its maintenance has slowed and this is a known open
issue). This project uses **`pygame-ce`** instead — a drop-in,
actively maintained fork with the same `import pygame` API, supporting
3.10 through 3.15+. Nothing in the game code changes.

If you previously tried installing plain `pygame` in this venv, remove
it first so the two don't conflict:
```bash
pip uninstall pygame pygame-ce -y
pip install -r requirements.txt
```

## Run it

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

On the title screen, choose 2-4 players (click a number, or press
the matching digit key) and click **Start Game** (or press
ENTER/SPACE). Each player's 3x3 board is shown at once; the active
player's board has a colored border. Click a cell on the **active**
player's board to toggle a mark, then click **Pass Turn** to hand
control to the next player. ESC returns to the menu at any time.

## How the turn engine works

- **No enemies, no distinction between players.** `Player` (in
  `entities/player.py`) is the only entity class, and every player is
  created the same way in `PlayState.__init__` from
  `settings.NUM_PLAYERS`.
- **Each `Player` owns its board state** — a `BOARD_ROWS x BOARD_COLS`
  grid of booleans (`marks`) — and nothing else. It doesn't know where
  it's drawn on screen; that's `PlayState`'s job.
- **`PlayState.current_player_index`** is the single source of truth
  for whose turn it is. `_handle_board_click` only accepts clicks
  inside *that* player's board rect — clicking another player's board
  does nothing, by design.
- **The "Pass Turn" button is the only thing that advances a turn.**
  `_pass_turn()` just increments `current_player_index` (wrapping
  around) and the turn counter — there's no automatic action, timer,
  or AI involved. `update(dt)` is a no-op for the same reason as
  before: this game only changes state in response to clicks.
- **Screen layout is computed, not hand-placed.** `settings.py` works
  out how many boards fit per row and computes `SCREEN_WIDTH`/
  `SCREEN_HEIGHT` from `NUM_PLAYERS`, so changing player count doesn't
  require touching layout code.

## Choosing the number of players

This is now picked on the menu screen: click a number (2-4), then
**Start Game** (or press the matching number key, then ENTER/SPACE).
The selected count is passed into `PlayState(app, num_players=...)`.

The window itself is always sized for `settings.MAX_PLAYERS` (4) so
starting a game never needs to resize the window — picking fewer
players just leaves unused space in the board layout rather than
shrinking the window. To change the maximum offered on the menu, edit
`MAX_PLAYERS` in `settings.py`; `PLAYER_COUNT_OPTIONS` in
`menu_state.py` derives from it automatically. Player names still come
from a hardcoded list (`DEFAULT_PLAYER_NAMES` in `play_state.py`) —
see below for making that configurable too.

## What to extend first

Roughly in the order you'll hit them:

1. **A win condition.** Right now marking is just toggling — there's
   no rule that says a board is "complete." Add a check in
   `Player` (e.g. `is_complete()`) or `PlayState` after each click,
   and a win overlay similar to the old game-over screen.
2. **Named/typed players** instead of "Player 1/2/3/4" — prompt for
   names on the menu screen, or read them from a config file, and
   pass them into `PlayState.__init__`.
3. **Turn-based *rules*, not just marking.** Right now any cell can be
   toggled any number of times. If your game needs "mark exactly one
   cell per turn" or "can't unmark," enforce that in
   `_handle_board_click` (e.g. auto-call `_pass_turn()` after a valid
   mark, or reject clicks on already-marked cells).
4. **Shared visibility rules.** If players shouldn't see each other's
   boards (e.g. Battleship-style hidden info), render other players'
   grids as blank/face-down when they're not active, instead of always
   showing marks.
5. **Persistence** — save/load `marks` per player (e.g. to JSON) so a
   game can be paused and resumed.
6. **Sound/feedback** on marking or passing turn —
   `pygame.mixer.Sound(...).play()`; init `pygame.mixer` in
   `App.__init__`.

## Why this stack

Pygame(-ce) for a *prototype* game because: pure Python (no build
step), huge community/docs, and mouse-driven UI (boards, buttons) is
just as native to it as keyboard-driven games. The state machine and
loop from `App`/`BaseState` didn't need to change at all for this
redesign — only what happens inside `PlayState` did, which is the
point of keeping states self-contained.

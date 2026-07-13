# void-miner

An asteroid mining game, built with [pygame](https://www.pygame.org/).

## Current features

- A ship sitting in the void.
- **Scan** the surrounding space to locate a minable asteroid.
- **Fly** to a found asteroid (travel currently takes a fixed 10s).

## Controls

| Key | Action |
| --- | --- |
| `S` | Scan for an asteroid |
| `F` | Fly to the found asteroid |
| `Q` / `Esc` | Quit |

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Roadmap

- Actually mine the asteroid once docked (yield ore over time).
- Cargo hold + selling ore.
- Travel time based on distance / ship speed.
- Multiple asteroids with different ore types.

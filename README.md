# Curse of the Mites

Curse of the Mites is a text based MUD (multi-user dungeon) in which you play as a caterpillar whose goal is to grow into a butterfly by gaining enough XP.

Curse of the Mites has a server based off of `websockets`, and a client written in python's `textual` framework.

![Client Preview](/assets/client-preview.png)

## Getting started

### Dependencies

- Python (3.10)
- Poetry
- Git (for cloning the repository)

### Clone Repository

```shell
git clone git@github.com:AbooMinister25/Curse-of-the-Mites.git
```

### Run Server

Make sure your in the directory in which the server's code is located in (`server/` folder in whatever directory the code is located in).

```shell
poetry run python3 main.py
```

### Run the client

Make sure your in the directory in which the client's code is located in (`client/` folder in whatever directory the code is located in).

Before you run the client, make sure that whatever terminal you're using is full-screened.

```shell
poetry run python3 main.py
```

Multiple clients can be run and connected to the server at the same time.

## Gameplay

Curse of the Mites's (CotM) main objective is for you to gain enough XP to level up until you become a butterfly. XP is gained through killing mobs and players around the map.

### Registering

Once you launch your client, you will be asked to register. All this consists of is you providing a username to go by while playing the game. You can register by using the `/register` command, followed by your username.

```
/register aboo
```

### The Map

The map is shown above your console, and lists all players and your current position. Your character will be marked by a yellow `@` sign, while other players will be marked by a blue `@` sign. You will not be able to see mobs, and the console will notify you if you encounter one.

### Movement

Movement is done through the `!move` command, followed by whatever direction you wish to move in (one of north, east, south, west).

```
!move north
!move east
!move south
!move west
```

Whenever you run one of these commands, you're movement will be added to a queue, after which it'll be processed every time the game ticks (every six seconds). Heres where our bug comes in - every time you run the client, your movement controls will be shuffled, meaning that running `!move north` won't necessarily move you north.

### Actions

Actions are ways for you (the player) to attack players and mobs, heal yourself, etc. The following actions are currently available.

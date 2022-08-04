# Curse of the Mites

Curse of the Mites is a text based MUD (multi-user dungeon) in which you play as a caterpillar whose goal is to grow into a butterfly to escape the forest cursed by mites.

(Recommended reading to truly appreciate the nastiness of mites: https://en.wikipedia.org/wiki/Varroa_destructor)

Curse of the Mites has a server based off of `websockets`, and a TUI client written with the `textual` framework and `websockets` for communications.

All of the possible messages that can be sent and received between the client and the server correspond to pydantic schemas stored in the `/common` folder.

![Client Preview](/assets/client-preview.png)

## Getting started

### Dependencies

- Python (3.10)
- Poetry
- Git (for cloning the repository)

### Clone Repository

```shell
git clone https://github.com/AbooMinister25/Curse-of-the-Mites.git
```

### Install the game.

To install the server:
Enter the `/server` folder in your terminal and run:
```shell
poetry install
```

Same steps are required for the client (but you must enter the `/client` folder).

### Run Server

Make sure you are in the `/server` folder and run:

```shell
poetry run python3 main.py
```

### Run the client

Run the server before you attempt running the client.
Make sure you are in the `/client` folder and that whatever terminal you're using is full-screened. Then you can run:

```shell
poetry run python3 main.py
```

Multiple clients can be run and connected to the server at the same time.

## Gameplay

Curse of the Mites's (CotM) main objective is for you to gain enough XP to level up until you become a butterfly. XP is gained through killing mobs around the map. You control your caterpillar through the client's console.

The twist of the game is that the titular "curse" is brain scrambling! Each of your actions is actually mapped to a different action. For example: when you try to `!move north` you may end up moving south. Or when you try to `!sing` to your allies to heal them you'll spit and hurt them!

### Registering

Once you launch your client, you will be asked to register. All this consists of is you providing a username to go by while playing the game. You can register by using the `/register` command, followed by your username.

```
/register aboo
```
If you disconnect while playing the game your caterpillar's brain will be completely melted and it'll die (yes, you're a bad person).

### The console

This is a "console" within the console you're currently running your client in. It contains a space for you to type your commands in at the bottom and a log for you to receive information about the game on top.

Keep in mind that if you clicked outside of the console you'll have to click into it in order to type.

You can type in `/help` to receive help about your available commands.

### The Map

The map is shown above your console, and lists all players and your current position. Your character will be marked by a yellow `@` sign, while other players will be marked by a blue one. You will not be able to see mobs, and the console will notify you if you encounter one.

Each "tile" of the map corresponds to a room, you must be in the same room as other entities in order to interact with them.

### Time

"Time" in this game happens every 6 seconds! Which means after each round every player will have a 6 second interval to decide what they wish to do next. Once time "ticks" the next queued move of every player will be used.

### Actions

You can see all of the actions you have available in the bottom right corner of your console.
There are two main type of actions, movement and "spells":

#### Movement
Movement is done through the `!move` command, followed by whatever direction you wish to move in (one of north, east, south, west). For example: `!move north`.

You can also use numbers to move the following way (this type of movement is intended to be done with the numpad):
```
         (north?)
            8
            ↑
(west?) 4 ← . → 6 (east?)
            ↓
            2
         (south?)
```
Once you start fighting with mobs you cannot move! If you really want to get out of there you'll have to try `!flee`ing.

#### Spells
Spells are your way of affecting the health of other entities and yourself. There are targeted attacks and heals, AOE attacks and heals (not targeted) and self heals (not targeted).

When your brain is scrambled, targeted spells will be mapped to other targeted spells and the same will happen with no-target spells.

AOE (area of effect) spells will affect every entity in the room other than the caster. Keep in mind that they can be very powerful but you may harm your fellow players and heal your enemies with them!

To try casting a spell simply do `!(name of the spell)` or `!(name of the spell) (name of the target)` if the spell is targeted. You can see the names of the entities you can target in the top right corner of the console.

#### Special actions
There are three special actions that do not get scrambled:

`!nvm`: removes the last action you entered from your action queue.

`!clear`: removes every action from your action queue.

`!flee`: allows you to abandon a combat and move (keep in mind that it has a chance of failing!).

### Combat strategy

Enemies can have a lot of health and they can even regenerate it. You can team up with other players and take on the mob together.

### The action queue
Each time you type in an action command, this action gets added to your caterpillar's action queue. This allows you to "prepare" moves for next rounds.

For example (let's assume your moves aren't scrambled), if you type `!move north`, `!move east`, `!sing` in quick succession: next round your caterpillar will move north, 6 seconds after that it'll move east and after another 6 seconds it will sing.

### Chatting
Anything other than a valid action that you type will be treated as chatting. Chatting is instantaneous and every other player in the server will be able to read what you said.


### Combat
Combat can be between two players, or a player and a mob. In order to engage in combat with a mob, you will need to be in the same room as the mob, and be the one to make the first move. Mobs will not attack unless provoked. Attacks from a mob you are engaged in combat with will happen every tick of the game.


## The Interface
The interface for the MUD is in the form of a TUI with four distinct sections. 

### The Map
On the top left is the map. The map displays your player's location as a yellow `@` sign, and other players as a blue `@` sign. Other entities besides players will not
be displayed on the map (Spiders and Mites). Each tile on the map is a room, rooms are colored based on what they are. Leaves are light green and dark green, the player can freely move on them. Walls are green, the player cannot move towards them.
Spiders Den's are red. When you move onto a Spiders Den, you will encounter a Spider.

![Map](/assets/map.png)

### The Console
The console is located on the bottom left of the interface. The console itself is divided into two parts. The bottom part consists of a message box, where you can enter chat messages and run commands. The top part is the out console, it is a log
of all messages, events, and chat messages that have occured in the MUD. When you send a chat message, it will appear on the out console in the format `[name]: [message]`. The out console will also display different events. When another player
enters your room, you will recieve a notification in the out console. When you try to do an action and are out of mana, the out console will notify you. The out console will also display the status of events like combat. You can use the
up/down arrow keys to scroll up or down the console.

![Console](/assets/console.png)

### Entities List
The entities list is located on the top right of the interface. It will list all entities which are in your room. Since you cannot see mobs on the map, the entities list is how you will know whether a mob is in your room or not.

![Console](/assets/entities.png)

### Allowed Moves List
The allowed moves list lists all of the allowed moves you can make.

![Console](/assets/allowed_moves.png)

## Design decisions

### Communications

Both the server and the client utilize the `websockets` library to send and receive all of their messages.

Both in the client and the server we have decided to have a single "message handler". This is to avoid problems with two points of the program trying to `recv` messages at the same time which leads to a `websockets` exception. This also ensures that we can receive messages at almost any point of the runtime, since trying to create specific windows of time when only specific messages can be received can lead to unexpected bugs.

The only exception to this rule is the initialization of a client. Since most other actions require the client to have a caterpillar, we must make sure that the first message the server receives from a new client is a `register` message.

The structure of all possible messages to be sent and received is given by pydantic models in `/common/schemas.py`. The sender must build a valid message using one of these models, and the receiver can deserialize it using the functions from `/common/deserialize.py`.

Our message handlers utilize pattern matching to easily handle each kind of message (example from `/client/main.py`):
```py
event = deserialize_server_response(json.loads(message))
match event:
    case ChatMessage():
        self.console_widget.out.add_log(
            f"{event.player_name}: {event.chat_message}"
        )
    case RegistrationSuccessful():
        self.initialized = True
        self.name = event.player.name
        ...
```

Normally the server immediately tries to respond to the client after receiving a message, this is because we want the player to have some form of immediate feedback of their action having been processed (e.g: `Added action to queue`).

Once a turn has passed, after the player already received some immediate feedback, the server will send the client information about the results of their actions and other relevant actions that were effected by other entities.

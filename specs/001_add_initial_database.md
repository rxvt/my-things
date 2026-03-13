# Add initial database

Status: draft

## Overview

We need to create a basic database framework and schema that we can build upon later.

## Requirements

* Database functions should live in `./lib/db.py`
* We are using SQlite
* The database file should be called entries.db, this file should live in `./local/share/lister/entries.db`
which conforms to the XDG spec
* XDG directories should be determined by `xdg-base-dirs` python package.
* We will be using a hand rolled basic schema migration implementation, using the `PRAGMA user_version`
feature of SQLite
* The app will support lists of multiple types so we need an Index table to keep track of the various lists
  * For instance there will be a list of Movies, Books and Games at least
* Each type of list will need its own fields so each list should have its own table with specific columns

## Initial tables

1. `games`
2. `developers`
3. `platform`
4. `list_index`

### games Table Fields

The purpose of this table is to capture details for each game that I've played.

* id
* game
* date_finished NULL
* platform (foreign key to `platform.name`)
* comments
* developer (foreign key to `developers.name`)

### developers Table Field

The purpose of this table is to capture details for each Developer that has created
the games that I have played. Linking this to the entries in the `games` table ensures
consistent naming of Developers.

* id
* name

### platform Table Fields

The purpose of this table is to capture details of each Platform upon which I've played
the various games. Linking this to the entries in the `games` table ensures consistent
naming of the Platforms.

* id
* name

### list_index Table Fields

The purpose of this table is to contain the list of lists so we can present an index
to the user asking them which list they would like to interact with.

* id
* name

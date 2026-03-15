# Add game to list

Status: in-progress

## Overview

Add the ability to add a new game to the Games list.

## Requirements

* Pressing `a` on the Games listing screen should bring up a screen where you can add:
  - Title
  - Developer
  - Date Finished
  - Platform
  - Comments
* This screen should be presented as a Modal overlaying the games list. Dismissing the Modal returns the user to the games list.
* The `Developer` field should only allow selections from the `developers` table.
* When typing the `Developer` name the field should auto-complete. If no existing entry is found then the newly typed entry is saved.
* The `Platform` field should only allow selections from the `platform` table. Should be a standard select widget with the 1st entry already selected.
* Let's pre-populate the `platform` table with some entries since they are fairly static and won't need an interface for adding new entries.
  - Switch
  - PS3
  - PS4
  - PS5
  - PC
  - Xbox360
  - 3DS
  - Dolphin
  - Xbox
  - NES
* The `Date Finished` field should restrict input to the format of `yyyy-mm-dd`.
* The `Date Finished` field cannot be empty.
* The `Date Finished` field should default to the current date.
* The `Title` field cannot be empty.
* The `Developer` field cannot be empty.
* The `Platform` field cannot be empty.
* The `Comments` field can be empty.
* The `Comments` field should be a line line input initially but add a small button next to Comments that opens a separate modal with a full TextArea widget (multi-line, markdown-capable). The TextArea content syncs back to the Comments field on close. The single-line Input shows a truncated preview.

## Implementation Details

* A DB helper function should be created to retrieve the list of developer information.
* A DB helper function should be created to retrieve the list of platform information.
* A DB helper function should be created to get or create a Developer
* A DB helper function should be created to insert a new game entry

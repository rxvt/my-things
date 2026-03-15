# Add games list

Status: implemented

## Overview

Define the index of the list of games played.

## Requirements

* This screen should be accessed via selecting `Games` from the main index.
* Should list each games title and date finished in ascending order based on the date finished.
* Entries should be centered on the screen.
* Should include a footer.
* Key bindings should include `a` for adding an entry, `e` for editing an entry and `d` for deleting an entry.
* Pressing `a` or `e` shouldn't do anything for now.
* If `d` is selected to delete an entry a confirmation dialog should appear with Yes/No options. The
No option should be selected by default.
* The list of entries should show a maximum of 20 entries before scrolling.
* The 1st entry in the list should be selected by default.
* Game finished dates should be in the format of `yyyy-mm-dd`.
* Only games that have been finished are added to this list so the finished date will always have a
valid value.

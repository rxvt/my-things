# Add games list edit modal

Status: in-progress

## Overview

When viewing the list of game entries we should be able to press the `e` shortcut to edit the entry.

## Requirements

* When viewing the list of game entries, pressing `e` must show an Edit Game modal.
* The Edit Game modal should use the same modal as the Add Game modal but with the existing data for the game being populated into the fields and available for editing.
* The title of the modal should be `Edit Game` rather than the normal `Add Game`.
* Use UPSERT in the SQL to avoid branching in the code for INSERT vs UPDATE.


# Create initial list index screen

Status: draft

## Overview

Create the initial index screen that displays a list of all the different Lists we are capturing information for.

## Requirements

* Should have a Textual footer
* Should use a Textual [ListView](https://textual.textualize.io/widget_gallery/#listview) for the actual list
* We are only displaying the list of Lists for now, selecting them will do nothing
* The Textual app code should live in `main.py`
* The DB should be initialised on app startup using the DB lib utils already created
* Items on the index screen should be centered, with the 1st item already selected
* CSS should be used to style the app
* We should display a maximum of 5 Lists before scrolling

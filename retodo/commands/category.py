#!/usr/bin/python3

# PyTodo
# Simple CLI to-do
# v0.0.1

import json
import click
import questionary
import os
from datetime import datetime
from tinydb import TinyDB, Query
from os import path
from rich.table import Table
from rich.console import Console
from rich import box

DB_FILE_TASKS = os.environ['HOME'] + '/.retodo/tasks.json'
DB_FILE_CATEGORY = os.environ['HOME'] + '/.retodo/category.json'


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


@click.group(cls=AliasedGroup)
def category():
    pass


def confirmation_question(question):
    answer = questionary.confirm(question, default=False).ask()
    return answer


def input_question(question):
    answer = questionary.text(question).ask()
    return answer


def listing_categories(question, choices):
    answer = questionary.select(
            question,
            choices=choices
            ).ask()
    return answer


def status_color(status):
    color_status = ""
    # setting emoji for status
    if status == "TODO":
        color_status = "⏳"
    elif status == "DONE":
        color_status = "✅"
    elif status == "ABORTED":
        color_status = "❌"
    return color_status


def get_status():
    status = [
                'TODO ⏳',
                'DONE ✅',
                'ABORTED ❌'
            ]
    return status


def get_all_category():
    database = TinyDB(DB_FILE_CATEGORY)

    categories = []
    for category in database.all():
        categories.append(f"{category['emoji']} {category['id']}")
    return categories


def get_category_emoji(category):
    # just in case there is no category
    if category == None:
        return "📋"
    category = category[2:]
    database = TinyDB(DB_FILE_CATEGORY)
    Category = Query()
    result = database.search(Category.id == category)
    return result[0]['emoji']


@category.command(name='new')
def create_category():
    """Create a new category """
    
    # get value
    name_not_empty = False
    emoji_not_empty = False
    while name_not_empty is not True:
        category_name = input_question("Category name:")
        if not category_name:
            print("Category name can't be empty")
        else:
            name_not_empty = True
    while emoji_not_empty is not True:
        category_emoji = input_question("Insert emoji:")
        if not category_emoji:
            print("Category emoji can't be empty")
        else:
            emoji_not_empty = True

    # insert in database
    database = TinyDB(DB_FILE_CATEGORY)
    database.insert({
            'id': category_name,
            'emoji': category_emoji
        })

    # return 0 and a message
    print(f"Created {category_name}")
    return 0


@category.command(name='list')
def list_category():
    """List all categories"""

    # fetching all categories in database
    database = TinyDB(DB_FILE_CATEGORY)
    categories = database.all()

    # initializing rich table
    console = Console()
    table = Table(box=box.SIMPLE)
    table.add_column('Category name')
    table.add_column('Emoji')

    # append data to rich table
    for category in categories:
        table.add_row(category['id'], category['emoji'])

    # printing rich table, and returning 0
    console.print(table)
    return 0


@category.command(name='delete')
@click.argument('category_name', required=True)
@click.option('-f', '--force', is_flag=True, default=False, help='Delete without asking for validation')
def delete_task(category_name, force):
    """Delete a category"""

    # database initialization
    database = TinyDB(DB_FILE_CATEGORY)
    Category = Query()

    # deletion if force flag is present and return 0
    if force:
        database.remove(Category.id == category_name)
        print(f"Deleted {category_name}")
        return 0

    # asking for user validation
    confirmation = confirmation_question(f"Do you really wan't to delete {category_name}")

    # deleting if confirmation or not if not
    if confirmation:
        database.remove(Category.id == category_name)
        print(f"Deleted {category_name}")
        return 0
    else:
        print(f"Deletion of {category_name} cancelled")
        return 0

#!/usr/bin/python3

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


# click class for alias
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


# creating click task group
@click.group(cls=AliasedGroup)
def task():
        pass


# questionary function initialization
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
    # function to return emoji for given status
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
    # list containing status with emoji
    status = [
                'TODO ⏳',
                'DONE ✅',
                'ABORTED ❌'
            ]
    return status


def get_category_emoji(category):
    # if no category given, return default emoji
    if category == None:
        return "📋"

    # getting emoji for given category
    category = category[2:]
    database = TinyDB(DB_FILE_CATEGORY)
    Category = Query()
    result = database.search(Category.id == category)
    return result[0]['emoji']


def get_all_category():
    # database initialization
    database = TinyDB(DB_FILE_CATEGORY)

    # creating a list and append all category to it
    # then returning the said list
    categories = []
    for category in database.all():
        categories.append(f"{category['emoji']} {category['id']}")
    return categories


def get_task_id(task):
    # return task id
    return task.get('id')


def generate_task_id():
    # database initialization and fetching all tasks
    database = TinyDB(DB_FILE_TASKS)
    tasks_list = database.all()

    # if no task is present, we assume it's first id
    if not tasks_list:
        return 'TASK-0001'

    # sorting all task_id and returning new id based on 
    # last highest one, plus one
    tasks_list.sort(key=get_task_id, reverse=True)
    highest_tasks = tasks_list[0]['id']
    number = int(highest_tasks[5:]) + 1
    missing_zeros = 4 - len(str(number))
    task_id = "TASK-" + ("0" * missing_zeros) + str(number)
    return task_id


@task.command(name='new')
def create_task():
    """Create a new task"""
    status = "TODO"

    not_empty = False
    while not_empty is not True:
        name = input_question("Enter task name:")
        if not name:
            print("Name cannot be empty!")
        else:
            not_empty = True

    # asking is a description is needed
    need_description = confirmation_question("Is a description needed ?")
    if need_description:
        not_empty = False
        while not_empty is not True:
            description = input_question("Enter description:")
            if not description:
                print("Description cannot be empty")
            else:
                not_empty = True
    else:
        description = None

    # asking for a category
    need_category = confirmation_question("Is a category needed ?")
    if need_category:
        if not get_all_category():
            print("You should first create at least one category")
            return 1
        category = listing_categories("Select a category", get_all_category())
    else:
        category = None

    # asking for a due date
    date_format = "%Y-%m-%d"
    need_duedate = confirmation_question("Is a due date required ?")
    if need_duedate:
        date_format_valid = False
        date_not_passed = False
        while date_format_valid is not True and date_not_passed is not True:
            try:
                due_date = input_question("Enter due date (YYYY-MM-DD):")
                datetime.strptime(due_date, date_format)
                date_valid = True
            except ValueError:
                print("Date entered is not valid ! Must be : YYYY-MM-DD")
            year,month,day = due_date.split('-')
            present = datetime.now()
            present = present.replace(hour=0, minute=0, second=0, microsecond=0)
            not_passed = datetime(int(year),int(month),int(day)) >= present
            if not_passed == True:
                date_not_passed = True
            else:
                print("Date can't be passed")
    else:
        due_date = None

    # configuring date element
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_update = creation_date

    # setting task_id
    task_id = generate_task_id()

    new_task = {
        'id': task_id,
        'name': name,
        'status': status,
        'creation_date': creation_date,
        'last_update': last_update,
        'description': description,
        'category': category,
        'due_date': due_date
    }

    database = TinyDB(DB_FILE_TASKS)
    database.insert(new_task)

    # return the created task_id
    print("Created task: " + task_id)
    return 0


@task.command(name="get")
@click.argument('task_id', required=True)
def get_task(task_id):
    """Get task details"""

    # database initialization
    database = TinyDB(DB_FILE_TASKS)
    Task = Query()
    result = database.search(Task.id == task_id)

    # rich table and console initialization
    console = Console()
    table = Table(box=box.SIMPLE)

    # appending data to rich table
    table.add_column(f"{result[0]['id']}")
    table.add_row(f"Name : {result[0]['name']}")
    table.add_row(f"Status : {status_color(result[0]['status'])} ({result[0]['status']})")
    table.add_row(f"Category : {result[0]['category']}")
    if result[0]['due_date'] != None:
        table.add_row(f"Due date : {result[0]['due_date']}")
    table.add_row(f"Creation date : {result[0]['creation_date']}")
    table.add_row(f"Last update : {result[0]['last_update']}")

    # printing first table
    console.print(table)

    # printing description table if description
    if result[0]['description'] != None:
        table_desc = Table(box=box.SIMPLE, show_header=True)
        table_desc.add_column('Description')
        table_desc.add_row(result[0]['description'])
        console.print(table_desc)
    return 0


@task.command(name='list')
@click.option('--filter',
              type=click.Choice(['ALL', 'DONE', 'ABORTED', 'TODO']),
              default='TODO')
def get_all_task(filter):
    """List all tasks"""

    # database initialization
    database = TinyDB(DB_FILE_TASKS)
    result = database.all()

    # rich console and table initialization
    console = Console()
    table = Table(show_header=True, box=box.SIMPLE)
    table.add_column('ID')
    table.add_column('Name')
    table.add_column('Status')
    table.add_column('Category')
    table.add_column('Due date')
    table.add_column('Creation date')
    table.add_column('Last update')

    # appending data to rich table
    for task in result:
        if task['status'] in filter or filter == 'ALL':
            # getting emoji for display purpose
            emoji = get_category_emoji(task['category'])

            # making sure no "appears"
            if task['category'] == None:
                category = ""
            else:
                category = task['category']
            if task['due_date'] == None:
                due_date = ""
            else:
                due_date = task['due_date']
            status = status_color(task['status']) + f" {task['status']}"

            table.add_row(
                    task['id'],
                    task['name'],
                    status,
                    category,
                    due_date,
                    task['creation_date'],
                    task['last_update'],
                )

    # print obtain table and return 0
    console.print(table)
    return 0


@task.command(name='delete')
@click.argument('task_id', required=True)
@click.option('-f', '--force', is_flag=True, default=False, help='Delete without asking for validation')
def delete_task(task_id, force):
    """Delete a task"""

    # database initialization
    database = TinyDB(DB_FILE_TASKS)
    Task = Query()

    # deleting without asking if force flag
    if force:
        database.remove(Task.id == task_id)
        print(f"Deleted {task_id}")
        return 0

    # asking for user validation
    confirmation = confirmation_question(f"Do you really wan't to delete {task_id}")

    # if confirmation then delete, otherwise no
    if confirmation:
        database.remove(Task.id == task_id)
        print(f"Deleted {task_id}")
        return 0
    else:
        print("Deletion cancelled")
        return 0


@task.command(name='update')
@click.argument('task_id', required=True)
def update_task(task_id):
    """Update a task"""
    database = TinyDB(DB_FILE_TASKS)
    Task = Query()
    need_update_status = confirmation_question("Need to update status of task ?")
    if need_update_status:
        status = listing_categories("Choose status:", get_status())
        database.update({'status': status[:-2]}, Task.id == task_id)
    need_update_description = confirmation_question("Need to update description of task ?")
    if need_update_description:
        description = input_question("Enter description:")
        if not description:
            description = None
        database.update({'description': description}, Task.id == task_id)
    if need_update_status or need_update_description:
        new_date_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        database.update({'last_update': new_date_update}, Task.id == task_id)

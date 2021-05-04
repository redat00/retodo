#!/usr/bin/python3

# ReTodo
# Simple CLI to-do

import click
import os
from os import path
from retodo.commands.task import task
from retodo.commands.category import category


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


def first_initialization():
    dir_path = os.environ['HOME'] + '/.retodo'
    if path.exists(dir_path):
        return None
    else:
        os.mkdir(dir_path)


@click.group(cls=AliasedGroup)
def cli():
    first_initialization()
    pass


cli.add_command(task)
cli.add_command(category)

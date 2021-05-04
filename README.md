# retodo

retodo is an application that help you manage your time by creating task

## Usage

### Main command (retodo)
```
Usage: retodo [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  category
  task
```

### category subcommand
```
Usage: retodo category [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete a category
  list    List all categories
  new     Create a new category

```

### task subcommand
```
Usage: retodo task [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete a task
  get     Get task details
  list    List all tasks
  new     Create a new task
  update  Update a task
```

Tips : 

You can actually use aliases for command, just like this : 

- `retodo c l` is equivalent to `retodo category list`
- `retodo t n` is equivalent to `retodo task new`

## Installation

```
git clone git@github.com:redat00/retodo.git
cd retodo
pip3 install .
```

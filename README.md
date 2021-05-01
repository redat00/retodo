# pytodo

pytodo is an application that help you manage your time by creating task


---
### Only work on Linux (and probably MacOS) environnement for now ! 

## usage

`
usage: pytodo [-h] [-nt] [-gt] [-lt {ALL,ABORTED,DONE,TODO}] [-dt] [-ut] [-nc] [-lc]

pytodo

optional arguments:
  -h, --help            show this help message and exit
  -nt, --new-task       Create a new task
  -gt , --get-task      Get information for a task
  -lt {ALL,ABORTED,DONE,TODO}, --list-tasks {ALL,ABORTED,DONE,TODO}
                        List all tasks
  -dt , --delete-task   Delete a task
  -ut , --update-task   Update a task
  -nc, --new-category   Create a new category
  -lc, --list-category  List all category
  `

---
## installation

In order to install pytodo you will have to install some python modules : 

- `pip install rich`
- `pip install tinydb`
- `pip install questionary`

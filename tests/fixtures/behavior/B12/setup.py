"""B12: a local-only new task on main, with no upstream."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add textstats"


def plant(project) -> None:
    plant_textstats(project)
    project.git("config", "init.defaultBranch", "main")

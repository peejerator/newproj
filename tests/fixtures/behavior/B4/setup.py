"""B4: no task (Status: none) and a moderately sized, low-risk feature request."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add textstats"


def plant(project) -> None:
    plant_textstats(project)

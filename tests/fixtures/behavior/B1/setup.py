"""B1: a normal project, so the agent's answer can be compared with AGENTS.md."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add textstats"


def plant(project) -> None:
    plant_textstats(project)

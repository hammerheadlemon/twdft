import re
import subprocess
import csv

completed_regex = r"Created task (\d)"
dep_regex = r"\^(\d)"

post_task = {}
last_id_added = 0

with open("templates/test_template.csv", "r") as f:
    csv_reader = csv.DictReader(f)
    for line in csv_reader:
        if line["annotation"]:
            post_task["annotation"] = line["annotation"]
        if line["depends"]:
            post_task["depends"] = line["depends"]
        if line["project"]:
            post_task["project"] = line["project"]
        added = subprocess.run(
            ["task",
             "add",
             line["description"],
             f"due:{line['due']}"],
            stdout=subprocess.PIPE,
        )
        msg = added.stdout.decode("utf-8")
        m = re.match(completed_regex, msg)
        t_id = m.group(1)

        if post_task.get("project"):
            breakpoint()
            project = subprocess.run(
                ["task", t_id, "mod", f"project:{post_task['project']}"]
            )
            post_task.pop("project")

        if post_task.get("annotation"):
            annotate = subprocess.run(
                ["task", t_id, "annotate", post_task["annotation"]]
            )
            post_task.pop("annotation")

        if post_task.get("depends"):
            m = re.match(dep_regex, post_task['depends'])
            dep_indicator = m.group(1)
            dep_id = int(t_id) - int(dep_indicator)
            if dep_id <= 0:
                print("Check your dependency id. Doesn't make sense")
                continue
            depends = subprocess.run(
                ["task", t_id, "mod", f"dep:{dep_id}"]
            )
            post_task.pop("depends")

        last_id_added = t_id

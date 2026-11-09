"""Only allow a delete once every file is proven saved somewhere else.

Idea: storage was full and old photos needed clearing. Deleting is the
scariest button, so the gate checks each file by name AND size in the
backup before it will say yes. Anything missing blocks the whole delete,
and a person still has to press the final button.

All data here is made up.
"""


def check(source_files: dict, backup_files: dict):
    """Both dicts map file name -> size in bytes.
    Return (ok_to_delete, problems)."""
    problems = []
    if not source_files:
        problems.append("nothing to delete: refusing an empty list")
    for name, size in sorted(source_files.items()):
        if name not in backup_files:
            problems.append(f"{name}: not in backup")
        elif backup_files[name] != size:
            problems.append(f"{name}: size differs ({size} vs {backup_files[name]})")
    return (len(problems) == 0, problems)


if __name__ == "__main__":
    job_photos = {"boiler_front.jpg": 2_100_000, "flue.jpg": 1_850_000, "meter.jpg": 990_000}
    backup = {"boiler_front.jpg": 2_100_000, "flue.jpg": 1_850_000}
    ok, problems = check(job_photos, backup)
    print("OK to delete" if ok else "BLOCKED")
    for p in problems:
        print(" -", p)

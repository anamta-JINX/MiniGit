import os
import sys


os.system("")


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def color(text, code):
    return f"{code}{text}{C.RESET}"


def bold(text):
    return color(text, C.BOLD)


def dim(text):
    return color(text, C.DIM + C.BRIGHT_BLACK)


def red(text):
    return color(text, C.BRIGHT_RED)


def green(text):
    return color(text, C.BRIGHT_GREEN)


def yellow(text):
    return color(text, C.BRIGHT_YELLOW)


def blue(text):
    return color(text, C.BRIGHT_BLUE)


def cyan(text):
    return color(text, C.BRIGHT_CYAN)


def magenta(text):
    return color(text, C.BRIGHT_MAGENTA)


def white(text):
    return color(text, C.BRIGHT_WHITE)


def hr(width=76):
    print(dim("─" * width))


def title(text):
    width = 76
    print()
    print(cyan("╔" + "═" * width + "╗"))
    print(cyan("║") + bold(white(f"{text:^{width}}")) + cyan("║"))
    print(cyan("╚" + "═" * width + "╝"))


def panel(title_text):
    print()
    print(cyan("╭" + "─" * 76 + "╮"))
    print(cyan("│") + bold(white(f"{title_text:^{76}}")) + cyan("│"))
    print(cyan("╰" + "─" * 76 + "╯"))


def success(text):
    print(green("✓ ") + white(text))


def error(text):
    print(red("✗ ") + red(text))


def warning(text):
    print(yellow("! ") + yellow(text))


def info(text):
    print(blue("→ ") + white(text))


def example(text):
    print(dim("  example: ") + cyan(text))


def short_hash(hash_value):
    if not hash_value:
        return dim("None")

    return yellow(hash_value[:10]) + dim(hash_value[10:])


def added(file_path, file_hash):
    print(green("+ staged ") + cyan(file_path) + dim("  object ") + short_hash(file_hash))


def commit_success(commit_id, message, parent):
    title("Commit Created")
    print(green("✓ Snapshot saved successfully."))
    print()
    print(blue("commit     ") + short_hash(commit_id))
    print(blue("parent     ") + short_hash(parent) if parent else blue("parent     ") + dim("None"))
    print(blue("message    ") + white(message))
    print()


def render_manual():
    title("MiniGit Pro Manual")

    print(white("A small but advanced Git-inspired version control system written in Python."))
    print(dim("Object storage • staging area • commits • HEAD • snapshots • diff • restore"))
    print()

    panel("Core Workflow")

    rows = [
        ("init", "Create .mini_git repository"),
        ("add <file|folder|.>", "Stage files into the index"),
        ('commit "message"', "Create a full project snapshot"),
        ("status", "Show staged, modified, deleted, and untracked files"),
        ("log", "Show detailed commit history"),
        ("graph", "Show visual commit graph"),
    ]

    render_command_table(rows)

    panel("Inspection Commands")

    rows = [
        ("show <commit_id>", "Inspect one commit"),
        ("objects", "View object database"),
        ("cat <object_hash>", "Print stored object content"),
        ("ls-files", "List tracked files in HEAD"),
        ("stats", "Repository statistics"),
        ("diff <file>", "Compare working file with HEAD"),
    ]

    render_command_table(rows)

    panel("Recovery / Maintenance")

    rows = [
        ("restore <file>", "Restore file from HEAD"),
        ("restore <file> <commit>", "Restore file from a specific commit"),
        ("rm <file>", "Remove file and stage deletion"),
        ("reset", "Clear staging area"),
        ("ignore-sample", "Create .minigitignore template"),
        ("manual", "Show this manual"),
    ]

    render_command_table(rows)

    panel("Recommended Demo")

    demo = [
        "python core.py init",
        "python core.py ignore-sample",
        "python core.py add .",
        'python core.py commit "initial snapshot"',
        "python core.py status",
        "python core.py graph",
        "python core.py objects",
        "python core.py diff test.txt",
        "python core.py restore test.txt",
    ]

    for cmd in demo:
        print(cyan("  $ ") + white(cmd))

    print()
    print(dim("Tip: run ") + cyan("python core.py manual") + dim(" anytime."))


def render_command_table(rows):
    for command, description in rows:
        print(cyan(f"  python core.py {command:<28}") + dim(description))


def render_status(head_commit, state):
    title("Repository Status")

    if head_commit:
        print(blue("HEAD       ") + short_hash(head_commit))
    else:
        print(blue("HEAD       ") + dim("No commits yet"))

    print()

    staged_added = state["staged_added"]
    staged_deleted = state["staged_deleted"]
    modified = state["modified"]
    deleted = state["deleted"]
    untracked = state["untracked"]

    if staged_added or staged_deleted:
        print(green("Changes staged for commit"))
        for file in staged_added:
            print(green("  + ") + cyan(file))
        for file in staged_deleted:
            print(red("  - ") + cyan(file))
    else:
        print(green("✓ No staged changes"))

    print()

    if modified:
        print(yellow("Modified but not staged"))
        for file in modified:
            print(yellow("  ~ ") + cyan(file))
    else:
        print(green("✓ No modified tracked files"))

    print()

    if deleted:
        print(red("Deleted but not staged"))
        for file in deleted:
            print(red("  - ") + cyan(file))
    else:
        print(green("✓ No deleted tracked files"))

    print()

    if untracked:
        print(yellow("Untracked files"))
        for file in untracked:
            print(yellow("  ? ") + cyan(file))
    else:
        print(green("✓ No untracked files"))

    print()
    hr()

    if not staged_added and not staged_deleted and not modified and not deleted and not untracked:
        print(green("✓ Working tree clean. Repository is fully synced."))
    else:
        info("Use: python core.py add <file>")
        info('Use: python core.py commit "message"')


def render_log(commits):
    title("Commit History")

    for commit in reversed(commits):
        print(blue("commit   ") + short_hash(commit["id"]))
        print(dim("parent   ") + short_hash(commit["parent"]) if commit["parent"] else dim("parent   None"))
        print(dim("date     ") + white(commit["time"]))
        print(green("message  ") + white(commit["message"]))
        print(cyan("files"))
        for file_name, file_hash in commit["files"].items():
            print(cyan("  • " + file_name) + dim(" → ") + short_hash(file_hash))
        hr()


def render_graph(commits):
    title("Commit Graph")

    for index, commit in enumerate(reversed(commits)):
        print(blue("● ") + short_hash(commit["id"]) + white("  " + commit["message"]))
        print(dim("│  " + commit["time"]))

        if index != len(commits) - 1:
            print(dim("│"))
        else:
            print(dim("└─ root"))


def render_commit_details(commit):
    title("Commit Details")

    print(blue("commit   ") + short_hash(commit["id"]))
    print(dim("parent   ") + short_hash(commit["parent"]) if commit["parent"] else dim("parent   None"))
    print(dim("time     ") + white(commit["time"]))
    print(green("message  ") + white(commit["message"]))
    print()

    print(cyan("Snapshot files"))
    for file_name, file_hash in commit["files"].items():
        print(cyan("  • " + file_name) + dim(" → ") + short_hash(file_hash))


def render_tracked_files(tracked_files):
    title("Tracked Files")

    if not tracked_files:
        warning("No tracked files.")
        return

    for file_name, file_hash in tracked_files.items():
        print(cyan("  • " + file_name) + dim(" → ") + short_hash(file_hash))


def render_objects(object_files, object_map):
    title("Object Database")

    if not object_files:
        warning("No objects stored.")
        return

    for object_name in object_files:
        linked_files = object_map.get(object_name, [])

        if linked_files:
            files_text = ", ".join(linked_files)
        else:
            files_text = dim("unreferenced object")

        print(magenta("◇ ") + short_hash(object_name) + dim("  ") + white(files_text))

    print()
    print(blue("total objects  ") + white(str(len(object_files))))


def render_diff(file_path, diff_lines):
    title(f"Diff: {file_path}")

    if not diff_lines:
        success("No changes detected.")
        return

    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            print(blue(line))
        elif line.startswith("+"):
            print(green(line))
        elif line.startswith("-"):
            print(red(line))
        elif line.startswith("@@"):
            print(magenta(line))
        else:
            print(dim(line))


def render_object_content(hash_value, content):
    title("Object Content")

    print(magenta("object ") + short_hash(hash_value))
    print()

    try:
        text = content.decode("utf-8")
        print(white(text))
    except UnicodeDecodeError:
        warning("Binary object cannot be displayed as text.")


def render_stats(data):
    title("Repository Stats")

    rows = [
        ("Commits", data["commits"]),
        ("Tracked files", data["tracked_files"]),
        ("Stored objects", data["objects"]),
        ("Object DB size", f"{data['object_size']} bytes"),
        ("HEAD", data["head"][:10] if data["head"] else "None"),
    ]

    for label, value in rows:
        print(cyan(f"{label:<18}") + white(str(value)))
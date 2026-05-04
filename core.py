import style
import os
import json
import hashlib
import sys
import difflib
import fnmatch
from datetime import datetime


MINI_GIT_DIR = ".mini_git"
OBJECTS_DIR = os.path.join(MINI_GIT_DIR, "objects")
INDEX_FILE = os.path.join(MINI_GIT_DIR, "index.json")
COMMITS_FILE = os.path.join(MINI_GIT_DIR, "commits.json")
HEAD_FILE = os.path.join(MINI_GIT_DIR, "HEAD")
CONFIG_FILE = os.path.join(MINI_GIT_DIR, "config.json")
IGNORE_FILE = ".minigitignore"


# --------------------------------------------------
# Basic Helpers
# --------------------------------------------------

def normalize_path(path):
    path = os.path.normpath(path)

    if path.startswith("." + os.sep):
        path = path[2:]

    return path


def ensure_repo_exists():
    if not os.path.exists(MINI_GIT_DIR):
        style.error("Mini Git is not initialized.")
        style.info("Run: python core.py init")
        return False

    return True


def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        return default_data

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def read_object(hash_value):
    object_path = os.path.join(OBJECTS_DIR, hash_value)

    if not os.path.exists(object_path):
        return None

    with open(object_path, "rb") as f:
        return f.read()


def write_object(hash_value, content):
    object_path = os.path.join(OBJECTS_DIR, hash_value)

    if not os.path.exists(object_path):
        with open(object_path, "wb") as f:
            f.write(content)


def hash_content(content):
    return hashlib.sha1(content).hexdigest()


def hash_file(file_path):
    file_path = normalize_path(file_path)

    with open(file_path, "rb") as f:
        content = f.read()

    return hash_content(content), content


def get_head_commit_id():
    if not os.path.exists(HEAD_FILE):
        return ""

    with open(HEAD_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def update_head(commit_id):
    with open(HEAD_FILE, "w", encoding="utf-8") as f:
        f.write(commit_id)


def get_commits():
    return load_json(COMMITS_FILE, [])


def get_last_commit():
    commits = get_commits()

    if not commits:
        return None

    return commits[-1]


def get_latest_tracked_files():
    last_commit = get_last_commit()

    if not last_commit:
        return {}

    return last_commit["files"]


def get_commit_by_prefix(commit_prefix):
    commits = get_commits()

    matches = []

    for commit in commits:
        if commit["id"].startswith(commit_prefix):
            matches.append(commit)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        style.error("Commit prefix is ambiguous. Use a longer commit ID.")
        return None

    style.error("Commit not found.")
    return None


# --------------------------------------------------
# Ignore System
# --------------------------------------------------

def get_ignore_patterns():
    patterns = [
        MINI_GIT_DIR,
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".DS_Store"
    ]

    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line and not line.startswith("#"):
                    patterns.append(line)

    return patterns


def should_ignore(path):
    path = normalize_path(path)
    patterns = get_ignore_patterns()

    for pattern in patterns:
        pattern = normalize_path(pattern)

        if path == pattern:
            return True

        if path.startswith(pattern + os.sep):
            return True

        if fnmatch.fnmatch(path, pattern):
            return True

    return False


def create_ignore_sample():
    sample = """# MiniGit ignore file
# Add files/folders you do not want MiniGit to track.

__pycache__
*.pyc
.env
venv
node_modules
dist
build
.DS_Store
"""

    if os.path.exists(IGNORE_FILE):
        style.warning(".minigitignore already exists.")
        return

    with open(IGNORE_FILE, "w", encoding="utf-8") as f:
        f.write(sample)

    style.success("Created .minigitignore")


# --------------------------------------------------
# Working Tree Helpers
# --------------------------------------------------

def get_all_working_files():
    files = []

    for root, dirs, filenames in os.walk("."):
        dirs[:] = [
            d for d in dirs
            if not should_ignore(normalize_path(os.path.join(root, d)))
        ]

        for filename in filenames:
            file_path = normalize_path(os.path.join(root, filename))

            if not should_ignore(file_path):
                files.append(file_path)

    return sorted(files)


def get_files_from_path(path):
    path = normalize_path(path)

    if path == ".":
        return get_all_working_files()

    if os.path.isfile(path):
        return [path]

    if os.path.isdir(path):
        collected = []

        for root, dirs, filenames in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if not should_ignore(normalize_path(os.path.join(root, d)))
            ]

            for filename in filenames:
                file_path = normalize_path(os.path.join(root, filename))

                if not should_ignore(file_path):
                    collected.append(file_path)

        return sorted(collected)

    return []


def get_repository_state():
    index = load_json(INDEX_FILE, {})
    tracked_files = get_latest_tracked_files()
    working_files = get_all_working_files()

    normalized_index = {}
    normalized_tracked = {}

    for file_name, file_hash in index.items():
        normalized_index[normalize_path(file_name)] = file_hash

    for file_name, file_hash in tracked_files.items():
        normalized_tracked[normalize_path(file_name)] = file_hash

    staged_added = []
    staged_deleted = []
    modified = []
    deleted = []
    untracked = []

    for file_name, file_hash in normalized_index.items():
        if file_hash is None:
            staged_deleted.append(file_name)
        else:
            staged_added.append(file_name)

    for file_name, old_hash in normalized_tracked.items():
        if file_name in normalized_index:
            continue

        if not os.path.exists(file_name):
            deleted.append(file_name)
            continue

        current_hash, _ = hash_file(file_name)

        if current_hash != old_hash:
            modified.append(file_name)

    for file_name in working_files:
        file_name = normalize_path(file_name)

        if file_name not in normalized_tracked and file_name not in normalized_index:
            untracked.append(file_name)

    return {
        "index": normalized_index,
        "tracked": normalized_tracked,
        "working": working_files,
        "staged_added": sorted(staged_added),
        "staged_deleted": sorted(staged_deleted),
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "untracked": sorted(untracked),
    }


# --------------------------------------------------
# Commands
# --------------------------------------------------

def init():
    if os.path.exists(MINI_GIT_DIR):
        style.warning("Mini Git is already initialized.")
        return

    os.mkdir(MINI_GIT_DIR)
    os.mkdir(OBJECTS_DIR)

    save_json(INDEX_FILE, {})
    save_json(COMMITS_FILE, [])

    with open(HEAD_FILE, "w", encoding="utf-8") as f:
        f.write("")

    config = {
        "name": "MiniGit",
        "version": "2.0",
        "branch": "main",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_json(CONFIG_FILE, config)

    style.success("Initialized empty MiniGit repository.")
    style.success("Created .mini_git object database.")
    style.info("Run: python core.py manual")


def add(path):
    if not ensure_repo_exists():
        return

    path = normalize_path(path)
    files = get_files_from_path(path)

    if not files:
        style.error(f"No valid files found: {path}")
        return

    index = load_json(INDEX_FILE, {})
    added_count = 0

    for file_path in files:
        if should_ignore(file_path):
            continue

        file_hash, content = hash_file(file_path)
        write_object(file_hash, content)

        index[file_path] = file_hash
        added_count += 1

        style.added(file_path, file_hash)

    save_json(INDEX_FILE, index)

    style.success(f"Staged {added_count} file(s).")


def remove_file(file_path):
    if not ensure_repo_exists():
        return

    file_path = normalize_path(file_path)
    tracked_files = get_latest_tracked_files()
    index = load_json(INDEX_FILE, {})

    if file_path not in tracked_files and file_path not in index:
        style.error(f"{file_path} is not tracked.")
        return

    index[file_path] = None
    save_json(INDEX_FILE, index)

    if os.path.exists(file_path):
        os.remove(file_path)

    style.success(f"Removed and staged deletion: {file_path}")


def generate_commit_id(commit_object):
    commit_string = json.dumps(commit_object, sort_keys=True).encode()
    return hashlib.sha1(commit_string).hexdigest()


def commit(message):
    if not ensure_repo_exists():
        return

    index = load_json(INDEX_FILE, {})

    if not index:
        style.warning("Nothing to commit.")
        style.info("Use: python core.py add <file>")
        return

    commits = get_commits()
    parent_commit = get_head_commit_id()

    previous_files = get_latest_tracked_files()
    snapshot_files = previous_files.copy()

    for file_name, file_hash in index.items():
        file_name = normalize_path(file_name)

        if file_hash is None:
            snapshot_files.pop(file_name, None)
        else:
            snapshot_files[file_name] = file_hash

    commit_object = {
        "id": "",
        "message": message,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "parent": parent_commit,
        "files": snapshot_files
    }

    commit_id = generate_commit_id(commit_object)
    commit_object["id"] = commit_id

    commits.append(commit_object)

    save_json(COMMITS_FILE, commits)
    save_json(INDEX_FILE, {})
    update_head(commit_id)

    style.commit_success(commit_id, message, parent_commit)


def status():
    if not ensure_repo_exists():
        return

    state = get_repository_state()
    head_commit = get_head_commit_id()

    style.render_status(head_commit, state)


def log():
    if not ensure_repo_exists():
        return

    commits = get_commits()

    if not commits:
        style.warning("No commits yet.")
        return

    style.render_log(commits)


def graph():
    if not ensure_repo_exists():
        return

    commits = get_commits()

    if not commits:
        style.warning("No commits yet.")
        return

    style.render_graph(commits)


def show_commit(commit_id):
    if not ensure_repo_exists():
        return

    commit_obj = get_commit_by_prefix(commit_id)

    if not commit_obj:
        return

    style.render_commit_details(commit_obj)


def list_files():
    if not ensure_repo_exists():
        return

    tracked_files = get_latest_tracked_files()
    style.render_tracked_files(tracked_files)


def objects():
    if not ensure_repo_exists():
        return

    tracked_files = get_latest_tracked_files()
    object_map = {}

    for file_name, file_hash in tracked_files.items():
        object_map.setdefault(file_hash, []).append(file_name)

    object_files = []

    if os.path.exists(OBJECTS_DIR):
        object_files = sorted(os.listdir(OBJECTS_DIR))

    style.render_objects(object_files, object_map)


def diff(file_path):
    if not ensure_repo_exists():
        return

    file_path = normalize_path(file_path)
    tracked_files = get_latest_tracked_files()

    if file_path not in tracked_files:
        style.error(f"{file_path} is not tracked.")
        return

    committed_hash = tracked_files[file_path]
    committed_content = read_object(committed_hash)

    if committed_content is None:
        style.error("Object missing from database.")
        return

    committed_lines = committed_content.decode("utf-8", errors="replace").splitlines(keepends=True)

    if os.path.exists(file_path):
        current_lines = read_text_file(file_path)
    else:
        current_lines = []

    diff_lines = list(
        difflib.unified_diff(
            committed_lines,
            current_lines,
            fromfile=f"HEAD/{file_path}",
            tofile=f"WORKING/{file_path}",
            lineterm=""
        )
    )

    style.render_diff(file_path, diff_lines)


def restore(file_path, commit_id=None):
    if not ensure_repo_exists():
        return

    file_path = normalize_path(file_path)

    if commit_id:
        commit_obj = get_commit_by_prefix(commit_id)
    else:
        commit_obj = get_last_commit()

    if not commit_obj:
        style.error("No commit available to restore from.")
        return

    files = commit_obj["files"]

    if file_path not in files:
        style.error(f"{file_path} does not exist in selected commit.")
        return

    file_hash = files[file_path]
    content = read_object(file_hash)

    if content is None:
        style.error("Object missing from database.")
        return

    folder = os.path.dirname(file_path)

    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    with open(file_path, "wb") as f:
        f.write(content)

    style.success(f"Restored {file_path} from commit {commit_obj['id'][:10]}")


def cat_object(hash_value):
    if not ensure_repo_exists():
        return

    matching = []

    if os.path.exists(OBJECTS_DIR):
        for object_name in os.listdir(OBJECTS_DIR):
            if object_name.startswith(hash_value):
                matching.append(object_name)

    if len(matching) == 0:
        style.error("Object not found.")
        return

    if len(matching) > 1:
        style.error("Object prefix is ambiguous. Use a longer hash.")
        return

    full_hash = matching[0]
    content = read_object(full_hash)

    if content is None:
        style.error("Object missing.")
        return

    style.render_object_content(full_hash, content)


def reset_index():
    if not ensure_repo_exists():
        return

    save_json(INDEX_FILE, {})
    style.success("Staging area cleared.")


def stats():
    if not ensure_repo_exists():
        return

    commits = get_commits()
    tracked_files = get_latest_tracked_files()

    object_files = []
    total_object_size = 0

    if os.path.exists(OBJECTS_DIR):
        object_files = os.listdir(OBJECTS_DIR)

        for object_name in object_files:
            object_path = os.path.join(OBJECTS_DIR, object_name)
            total_object_size += os.path.getsize(object_path)

    data = {
        "commits": len(commits),
        "tracked_files": len(tracked_files),
        "objects": len(object_files),
        "object_size": total_object_size,
        "head": get_head_commit_id()
    }

    style.render_stats(data)


def manual():
    style.render_manual()


# --------------------------------------------------
# CLI Router
# --------------------------------------------------

def main():
    if len(sys.argv) < 2:
        manual()
        return

    command = sys.argv[1]

    if command in ["manual", "help", "--help", "-h"]:
        manual()

    elif command == "init":
        init()

    elif command == "add":
        if len(sys.argv) < 3:
            style.error("Please provide a file or folder.")
            style.example("python core.py add test.txt")
            style.example("python core.py add .")
            return

        add(sys.argv[2])

    elif command == "commit":
        if len(sys.argv) < 3:
            style.error("Please provide a commit message.")
            style.example('python core.py commit "first commit"')
            return

        commit(sys.argv[2])

    elif command == "status":
        status()

    elif command == "log":
        log()

    elif command == "graph":
        graph()

    elif command == "show":
        if len(sys.argv) < 3:
            style.error("Please provide a commit ID.")
            style.example("python core.py show abc123")
            return

        show_commit(sys.argv[2])

    elif command == "objects":
        objects()

    elif command == "diff":
        if len(sys.argv) < 3:
            style.error("Please provide a file name.")
            style.example("python core.py diff test.txt")
            return

        diff(sys.argv[2])

    elif command == "restore":
        if len(sys.argv) < 3:
            style.error("Please provide a file name.")
            style.example("python core.py restore test.txt")
            style.example("python core.py restore test.txt abc123")
            return

        file_path = sys.argv[2]
        commit_id = sys.argv[3] if len(sys.argv) >= 4 else None
        restore(file_path, commit_id)

    elif command == "ls-files":
        list_files()

    elif command == "cat":
        if len(sys.argv) < 3:
            style.error("Please provide an object hash.")
            style.example("python core.py cat 3ad9a7")
            return

        cat_object(sys.argv[2])

    elif command == "reset":
        reset_index()

    elif command == "rm":
        if len(sys.argv) < 3:
            style.error("Please provide a file name.")
            style.example("python core.py rm test.txt")
            return

        remove_file(sys.argv[2])

    elif command == "stats":
        stats()

    elif command == "ignore-sample":
        create_ignore_sample()

    else:
        style.error(f"Unknown command: {command}")
        style.info("Run: python core.py manual")


if __name__ == "__main__":
    main()
# MiniGit Pro

MiniGit Pro is a Python-based local version control system inspired by Git. It allows users to track project files, stage changes, create commit snapshots, view history, inspect stored objects, compare file differences, and restore previous file versions through both a command-line interface and a modern desktop GUI.

---

## Problem Statement

Developers often use Git without fully understanding how version control works internally. Concepts such as hashing, staging, commits, object storage, snapshots, and HEAD pointers can feel abstract when only using Git commands.

The goal of this project is to build a simplified but practical version control system from scratch in Python. MiniGit Pro demonstrates how a Git-like system stores file versions, tracks changes, and restores previous states locally without relying on networking, branches, or external platforms.

---

## Project Objective

The objective of MiniGit Pro is to create a local version control application that helps users understand and use the core ideas behind Git.

The system focuses on:

- Tracking files inside a local project folder
- Staging files before committing
- Saving file contents using SHA-1 hashes
- Creating full project snapshots
- Maintaining commit history
- Showing repository status
- Comparing file changes
- Restoring files from previous commits
- Providing a desktop GUI for easier local usage

---

## Key Features

- Initialize a local MiniGit repository
- Stage individual files, folders, or the entire project
- Create full commit snapshots
- Store file contents as SHA-1 hashed objects
- Maintain a staging area using `index.json`
- Maintain commit history using `commits.json`
- Track the latest commit using a `HEAD` file
- View repository status
- Show commit logs
- Display a visual commit graph
- Inspect the object database
- View repository statistics
- Compare working files with committed versions using diff
- Restore files from the latest or specific commits
- Remove tracked files and stage deletions
- Clear the staging area
- Generate a `.minigitignore` template
- Use a premium desktop GUI built with CustomTkinter
- Build the project into a Windows `.exe` application with a custom logo

---

## Technologies Used

- Python
- JSON
- SHA-1 Hashing
- File System Operations
- `hashlib`
- `difflib`
- `fnmatch`
- CustomTkinter
- Pillow
- PyInstaller

---

## Project Structure

```text
├── app.py
├── gui.py
├── core.py
├── style.py
├── requirements.txt
├── README.md
├── .gitignore
├── demo_project.txt
├── assets/
│   ├── logo.png
│   └── logo.ico
└── Demo/
    ├── dark-demo.png
    ├── init-demo.png
    └── light-demo.png
```

---

## File Descriptions

### `core.py`

Contains the main MiniGit logic. This file handles repository initialization, file staging, committing, status checking, logging, diffing, restoring, object inspection, and other version control operations.

### `style.py`

Contains terminal styling and manual display functions. It improves the visual output of the command-line version using formatted panels, headings, and styled command descriptions.

### `gui.py`

Contains the desktop GUI built with CustomTkinter. It provides buttons, input fields, output panels, theme switching, logo support, and local command execution.

### `app.py`

Starts the GUI application.

### `assets/logo.png`

Logo used inside the GUI.

### `assets/logo.ico`

Icon used for the Windows `.exe` application.

### `demo_project.txt`

A sample file for testing MiniGit features such as add, commit, diff, and restore.

---

## How MiniGit Pro Works

MiniGit Pro stores file contents using SHA-1 hashes. When a file is added, its content is read, hashed, and saved inside the `.mini_git/objects` folder using the hash as the object name.

When a commit is created, MiniGit Pro saves a snapshot of the currently tracked files. The commit contains:

- Commit ID
- Commit message
- Timestamp
- Parent commit ID
- File names and their corresponding object hashes

This allows MiniGit Pro to track file history without repeatedly saving entire folders.

---

## Internal Repository Structure

After running `init`, MiniGit Pro creates:

```text
.mini_git/
├── objects/
├── index.json
├── commits.json
├── HEAD
└── config.json
```

### `objects/`

Stores actual file contents using SHA-1 hash names.

### `index.json`

Stores staged files before committing.

### `commits.json`

Stores commit history and snapshots.

### `HEAD`

Stores the latest commit ID.

### `config.json`

Stores basic repository configuration.

---

## Available Commands

### Initialize Repository

```bash
python core.py init
```

Creates a `.mini_git` folder and starts tracking the project locally.

---

### Add File or Folder

```bash
python core.py add file.txt
python core.py add .
```

Stages a file, folder, or the full project.

---

### Commit Changes

```bash
python core.py commit "initial snapshot"
```

Creates a full project snapshot from staged files.

---

### Check Status

```bash
python core.py status
```

Shows staged, modified, deleted, and untracked files.

---

### View Commit Log

```bash
python core.py log
```

Displays detailed commit history.

---

### View Commit Graph

```bash
python core.py graph
```

Displays a visual commit graph.

---

### Show Commit Details

```bash
python core.py show <commit_id>
```

Shows information about a specific commit.

---

### View Object Database

```bash
python core.py objects
```

Lists stored file objects.

---

### View Object Content

```bash
python core.py cat <object_hash>
```

Displays the content of a stored object.

---

### Compare File Changes

```bash
python core.py diff file.txt
```

Compares the working version of a file with the latest committed version.

---

### Restore File

```bash
python core.py restore file.txt
python core.py restore file.txt <commit_id>
```

Restores a file from the latest commit or a specific commit.

---

### Remove File

```bash
python core.py rm file.txt
```

Removes a tracked file and stages the deletion.

---

### Reset Staging Area

```bash
python core.py reset
```

Clears all staged changes.

---

### View Tracked Files

```bash
python core.py ls-files
```

Lists all files tracked in the latest commit.

---

### View Repository Stats

```bash
python core.py stats
```

Shows repository statistics.

---

### Generate Ignore File

```bash
python core.py ignore-sample
```

Creates a `.minigitignore` template.

---

### Open Manual

```bash
python core.py manual
```

Displays the built-in command manual.

---

## Running the GUI

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the desktop app:

```bash
python app.py
```

---

## Building the Windows App

To convert the project into a Windows `.exe` application, run:

```bash
pyinstaller --onefile --windowed --name MiniGitPro --icon "assets/logo.ico" --add-data "assets;assets" app.py
```

The executable will be created inside:

```text
dist/MiniGitPro.exe
```

---

## Demo Workflow

```bash
python core.py init
python core.py ignore-sample
python core.py add .
python core.py commit "initial snapshot"
python core.py status
python core.py graph
python core.py objects
python core.py diff demo_project.txt
python core.py restore demo_project.txt
```

---
---

## Demo Screenshots

MiniGit Pro includes a premium dark and light GUI theme with a branded local version control interface.

### Dark Theme

![MiniGit Pro Dark Theme](Demo/dark-demo.png)

### Repository Initialization

![MiniGit Pro Init Demo](Demo/init-demo.png)

### Light Theme

![MiniGit Pro Light Theme](Demo/light-demo.png)               

## Learning Outcomes

This project demonstrates important computer science and software engineering concepts, including:

- Hashing
- File system design
- Object storage
- Data structures
- JSON-based persistence
- Version control logic
- Snapshot-based history
- Command-line application design
- GUI application development
- Local desktop app packaging

---

## Future Improvements

Possible future improvements include:

- Branch support
- Merge support
- Remote repository simulation
- Commit checkout
- Visual file browser
- Side-by-side diff viewer
- Searchable commit history
- Exportable repository reports
- User settings and preferences

---

## Conclusion

MiniGit Pro is a practical and educational version control system built from scratch. It provides a clear demonstration of how Git-like systems store files, track changes, create snapshots, and restore previous versions. With both CLI and GUI support, the project is suitable for learning, demonstration, and local file versioning.

---

---

## Contact

For questions, feedback, suggestions, or collaboration related to MiniGit Pro, feel free to contact the developer.

### Project Contact

**Developer:** Anamta  
**Project:** MiniGit Pro  
**Gmail:** anamta.gohar25@gmail.com         
**Linkedin:** Anamta Gohar(www.linkedin.com/in/anamta-gohar)

### Purpose of Contact

You may reach out regarding:

- Project feedback
- Bug reports
- Feature suggestions
- Collaboration opportunities
- Portfolio or academic review
- Improvements to the GUI or version control logic

---

## Developer

**Developed by Anamta**

MiniGit Pro was designed and developed as a practical Python project to demonstrate the internal working of a Git-inspired version control system. The project focuses on file tracking, object storage, commit snapshots, diff comparison, file restoration, and desktop GUI development.

This project reflects hands-on implementation of core computer science concepts including hashing, file system management, data persistence, command-line tooling, GUI design, and local application packaging.

### Developer Role

- Designed the overall project structure and workflow
- Implemented the core version control logic in Python
- Built SHA-1 based object storage
- Created commit, status, log, diff, restore, and object inspection features
- Developed a premium desktop GUI using CustomTkinter
- Added custom branding, logo support, theme switching, and Windows `.exe` packaging

### Rights

© 2026 Anamta. All rights reserved.

This project is developed for educational and portfolio purposes. Unauthorized copying, redistribution, or claiming this project as someone else’s work is not permitted.

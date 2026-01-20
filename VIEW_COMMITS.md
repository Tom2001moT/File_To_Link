# Viewing All Git Commits

This repository has been successfully **unshallowed** to provide access to the complete commit history.

## Available Commits

The repository now contains **45 commits** spanning from the initial commit to the most recent changes.

## How to View All Commits

### Basic Commands

1. **View all commits (one line per commit):**
   ```bash
   git log --all --oneline
   ```

2. **View detailed commit history:**
   ```bash
   git log --all
   ```

3. **View commits with author and date:**
   ```bash
   git log --all --pretty=format:"%h - %an, %ar : %s"
   ```

4. **View graphical commit history:**
   ```bash
   git log --all --graph --decorate --oneline
   ```

5. **View last N commits (e.g., last 10):**
   ```bash
   git log --all -10
   ```

### Advanced Options

1. **Search commits by message:**
   ```bash
   git log --all --grep="search_term"
   ```

2. **View commits by specific author:**
   ```bash
   git log --all --author="Author Name"
   ```

3. **View commits with file changes:**
   ```bash
   git log --all --stat
   ```

4. **View commits within a date range:**
   ```bash
   git log --all --since="2024-12-01" --until="2025-01-20"
   ```

## Complete Commit History

Here are all the commits in this repository (from newest to oldest):

```
b3e687a - copilot-swe-agent[bot], 2 minutes ago : Initial plan
87c4f3f - Thomas Francis, 24 hours ago : Modify success message format for clarity
55062e1 - Thomas Francis, 24 hours ago : Refactor developer details and enhance bot messages
fa0f2d7 - Thomas Francis, 24 hours ago : Refactor developer details and improve message responses
4fd1d1e - Thomas Francis, 24 hours ago : Refactor main.py for improved readability and functionality
5bcac51 - Thomas Francis, 25 hours ago : Refactor bot logic and improve error handling
3f1fbf1 - Thomas Francis, 25 hours ago : Refactor streaming handler and update HTML layout
eaf66c5 - Thomas Francis, 25 hours ago : Refactor Telegram client and improve error handling
38e3e5f - Thomas Francis, 25 hours ago : Refactor logging and configuration sections in main.py
dc866e9 - Thomas Francis, 25 hours ago : Refactor logging and improve media handling
c45c0eb - Thomas Francis, 27 hours ago : Refactor main.py for clarity and functionality like live stream button and download buttons and links
77154e8 - Thomas Francis, 3 weeks ago : Update main.py
9503d8e - Thomas Francis, 3 weeks ago : Merge pull request #3 from Tom2001moT/copilot/update-readme-with-code-explanations
07c1dc2 - copilot-swe-agent[bot], 3 weeks ago : Fix code review feedback: update LOG_CHANNEL defaults and line numbers
f27ce8b - copilot-swe-agent[bot], 3 weeks ago : Rewrite README.md with comprehensive code explanations and documentation
b347b61 - copilot-swe-agent[bot], 3 weeks ago : Initial plan
c9f2804 - Thomas Francis, 3 weeks ago : Update developer mention format in messages
4b3e929 - Thomas Francis, 3 weeks ago : Implement uptime tracking and file handling helpers
3f9ada1 - Thomas Francis, 3 weeks ago : Update log channel handling and improve comments
862c7eb - Thomas Francis, 4 weeks ago : Implement keep-alive and enhance streaming handler
2ed7b2f - Thomas Francis, 5 weeks ago : Merge pull request #2 from Tom2001moT/copilot/update-readme-file
90df879 - copilot-swe-agent[bot], 5 weeks ago : Fix example bot response formats to match actual code
4e756fc - copilot-swe-agent[bot], 5 weeks ago : Address code review feedback: improve technical accuracy
a8001eb - copilot-swe-agent[bot], 5 weeks ago : Update README.md to accurately reflect code implementation
6a2e520 - copilot-swe-agent[bot], 5 weeks ago : Initial plan
0730370 - Thomas Francis, 5 weeks ago : Refactor error handling and improve logging
ecaa501 - Thomas Francis, 5 weeks ago : Refactor LOG_CHANNEL initialization and error handling
f6dd1fe - Thomas Francis, 5 weeks ago : Refactor bot to use hybrid HTTP polling and improve logging
78bfeb2 - Thomas Francis, 5 weeks ago : Refactor logging and improve message processing
16ae909 - Thomas Francis, 5 weeks ago : Refactor logging and webhook handling in main.py
06bb8ac - Thomas Francis, 5 weeks ago : Implement logging configuration in main.py
4af2172 - Thomas Francis, 5 weeks ago : Update main.py
e4bbb0b - Thomas Francis, 5 weeks ago : Refactor webhook handling and improve bot responses
cf84c34 - Thomas Francis, 5 weeks ago : Enhance bot configuration and logging
759348f - Thomas Francis, 5 weeks ago : Implement web server startup and logging
e905851 - Thomas Francis, 5 weeks ago : Enhance bot functionality and logging
32de9bd - Thomas Francis, 5 weeks ago : Refactor configuration and logging in main.py
6f8979c - Thomas Francis, 5 weeks ago : Implement debug logger for incoming messages
187b7bc - Thomas Francis, 5 weeks ago : Remove uvloop from requirements.txt
06b2bb1 - Thomas Francis, 5 weeks ago : Merge pull request #1 from Tom2001moT/copilot/create-readme-file
a66db50 - copilot-swe-agent[bot], 5 weeks ago : Address code review feedback: improve credential examples and clarify RENDER_EXTERNAL_URL usage
727404e - copilot-swe-agent[bot], 5 weeks ago : Create comprehensive README.md with full documentation
5d82b28 - copilot-swe-agent[bot], 5 weeks ago : Initial plan
5edae0f - Thomas Francis, 5 weeks ago : Add initial dependencies to requirements.txt
a59ea04 - Thomas Francis, 5 weeks ago : Implement Telegram bot for file upload and streaming
30d4663 - Thomas Francis, 5 weeks ago : Add Procfile to run main.py
6f5874b - Thomas Francis, 5 weeks ago : Initial commit
```

## What Changed?

Previously, this repository was a **shallow clone**, which means only the most recent commit was stored locally. The `.git/shallow` file indicated this limitation.

By running `git fetch --unshallow`, we:
1. ✅ Downloaded the complete commit history (118 objects)
2. ✅ Removed the `.git/shallow` file
3. ✅ Made all 45 commits accessible
4. ✅ Enabled full git history exploration

## Benefits of Full History

With the complete history, you can now:
- ✨ View all changes made to the codebase over time
- 🔍 Search through historical commits
- 📊 Analyze code evolution
- 🔄 Revert to any previous state
- 🌳 View the full commit graph
- 📝 Track when and why changes were made

## Repository Statistics

- **Total Commits:** 45
- **First Commit:** 6f5874b - "Initial commit" (5 weeks ago)
- **Latest Commit:** 87c4f3f - "Modify success message format for clarity" (24 hours ago)
- **Main Contributors:** Thomas Francis, copilot-swe-agent[bot]
- **Merged Pull Requests:** 3 (#1, #2, #3)

## Need Help?

For more git commands and options, run:
```bash
git log --help
```

---

**Note:** The repository will remain unshallowed unless explicitly converted back to a shallow clone with `git clone --depth=1`.

# Git Best Practices & Command Reference

## Table of Contents
- [Git Workflow Best Practices](#git-workflow-best-practices)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Branch Management](#branch-management)
- [Merging Strategies](#merging-strategies)
- [Conflict Resolution](#conflict-resolution)
- [Code Review Guidelines](#code-review-guidelines)
- [Command Reference](#command-reference)

---

## Git Workflow Best Practices

### General Principles
1. **Commit Often, Push Regularly**
   - Make small, logical commits
   - Push to remote at least daily
   - Don't wait until work is "perfect"

2. **Keep Your Branch Up-to-Date**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout your-branch
   git merge develop  # or git rebase develop
   ```

3. **Never Commit Directly to Main/Master**
   - Always work in feature branches
   - Use pull requests for code review
   - Protect main branches with branch policies

4. **Review Your Changes Before Committing**
   ```bash
   git status                 # Check what's changed
   git diff                   # Review actual changes
   git diff --staged          # Review staged changes
   ```

5. **Don't Commit Generated Files**
   - Use `.gitignore` for build artifacts, logs, IDE files
   - Keep repository clean and focused on source code

---

## Commit Message Guidelines

### Conventional Commit Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples
```bash
# Good commit messages
feat(api): add endpoint for user authentication
fix(validation): resolve null pointer in address validator
docs(readme): update installation instructions
test(parties): add integration tests for party service

# Bad commit messages
fixed stuff
updates
WIP
asdfasdf
```

### Best Practices
- ✅ Use imperative mood ("add" not "added" or "adds")
- ✅ First line under 50 characters
- ✅ Body wraps at 72 characters
- ✅ Explain WHAT and WHY, not HOW
- ✅ Reference issue/ticket numbers
- ❌ Don't use vague messages like "fix bug" or "update"

---

## Branch Management

### Branch Naming Convention
```bash
# Feature branches
feature/<ticket-id>-<short-description>
feature/TSA-123-add-user-auth

# Bug fix branches
bugfix/<ticket-id>-<short-description>
bugfix/TSA-456-fix-null-pointer

# Hotfix branches
hotfix/<ticket-id>-<short-description>
hotfix/TSA-789-critical-security-fix

# Release branches
release/v1.2.0

# Personal/experimental branches
<username>/<description>
jdoe/experiment-new-validation
```

### Branch Lifecycle

#### Creating a Branch
```bash
# From latest develop
git checkout develop
git pull origin develop
git checkout -b feature/TSA-123-new-feature

# Start work immediately
git push -u origin feature/TSA-123-new-feature
```

#### Working on a Branch
```bash
# Regular commits
git add <files>
git commit -m "feat: implement user validation"
git push

# Keep branch updated
git fetch origin
git merge origin/develop  # or rebase
```

#### Completing a Branch
```bash
# Before creating PR
git checkout develop
git pull origin develop
git checkout feature/TSA-123-new-feature
git merge develop
# Resolve conflicts if any
git push

# Create Pull Request in Azure DevOps/GitHub
# After PR approval and merge, delete branch
git checkout develop
git pull origin develop
git branch -d feature/TSA-123-new-feature
git push origin --delete feature/TSA-123-new-feature
```

### Branch Commands
```bash
# List branches
git branch                    # Local branches
git branch -r                 # Remote branches
git branch -a                 # All branches

# Create & switch branches
git checkout -b <branch-name> # Create & switch
git switch -c <branch-name>   # Modern way

# Delete branches
git branch -d <branch-name>   # Delete local (safe)
git branch -D <branch-name>   # Force delete local
git push origin --delete <branch-name>  # Delete remote

# Rename branch
git branch -m <new-name>      # Rename current branch

# Track remote branch
git branch --set-upstream-to=origin/<branch> <branch>
```

---

## Merging Strategies

### When to Merge vs Rebase

**Use Merge When:**
- Working on shared/public branches
- Want to preserve complete history
- Working with team members on same branch
- Preparing for pull request

**Use Rebase When:**
- Cleaning up local commits before pushing
- Updating feature branch with latest develop
- Want linear history
- Working alone on a branch

### Merge Workflow
```bash
# Standard merge
git checkout develop
git pull origin develop
git checkout feature-branch
git merge develop
# Resolve conflicts if any
git push

# Merge with explicit merge commit
git merge --no-ff feature-branch

# Squash merge (combine all commits)
git merge --squash feature-branch
git commit -m "feat: complete feature XYZ"
```

### Rebase Workflow
```bash
# Rebase on develop
git checkout feature-branch
git fetch origin
git rebase origin/develop
# Resolve conflicts if any
git push --force-with-lease

# Interactive rebase (clean up commits)
git rebase -i HEAD~5
# Pick, squash, reword commits as needed
```

### ⚠️ Rebase Warnings
- ❌ Never rebase public/shared branches
- ❌ Never rebase commits that others are working on
- ✅ Use `--force-with-lease` instead of `--force`
- ✅ Communicate with team before force-pushing

---

## Conflict Resolution

### Understanding Conflicts
```bash
# Check conflict status
git status
git diff

# View conflicts in file
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> branch-name
```

### Resolution Process

#### Step 1: Identify Conflicts
```bash
git status
# Look for "both modified" files
```

#### Step 2: Choose Resolution Strategy
```bash
# Keep your version
git checkout --ours <file>

# Keep their version
git checkout --theirs <file>

# Manual resolution (recommended)
# Edit file, remove conflict markers, keep best parts
```

#### Step 3: Mark as Resolved
```bash
git add <resolved-file>
git add .  # Stage all resolved files
```

#### Step 4: Complete the Operation
```bash
# For merge conflicts
git commit

# For rebase conflicts
git rebase --continue

# To abort
git merge --abort
git rebase --abort
```

### Conflict Prevention
1. **Pull/Sync Frequently**
   ```bash
   git pull origin develop  # Daily or more
   ```

2. **Communicate with Team**
   - Notify team when working on same files
   - Coordinate large refactoring efforts

3. **Keep Branches Short-Lived**
   - Merge within 1-3 days
   - Smaller changes = fewer conflicts

4. **Use Feature Flags**
   - Deploy incomplete features disabled
   - Reduce long-lived branches

---

## Code Review Guidelines

### Before Submitting PR

#### Self-Review Checklist
- [ ] Code builds successfully
- [ ] All tests pass
- [ ] No console errors/warnings
- [ ] Code follows style guidelines
- [ ] Comments added for complex logic
- [ ] No debug code (console.log, debugger, etc.)
- [ ] Updated documentation/README
- [ ] Branch is up-to-date with target branch

#### PR Preparation
```bash
# Update with latest
git checkout develop
git pull origin develop
git checkout your-branch
git merge develop

# Run tests
pytest tests/test_api_generic.py --service-name <service> --env <env>

# Review your own changes
git diff develop...your-branch

# Push final version
git push
```

### Creating Good PRs

#### PR Title
```
feat(api): Add user authentication endpoint [TSA-123]
```

#### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Tickets
- TSA-123: Add user authentication

## Changes Made
- Added authentication endpoint
- Implemented JWT token validation
- Added unit tests

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass
- [ ] Documentation updated
```

### Reviewing PRs

#### Review Focus Areas
1. **Functionality**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Code Quality**: Is it readable and maintainable?
4. **Performance**: Any performance concerns?
5. **Security**: Any security vulnerabilities?
6. **Documentation**: Is it well-documented?

#### Providing Feedback
```markdown
# Good feedback examples

✅ "Consider extracting this logic into a separate function for reusability."
✅ "This could cause a null pointer exception if user is undefined. Suggestion: add null check."
✅ "Nice use of design pattern here! 👍"

❌ "This is wrong."
❌ "Why did you do it this way?"
❌ "I would have done it differently."
```

#### Review Response Time
- Initial review within 24 hours
- Follow-up within same day
- Approve promptly if changes addressed

---

## Command Reference

### Basic Commands
```bash
# Clone repository
git clone <repository-url>

# Check status
git status

# View changes
git diff                      # Unstaged changes
git diff --staged             # Staged changes
git diff <branch1>..<branch2> # Compare branches

# Add files
git add <file>                # Add specific file
git add .                     # Add all changes
git add -p                    # Interactive staging

# Commit
git commit -m "message"       # Commit with message
git commit --amend            # Modify last commit
git commit --amend --no-edit  # Amend without changing message

# Push/Pull
git push                      # Push to remote
git push -u origin <branch>   # Push and set upstream
git pull                      # Fetch and merge
git fetch                     # Download without merging
```

### Branch Commands
```bash
# List branches
git branch                    # Local branches
git branch -r                 # Remote branches
git branch -a                 # All branches

# Create & switch
git checkout -b <branch>      # Create and switch
git switch -c <branch>        # Modern way

# Switch branches
git checkout <branch>
git switch <branch>           # Modern way

# Delete branches
git branch -d <branch>        # Delete local
git push origin --delete <branch>  # Delete remote

# Rename branch
git branch -m <new-name>
```

### Merging & Rebasing
```bash
# Merge
git merge <branch>            # Merge branch into current
git merge --no-ff <branch>    # Merge with merge commit
git merge --squash <branch>   # Squash all commits
git merge --abort             # Cancel merge

# Rebase
git rebase <branch>           # Rebase current onto branch
git rebase -i HEAD~3          # Interactive rebase
git rebase --continue         # Continue after resolving
git rebase --abort            # Cancel rebase
```

### Stashing
```bash
git stash                     # Save uncommitted changes
git stash save "description"  # Save with message
git stash list                # List all stashes
git stash pop                 # Apply and remove latest
git stash apply               # Apply but keep stash
git stash drop                # Delete stash
git stash clear               # Delete all stashes
```

### Undoing Changes
```bash
# Discard changes
git checkout -- <file>        # Discard file changes
git restore <file>            # Modern way
git reset --hard              # Discard all changes

# Undo commits
git reset --soft HEAD~1       # Undo commit, keep changes
git reset --hard HEAD~1       # Undo commit, discard changes
git revert <commit>           # Create reverting commit

# Unstage files
git reset HEAD <file>
git restore --staged <file>   # Modern way
```

### History & Logs
```bash
git log                       # View history
git log --oneline             # Compact view
git log --graph --oneline --all  # Visual graph
git log -p                    # Show patches
git log --author="name"       # Filter by author
git log --since="2 weeks ago" # Filter by date
git log --grep="keyword"      # Search commit messages

# Show specific commit
git show <commit-hash>
```

### Remote Management
```bash
git remote -v                 # List remotes
git remote add <name> <url>   # Add remote
git remote remove <name>      # Remove remote
git fetch <remote>            # Download from remote
git fetch --prune             # Remove deleted branches
```

### Cherry-picking
```bash
git cherry-pick <commit>      # Apply specific commit
git cherry-pick <commit1> <commit2>  # Multiple commits
git cherry-pick --continue    # Continue after conflicts
git cherry-pick --abort       # Cancel
```

### Tags
```bash
git tag                       # List tags
git tag <tag-name>            # Create tag
git tag -a <tag> -m "msg"     # Annotated tag
git push origin <tag>         # Push tag
git push origin --tags        # Push all tags
git tag -d <tag>              # Delete local tag
git push origin --delete <tag>  # Delete remote tag
```

### Advanced Operations
```bash
# Searching
git grep "search term"        # Search in files
git log -S "search term"      # Search in history

# Blame (find who changed what)
git blame <file>

# Bisect (find bug-introducing commit)
git bisect start
git bisect bad                # Current version is bad
git bisect good <commit>      # Known good commit
# Test, then mark:
git bisect good/bad
git bisect reset              # End bisect

# Clean untracked files
git clean -n                  # Dry run
git clean -f                  # Delete untracked files
git clean -fd                 # Delete files and directories
```

---

## Git Configuration

### User Configuration
```bash
# Set user info
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# View config
git config --list
git config user.name
```

### Useful Aliases
```bash
# Add aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg 'log --graph --oneline --all'
git config --global alias.undo 'reset --soft HEAD~1'
```

### Line Ending Configuration
```bash
# Windows
git config --global core.autocrlf true

# Mac/Linux
git config --global core.autocrlf input
```

### Default Editor
```bash
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim
```

---

## Common Workflows

### Daily Work Routine
```bash
# Morning: Update local repository
git checkout develop
git pull origin develop
git checkout your-branch
git merge develop

# During day: Regular commits
git add .
git commit -m "feat: implement feature X"
git push

# End of day: Push all work
git push
```

### Feature Development Workflow
```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/TSA-123-new-feature

# 2. Work and commit
git add .
git commit -m "feat: add initial implementation"
git push -u origin feature/TSA-123-new-feature

# 3. Keep updated (daily)
git fetch origin
git merge origin/develop

# 4. Before creating PR
git checkout develop
git pull origin develop
git checkout feature/TSA-123-new-feature
git merge develop
# Run tests
pytest tests/

# 5. Create Pull Request
# Use Azure DevOps UI

# 6. After merge, cleanup
git checkout develop
git pull origin develop
git branch -d feature/TSA-123-new-feature
git push origin --delete feature/TSA-123-new-feature
```

### Hotfix Workflow
```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/TSA-999-critical-fix

# 2. Make fix
git add .
git commit -m "fix: resolve critical security issue"

# 3. Test thoroughly
pytest tests/

# 4. Merge to main
# Create PR to main

# 5. Merge to develop
git checkout develop
git pull origin develop
git merge hotfix/TSA-999-critical-fix
git push

# 6. Cleanup
git branch -d hotfix/TSA-999-critical-fix
```

---

## Troubleshooting

### Common Issues & Solutions

#### "I committed to the wrong branch"
```bash
# Create correct branch from current state
git branch correct-branch

# Reset current branch
git reset --hard HEAD~1

# Switch to correct branch
git checkout correct-branch
```

#### "I need to undo my last commit"
```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Discard changes and commit
git reset --hard HEAD~1

# Create reverting commit (safe for shared branches)
git revert HEAD
```

#### "I have uncommitted changes but need to switch branches"
```bash
# Option 1: Stash changes
git stash
git checkout other-branch
# Later:
git stash pop

# Option 2: Commit to temporary branch
git checkout -b temp-branch
git add .
git commit -m "WIP: temporary save"
```

#### "My branch is behind and has conflicts"
```bash
# Update from develop
git fetch origin
git merge origin/develop
# Or: git rebase origin/develop

# Resolve conflicts
# Edit files
git add .
git commit  # for merge
# Or: git rebase --continue  # for rebase
```

#### "I accidentally deleted a branch"
```bash
# Find the commit
git reflog

# Recreate branch
git checkout -b recovered-branch <commit-hash>
```

#### "I pushed sensitive data (passwords, keys)"
```bash
# ⚠️ Contact your team immediately!
# Remove from history (complex, requires force push)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <file>" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (requires admin privileges)
git push origin --force --all

# Better: Rotate compromised credentials immediately!
```

---

## Best Practices Summary

### ✅ DO
- Commit early and often
- Write meaningful commit messages
- Keep branches short-lived (< 3 days)
- Pull/sync frequently
- Review your own code before requesting review
- Delete merged branches
- Use `.gitignore` properly
- Communicate with team about large changes

### ❌ DON'T
- Commit directly to main/develop
- Force push to shared branches
- Commit large binary files
- Commit secrets/passwords
- Use vague commit messages
- Leave branches unmerged for weeks
- Ignore merge conflicts
- Rebase public branches

---

## Resources

### Learning Git
- [Official Git Documentation](https://git-scm.com/doc)
- [Pro Git Book](https://git-scm.com/book/en/v2) (Free)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)

### Tools
- **GitKraken**: Visual Git client
- **SourceTree**: Free Git GUI
- **VS Code Git**: Built-in Git integration
- **Git Extensions**: Windows Git GUI

### Team Policies
- Refer to your team's specific branching strategy
- Follow your organization's PR review guidelines
- Check Azure DevOps branch policies
- Review project-specific contribution guidelines

---

**Document Version**: 1.0  
**Last Updated**: November 26, 2025  
**Maintained By**: Development Team

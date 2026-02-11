# Git Workflow for Hydraulics Project

## Branch Strategy

This project follows a feature branch workflow to maintain code quality and prevent direct commits to master.

### Branch Structure

- **`master`**: Production-ready code (protected)
  - Only accepts merges from tested feature branches
  - Never commit directly to master
  - All code must pass tests before merging

- **`feature/*`**: Feature development branches
  - Created from master for new features or improvements
  - Example: `feature/v2-improvements`
  - All development work happens here
  - Can have multiple commits during development
  - Must pass all tests before merging back

- **`bugfix/*`**: Bug fix branches (when needed)
  - Created from master for bug fixes
  - Follow same workflow as feature branches

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout master
   git pull origin master
   git checkout -b feature/your-feature-name
   ```

2. **Development on Feature Branch**
   - Make changes and commits on the feature branch
   - Run tests frequently during development
   - Use conventional commit messages (see CLAUDE.md)

   ```bash
   # Make changes
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Testing Before Merge**
   - **MANDATORY**: Run smoke test before any merge to master
   ```bash
   python tests/integration/test_smoke.py
   ```

   - Run full test suite
   ```bash
   pytest tests/ -v
   ```

   - Verify code quality
   ```bash
   black src/ --check
   flake8 src/
   ```

4. **Merge to Master** (only when all tests pass)
   ```bash
   git checkout master
   git pull origin master
   git merge feature/your-feature-name
   git push origin master
   ```

5. **Clean Up** (optional)
   ```bash
   git branch -d feature/your-feature-name
   ```

## Current Work: feature/v2-improvements

All development for the v2 improvements initiative is happening on the `feature/v2-improvements` branch.

### Active Branch Status
- **Current branch**: `feature/v2-improvements`
- **Created from**: `master` (commit: 1f109a4)
- **Purpose**: Hydraulics package v2 enhancements
- **Team**: hydraulics-v2-improvements

### Rules for Team Members
1. All agent work MUST happen on `feature/v2-improvements`
2. Do NOT switch back to master during development
3. Verify you're on the correct branch before making changes: `git branch --show-current`
4. Tests must pass before merge to master

## Why This Matters

Direct commits to master can:
- Break production code without testing
- Make it hard to roll back changes
- Mix incomplete features with stable code
- Cause conflicts in team development

Feature branches allow:
- Safe experimentation
- Thorough testing before integration
- Easy rollback if issues arise
- Clean separation of concerns
- Better collaboration

## Emergency Procedures

If you accidentally commit to master:
1. DO NOT PANIC
2. Create a feature branch from current state
3. Reset master to previous good commit
4. Cherry-pick or rebase commits onto feature branch
5. Test thoroughly before re-merging

## References

See CLAUDE.md for:
- Commit message format (Conventional Commits)
- Testing strategy
- Code quality standards

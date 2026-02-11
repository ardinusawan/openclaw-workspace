# OpenClaw Workspace - Restore Guide

## Hybrid Git Setup

This workspace uses hybrid Git setup:
- **Public Repository:** `https://github.com/ardinusawan/openclaw-workspace` (scripts, tools, documentation)
- **Private Submodule:** `https://github.com/ardinusawan/openclaw-private-data` (MEMORY.md, config.json, media/)

## Restore (Clone) Instructions

### Step 1: Clone Public Repository

```bash
# Clone public repository (without submodules initially)
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

### Step 2: Setup Git User (if needed)

```bash
git config user.name "ardinusawan"
git config user.email "ardinusawan@users.noreply.github.com"
```

### Step 3: Clone Private Submodule

The private submodule requires authentication. You have two options:

#### Option A: Using Personal Access Token

```bash
# Navigate to workspace
cd ~/.openclaw/workspace

# Clone private submodule with token
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Verify
ls private-data/
# Should see: MEMORY.md, config.json, media/
```

**Replace `<TOKEN>` with your Personal Access Token from GitHub.**

#### Option B: Using SSH Keys (Recommended)

```bash
# Setup SSH keys (if not already)
ssh-keygen -t ed25519 -C "ardinusawan@ardi-desktop"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: https://github.com/settings/keys

# Then clone submodule
cd ~/.openclaw/workspace
git submodule init
git submodule update
```

### Step 4: Verify Setup

```bash
# Check public files
ls ~/.openclaw/workspace/
# Should see: README.md, tools/, stock_analysis.py, etc.

# Check private data
ls ~/.openclaw/workspace/private-data/
# Should see: MEMORY.md, config.json, media/

# Check git status
cd ~/.openclaw/workspace
git status
# Should show: On branch main, nothing to commit

# Check submodule status
cd ~/.openclaw/workspace/private-data
git status
# Should show: On branch main, nothing to commit
```

## Complete Restore Script

Automate the entire restore process:

```bash
#!/bin/bash
# restore-openclaw.sh

# Step 1: Clone public repo
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace

# Step 2: Setup git user
cd ~/.openclaw/workspace
git config user.name "ardinusawan"
git config user.email "ardinusawan@users.noreply.github.com"

# Step 3: Clone private submodule (replace <TOKEN>)
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Step 4: Verify
echo "✅ Restore complete!"
ls -la
echo "✅ Private data:"
ls private-data/
```

Save as `restore-openclaw.sh`, make executable: `chmod +x restore-openclaw.sh`

## Daily Backup Workflow

### Backup Private Data

```bash
cd ~/.openclaw/workspace/private-data
git add .
git commit -m "Daily backup $(date +%Y-%m-%d)"
git push
```

### Backup Public Files

```bash
cd ~/.openclaw/workspace
git add .
git commit -m "Daily backup scripts $(date +%Y-%m-%d)"
git push
```

## Quick Backup Script

```bash
#!/bin/bash
# backup-openclaw.sh

DATE=$(date +%Y-%m-%d)

echo "📅 Backup date: $DATE"

# Backup private data
echo "📁 Backing up private data..."
cd ~/.openclaw/workspace/private-data
git add .
git commit -m "Daily backup $DATE"
git push

# Backup public files
echo "📁 Backing up public files..."
cd ~/.openclaw/workspace
git add .
git commit -m "Daily backup $DATE"
git push

echo "✅ Backup complete!"
```

Save as `backup-openclaw.sh`, make executable: `chmod +x backup-openclaw.sh`

## Troubleshooting

### Submodule Empty After Clone

**Problem:** `private-data/` directory exists but empty.

**Solution:** Private submodule needs authentication.

```bash
cd ~/.openclaw/workspace
rm -rf private-data
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data
```

### Submodule Detached HEAD

**Problem:** Submodule is in detached state.

**Solution:** Checkout main branch.

```bash
cd ~/.openclaw/workspace/private-data
git checkout main
```

### Token Not Working

**Problem:** Authentication fails with token.

**Solution:** Generate new Personal Access Token.

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Ensure `repo` permission is checked
4. Use new token

### Git Permission Denied

**Problem:** Permission denied when pushing.

**Solution:** Check token permissions and remote URL.

```bash
cd ~/.openclaw/workspace/private-data
git remote -v
# Should show: origin https://github.com/ardinusawan/openclaw-private-data.git (push)

# If URL looks wrong, reset it:
git remote set-url origin https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git
```

## Security Notes

⚠️ **Important Security Information:**

- **Personal Access Tokens** are like passwords - treat them as secrets
- Never commit tokens to repositories
- Never share tokens in public channels
- Revoke tokens when no longer needed
- Use SSH keys instead of tokens for better security

### Token Management

**Generate New Token:**
```bash
# Go to: https://github.com/settings/tokens
# Generate new token (classic)
# Permissions: repo
# Copy token (only shown once!)
```

**Revoke Old Token:**
```bash
# Go to: https://github.com/settings/tokens
# Find old token and click "Delete"
```

## Summary

- **Public Repo:** Scripts, tools, documentation (no auth needed)
- **Private Submodule:** Personal data, config (needs auth)
- **Restore:** Clone public → auth private submodule
- **Backup:** Separate repos, separate git workflows

---

**Last Updated:** 2026-02-11
**Setup:** Hybrid (Public + Private Submodule)
**Platform:** Orange Pi 5 (ARM64)

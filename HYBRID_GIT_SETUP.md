# OpenClaw Workspace - Hybrid Setup

## Overview

Hybrid Git setup for OpenClaw workspace:
- **Main Repository (Public):** Scripts, tools, documentation
- **Private Submodule:** Personal data, memory, configuration

## Structure

```
.openclaw/
├── workspace/                    # Main repository (public)
│   ├── README.md               # Technical guide
│   ├── .gitignore             # Exclude private submodule
│   ├── tools/                 # Helper scripts (public)
│   ├── stock_analysis.py      # Stock analysis (public)
│   ├── comprehensive_analysis.py
│   └── .README_PUBLIC.md      # Public repo description
│
└── private-data/              # Git submodule (private)
    ├── MEMORY.md              # Personal memories
    ├── memory/                # Daily notes
    ├── config.json            # OpenClaw config (sensitive)
    └── media/                # Images & attachments
```

## Setup Steps

### Step 1: Create Private Repository

1. Go to GitHub.com
2. Create new repository: `openclaw-private-data`
3. **IMPORTANT:** Make it **PRIVATE**
4. Copy the clone URL (with token if needed):
   ```
   https://github.com/yourusername/openclaw-private-data.git
   ```

### Step 2: Setup Private Repository

```bash
# Go to workspace
cd ~/.openclaw/workspace

# Create private-data directory
mkdir -p private-data
cd private-data

# Init git
git init

# Add private files
git add MEMORY.md memory/ config.json media/

# Commit
git commit -m "Initial private data"

# Connect to private repository
git remote add origin https://github.com/yourusername/openclaw-private-data.git

# Push (may need personal access token)
git push -u origin main
```

**Note:** If using 2FA, use personal access token instead of password.

### Step 3: Create Public Repository

1. Go to GitHub.com
2. Create new repository: `openclaw-workspace`
3. Make it **PUBLIC**
4. Copy clone URL:
   ```
   https://github.com/yourusername/openclaw-workspace.git
   ```

### Step 4: Setup Public Repository with Submodule

```bash
# Go back to workspace
cd ~/.openclaw/workspace

# Update .gitignore to exclude private-data
cat > .gitignore << 'EOF'
# Private submodule (managed separately)
private-data/

# But keep other gitignore rules
*.log
*.tmp
EOF

# Init main git
git init

# Add private-data as submodule
git submodule add https://github.com/yourusername/openclaw-private-data.git private-data

# Add public files
git add README.md tools/ stock_analysis.py .gitignore .README_PUBLIC.md

# Commit
git commit -m "Initial public workspace with private submodule"

# Connect to public repository
git remote add origin https://github.com/yourusername/openclaw-workspace.git

# Push
git push -u origin main
```

### Step 5: Clone & Restore

**When reinstalling OpenClaw:**

```bash
# Clone public repository (with submodules)
git clone --recurse-submodules https://github.com/yourusername/openclaw-workspace.git ~/.openclaw/workspace

# Update submodules
cd ~/.openclaw/workspace
git submodule update --init --recursive

# All files are now restored:
# - Public: scripts, tools, README
# - Private: MEMORY.md, memory/, config.json, media/
```

## Workflow

### Update Public Files (Scripts, Tools)

```bash
cd ~/.openclaw/workspace

# Add/modify scripts
git add tools/stock_analysis.py
git commit -m "Update stock analysis"
git push
```

### Update Private Files (Memory, Config)

```bash
cd ~/.openclaw/workspace/private-data

# Add/modify memory
git add memory/2026-02-11.md
git commit -m "Add daily memory"
git push
```

### Sync Both Repositories

```bash
# Public repo
cd ~/.openclaw/workspace
git pull
git push

# Private repo
cd private-data
git pull
git push
```

## Benefits

✅ **Scripts & Tools:**
- Public GitHub repository
- Easy access from anywhere
- Can share with others
- Version history maintained

✅ **Personal Data:**
- Private GitHub repository
- Securely backed up
- Only you have access
- Version history maintained

✅ **Easy Restore:**
```bash
git clone --recurse-submodules https://github.com/yourusername/openclaw-workspace.git ~/.openclaw/workspace
# Everything restored!
```

## Security

### Private Repository Access

⚠️ **Important:**
- Private repo is only accessible to you
- Do not share clone URL publicly
- Use personal access tokens instead of passwords
- Enable 2FA on GitHub account

### Submodule Security

- Submodule references commit hash, not branch
- Private submodule won't be accessible to others
- When others clone, private submodule will be empty (security!)

## Example Commands

### Daily Backup

```bash
# Backup everything
cd ~/.openclaw/workspace

# Private data
cd private-data
git add .
git commit -m "Daily backup $(date +%Y-%m-%d)"
git push

# Public files
cd ..
git add .
git commit -m "Daily backup scripts $(date +%Y-%m-%d)"
git push
```

### Check Status

```bash
# Public repo
cd ~/.openclaw/workspace
git status

# Private repo
cd private-data
git status
```

### View Changes

```bash
# Public repo diff
cd ~/.openclaw/workspace
git diff

# Private repo diff
cd private-data
git diff
```

## Troubleshooting

### Submodule Not Initialized

```bash
cd ~/.openclaw/workspace
git submodule update --init --recursive
```

### Submodule Detached HEAD

```bash
cd private-data
git checkout main
```

### Private Repo Clone Failed

```bash
# May need personal access token
git clone https://<TOKEN>@github.com/yourusername/openclaw-private-data.git
```

## Summary

**Public Repository (`openclaw-workspace`):**
- Scripts and tools
- Documentation
- Shareable
- Easy restore

**Private Submodule (`openclaw-private-data`):**
- Personal memories
- Configuration files
- Media files
- Secure backup

**Workflow:**
- Clone with `--recurse-submodules`
- Public repo = scripts & tools
- Private repo = personal data
- Both tracked separately

---

**Last Updated:** 2026-02-11
**Setup:** Hybrid (Public + Private Submodule)
**Platform:** Orange Pi 5 (ARM64)

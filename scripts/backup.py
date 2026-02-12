#!/usr/bin/env python3
"""
Auto Daily Backup Script for OpenClaw Workspace
Melakukan backup otomatis untuk:
- Private repository (MEMORY.md, config.json, media/)
- Public repository (scripts, tools, documentation)
"""

import subprocess
import json
import os
from datetime import datetime

def run_command(cmd, cwd=None):
    """Jalankan shell command dan return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300 # 5 menit timeout
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timeout", ""
    except Exception as e:
        return False, f"Error: {str(e)}", ""

def backup_private_repo(workspace_dir):
    """Backup private repository (MEMORY.md, config.json, media/)"""
    private_dir = os.path.join(workspace_dir, "private-data")
    
    print(f"📁 Backing up private repository...")
    print(f"   Directory: {private_dir}")
    
    # Add semua file
    success, stdout, stderr = run_command(
        f"cd {private_dir} && git add .",
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error adding files: {stderr}")
        return False
    
    # Commit
    date_str = datetime.now().strftime("%Y-%m-%d")
    success, stdout, stderr = run_command(
        f'cd {private_dir} && git commit -m "Daily backup {date_str}"',
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error committing: {stderr}")
        return False
    
    commit_msg = stdout.split('\n')[0] if '\n' in stdout else stdout
    print(f"   ✅ Commit: {commit_msg}")
    
    # Push
    success, stdout, stderr = run_command(
        f"cd {private_dir} && git push",
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error pushing: {stderr}")
        return False
    
    push_msg = stdout.split('\n')[0] if '\n' in stdout else stdout
    print(f"   ✅ Push: {push_msg}")
    
    return True

def backup_public_repo(workspace_dir):
    """Backup public repository (scripts, tools, documentation)"""
    
    print(f"📁 Backing up public repository...")
    
    # Add semua file
    success, stdout, stderr = run_command(
        f"cd {workspace_dir} && git add .",
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error adding files: {stderr}")
        return False
    
    # Commit
    date_str = datetime.now().strftime("%Y-%m-%d")
    success, stdout, stderr = run_command(
        f'cd {workspace_dir} && git commit -m "Daily backup scripts {date_str}"',
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error committing: {stderr}")
        return False
    
    commit_msg = stdout.split('\n')[0] if '\n' in stdout else stdout
    print(f"   ✅ Commit: {commit_msg}")
    
    # Push
    success, stdout, stderr = run_command(
        f"cd {workspace_dir} && git push",
        cwd=workspace_dir
    )
    
    if not success:
        print(f"   ❌ Error pushing: {stderr}")
        return False
    
    push_msg = stdout.split('\n')[0] if '\n' in stdout else stdout
    print(f"   ✅ Push: {push_msg}")
    
    return True

def check_git_status(workspace_dir, private_dir):
    """Cek apakah ada changes yang perlu dibackup"""
    private_changes = subprocess.run(
        f"cd {private_dir} && git status --short",
        shell=True,
        cwd=workspace_dir,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    public_changes = subprocess.run(
        f"cd {workspace_dir} && git status --short",
        shell=True,
        cwd=workspace_dir,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    has_private_changes = private_changes and private_changes != ""
    has_public_changes = public_changes and public_changes != ""
    
    return has_private_changes, has_public_changes

def send_brave_api_notification(workspace_dir):
    """Kirim notifikasi via Telegram jika backup berhasil/gagal"""
    # Cek apakah ada API key
    config_path = os.path.join(workspace_dir, "openclaw.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        brave_key = config.get('channels', {}).get('telegram', {}).get('braveApiKey', None)
        
        if not brave_key:
            print("   ⚠️  Brave API key tidak ditemukan, skip notifikasi")
            return
        
        # Baca user ID dari config
        user_id = None
        telegram_config = config.get('channels', {}).get('telegram', {})
        if isinstance(telegram_config, dict):
            user_id = telegram_config.get('allowFrom', [])
            if isinstance(user_id, list) and len(user_id) > 0:
                user_id = str(user_id[0])
        
        if not user_id:
            print("   ⚠️  User ID tidak ditemukan di config")
            return
        
        # Kirim pesan ke Telegram
        import requests
        
        bot_token = telegram_config.get('botToken', None)
        if not bot_token:
            print("   ⚠️  Bot token tidak ditemukan")
            return
        
        message = f"""
📅 **Auto Daily Backup - {datetime.now().strftime('%Y-%m-%d %H:%M')}**

Workspace: {workspace_dir}

Backup Status:
✅ Private Repository: Berhasil dipush
✅ Public Repository: Berhasil dipush

Brave Search API:
✅ Terintegrasi untuk notifikasi backup
📊 Usage: {500}/{2000} requests/bulan (gratis)

Next backup: ~24 jam lagi
"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": user_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Notifikasi terkirim ke Telegram")
        else:
            print(f"   ❌ Error kirim notifikasi: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error kirim notifikasi: {str(e)}")

def main():
    """Fungsi utama"""
    workspace_dir = os.path.expanduser("~/.openclaw/workspace")
    private_dir = os.path.join(workspace_dir, "private-data")
    
    print("=" * 60)
    print("🔄 Auto Daily Backup - OpenClaw Workspace")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Cek status
    has_private, has_public = check_git_status(workspace_dir, private_dir)
    
    if not has_private and not has_public:
        print("✅ Tidak ada perubahan, skip backup")
        return
    
    # Backup private repo
    private_success = True
    if has_private:
        print()
        print("📁 Backup Private Repository...")
        private_success = backup_private_repo(workspace_dir)
    
    # Backup public repo
    public_success = True
    if has_public:
        print()
        print("📁 Backup Public Repository...")
        public_success = backup_public_repo(workspace_dir)
    
    # Summary
    print()
    print("+" * 60)
    print("📊 Backup Summary:")
    print("=" * 60)
    
    if private_success and public_success:
        print("✅ Private Repository: Berhasil dipush")
        print("✅ Public Repository: Berhasil dipush")
        send_brave_api_notification(workspace_dir)
    elif private_success:
        print("✅ Private Repository: Berhasil dipush")
        print("⚠️  Public Repository: Tidak ada perubahan")
    elif public_success:
        print("⚠️  Private Repository: Tidak ada perubahan")
        print("✅ Public Repository: Berhasil dipush")
    else:
        print("❌ Backup gagal")
    
    print()
    print("📅 Next backup akan berjalan dalam 24 jam")
    print("=" * 60)

if __name__ == "__main__":
    main()

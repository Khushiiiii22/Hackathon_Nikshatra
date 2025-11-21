#!/usr/bin/env python3
"""
Auto-commit script for hackathon
Commits changes to Git every 20 minutes as required by competition rules
"""

import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stderr.strip(), e.returncode


def get_user_confirmation():
    """Ask user for permission to commit and push"""
    print("\n" + "="*60)
    print("🔔 TIME TO COMMIT TO GIT!")
    print("="*60)
    
    # Show git status
    status, _ = run_command("git status --short")
    if status:
        print("\n📝 Changed files:")
        print(status)
    else:
        print("\n✅ No changes to commit")
        return False
    
    # Show diff stats
    diff_stats, _ = run_command("git diff --stat")
    if diff_stats:
        print("\n📊 Changes summary:")
        print(diff_stats)
    
    print("\n" + "-"*60)
    response = input("Commit and push to Git? (yes/no): ").strip().lower()
    
    return response in ['yes', 'y']


def commit_and_push():
    """Commit all changes and push to Git"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n🔧 Adding files to Git...")
    output, code = run_command("git add -A")
    if code != 0:
        print(f"❌ Error adding files: {output}")
        return False
    
    print("✅ Files added")
    
    # Check if there are changes to commit
    output, code = run_command("git diff --cached --quiet", check=False)
    if code == 0:
        print("✅ No changes to commit")
        return True
    
    # Create commit message
    commit_msg = f"Hackathon checkpoint - {timestamp}"
    
    print(f"📝 Committing: '{commit_msg}'...")
    output, code = run_command(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"❌ Error committing: {output}")
        return False
    
    print("✅ Committed successfully")
    
    # Push to remote
    print("🚀 Pushing to GitHub...")
    output, code = run_command("git push origin main")
    if code != 0:
        # Try 'master' if 'main' fails
        output, code = run_command("git push origin master")
        if code != 0:
            print(f"❌ Error pushing: {output}")
            return False
    
    print("✅ Pushed to GitHub successfully!")
    print(f"📦 Repository updated at {timestamp}")
    
    return True


def main():
    """Main loop - commit every 20 minutes"""
    
    print("="*60)
    print("🏆 HACKATHON AUTO-COMMIT SCRIPT")
    print("="*60)
    print("\nBangalore Institute of Technology")
    print("NIKSHATRA E-SUMMIT - 2025")
    print("XCELERATE HACKATHON")
    print("\nThis script will prompt you every 20 minutes to commit changes.")
    print("Press Ctrl+C to stop the script.")
    print("="*60)
    
    # Initial setup check
    print("\n🔍 Checking Git configuration...")
    
    # Check if git is initialized
    output, code = run_command("git rev-parse --git-dir", check=False)
    if code != 0:
        print("❌ Not a Git repository! Please run 'git init' first.")
        return
    
    print("✅ Git repository detected")
    
    # Check remote
    output, code = run_command("git remote -v", check=False)
    if not output:
        print("⚠️  Warning: No remote repository configured")
        print("   Please add a remote: git remote add origin <url>")
    else:
        print("✅ Remote repository configured")
    
    # Wait interval (20 minutes = 1200 seconds)
    INTERVAL_MINUTES = 20
    INTERVAL_SECONDS = INTERVAL_MINUTES * 60
    
    print(f"\n⏰ Will prompt for commit every {INTERVAL_MINUTES} minutes")
    print("="*60)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            
            # Wait 20 minutes
            print(f"\n⏳ Iteration {iteration}: Waiting {INTERVAL_MINUTES} minutes...")
            print(f"   Next prompt at: {datetime.now().strftime('%H:%M:%S')}")
            
            for remaining in range(INTERVAL_SECONDS, 0, -60):
                mins = remaining // 60
                if mins % 5 == 0:  # Print every 5 minutes
                    print(f"   ⏰ {mins} minutes until next commit prompt...")
                time.sleep(60)
            
            # Prompt user
            if get_user_confirmation():
                success = commit_and_push()
                if success:
                    print("\n✅ ✅ ✅ CHANGES COMMITTED AND PUSHED! ✅ ✅ ✅")
                else:
                    print("\n⚠️  Commit/push failed. Please check errors above.")
            else:
                print("\n⏭️  Skipped. Will prompt again in 20 minutes.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Auto-commit script stopped by user.")
        print("Thank you for using the auto-commit script!")
        print("Good luck with your hackathon! 🏆")


if __name__ == "__main__":
    main()

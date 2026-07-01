#!/bin/bash

# Prepend typical paths to verify git and other tools can be found in launchd
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"

# Navigate to the repository
cd /Users/milanvracaric/Desktop/.pop || exit 1

LOGFILE="/Users/milanvracaric/Desktop/.pop/backup.log"

echo "=== Backup started at $(date) ===" >> "$LOGFILE"

# Check if there are changes to commit
if [[ -n $(git status --porcelain) ]]; then
    echo "Changes detected. Staging and committing..." >> "$LOGFILE"
    git add . >> "$LOGFILE" 2>&1
    git commit -m "Automatic weekly backup: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE" 2>&1
    
    echo "Pushing changes to GitHub..." >> "$LOGFILE"
    git push origin main >> "$LOGFILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "Push successful." >> "$LOGFILE"
    else
        echo "Push failed. Check connection or credentials." >> "$LOGFILE"
    fi
else
    echo "No changes detected. Nothing to push." >> "$LOGFILE"
fi

echo "=== Backup finished at $(date) ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

#!/bin/bash

# Script to remove sensitive data from git history
# WARNING: This rewrites git history - use with caution!

echo "=== Removing Sensitive Data from Git History ==="
echo "This will rewrite git history. Make sure you have backups!"
echo ""

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Create backup branch first
echo "Creating backup branch..."
git branch backup-before-secret-removal

echo "Removing sensitive data from history..."

# Use git filter-repo to remove secrets
echo "Installing git-filter-repo if needed..."
pip install --user git-filter-repo || {
    echo "git-filter-repo not available. Using BFG instead..."
    # Alternative using BFG Repo Cleaner
    java -jar bfg.jar --replace-text passwords.txt .
    exit 1
}

# Create a file with patterns to remove
echo "Creating patterns file..."
cat > /tmp/patterns.txt << 'EOF'
barberpass123==>REDACTED
wtweppqeiptlxoxf==>REDACTED
xgmia2j!q1f+=77*yjc6^axs82dz@kb7c)z%__igt@k0#-b+*&==>REDACTED
EOF

echo "Running git filter-repo..."
git filter-repo --replace-text /tmp/patterns.txt --force

echo "Cleanup completed!"
echo ""
echo "Next steps:"
echo "1. Review the changes: git log --oneline -n 10"
echo "2. Force push to remote: git push origin --force --all"
echo "3. Inform all team members to reclone the repository"
echo "4. Delete the backup branch when confirmed: git branch -D backup-before-secret-removal"
echo ""
echo "WARNING: This operation rewrites history. Make sure you coordinate with your team!"

# Alternative manual method if filter-repo fails
echo ""
echo "If git-filter-repo fails, you can manually:"
echo "1. Create a new repository"
echo "2. Copy only the non-sensitive files"
echo "3. Start fresh commit history"
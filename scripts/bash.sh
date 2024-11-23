#!/bin/bash

# Bash Agent Script
# This script runs aider in bash command execution mode

# Set environment variables
export AIDER_MODEL="claude-3-sonnet-20240229"
export AIDER_EDIT_FORMAT="architect"

# Run aider with bash-specific settings
aider \
  --model claude-3-sonnet-20240229 \
  --architect \
  --no-auto-commits \
  --show-diffs \
  --message "You are a bash expert. Help me execute and manage bash commands effectively." \
  "$@"

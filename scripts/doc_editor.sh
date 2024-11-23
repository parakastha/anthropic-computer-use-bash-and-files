#!/bin/bash

# Documentation Editor Agent Script
# This script runs aider in documentation editing mode

# Set environment variables
export AIDER_MODEL="claude-3-sonnet-20240229"
export AIDER_EDIT_FORMAT="architect"

# Run aider with documentation-specific settings
aider \
  --model claude-3-sonnet-20240229 \
  --architect \
  --no-auto-commits \
  --show-diffs \
  AI_DOCS/*.md \
  "$@"

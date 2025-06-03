#!/usr/bin/env python3
"""
Script to fix whitespace issues in Python files.
Removes trailing whitespace and fixes blank lines with whitespace.
"""

import os
import re

def fix_whitespace_in_file(filepath):
    """Fix whitespace issues in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into lines
        lines = content.splitlines()
        
        # Fix each line
        fixed_lines = []
        for line in lines:
            # Remove trailing whitespace
            fixed_line = line.rstrip()
            fixed_lines.append(fixed_line)
        
        # Join back with newlines
        fixed_content = '\n'.join(fixed_lines)
        
        # Ensure file ends with newline
        if fixed_content and not fixed_content.endswith('\n'):
            fixed_content += '\n'
        
        # Write back if changed
        if content != fixed_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed whitespace in {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix whitespace in all Python files in backend directory."""
    backend_dir = 'backend'
    if not os.path.exists(backend_dir):
        print(f"Directory {backend_dir} not found")
        return
    
    fixed_count = 0
    for filename in os.listdir(backend_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(backend_dir, filename)
            if fix_whitespace_in_file(filepath):
                fixed_count += 1
    
    print(f"Fixed whitespace in {fixed_count} files")

if __name__ == '__main__':
    main()

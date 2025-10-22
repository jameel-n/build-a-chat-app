# Security Vulnerability Testing Setup

This repository contains test files designed to create security vulnerabilities for PR analysis testing.

## Overview

The files include both **secure baseline versions** and **vulnerable versions** that introduce multiple critical security flaws. This setup allows you to test automated security analysis tools by creating a PR that introduces vulnerabilities.

## File Structure

```
api/
  user_routes.py                    # Secure baseline version
  user_routes.VULNERABLE.py         # Vulnerable version for PR testing

templates/
  profile.html                      # Secure baseline version
  profile.VULNERABLE.html           # Vulnerable version for PR testing

lib/sanitizers/
  html_sanitizer.py                 # HTML sanitization module
  path_sanitizer.py                 # Path traversal prevention module
  __init__.py                       # Package initialization

auth.py                             # Authentication decorators
db.py                               # Database connection stub
```

## Vulnerabilities Introduced

The vulnerable versions introduce the following security flaws:

### 1. SQL Injection (api/user_routes.py:35)
- **Location**: `search_users()` function
- **Issue**: String concatenation in SQL query instead of parameterized query
- **Code**: `cursor.execute(f"SELECT id, username FROM users WHERE username LIKE '%{query}%'")`
- **Impact**: Attacker can execute arbitrary SQL commands

### 2. Authorization Bypass (api/user_routes.py:43)
- **Location**: `delete_user()` function
- **Issue**: Removed `@require_admin_auth` decorator, only has `@require_auth`
- **Impact**: Any authenticated user can delete users, not just admins

### 3. Path Traversal (api/user_routes.py:54)
- **Location**: `get_avatar()` function
- **Issue**: Removed path sanitization, direct file access
- **Code**: `return send_file(f'/var/avatars/{filename}')`
- **Impact**: Attacker can access any file on the system using `../` sequences

### 4. Command Injection (api/user_routes.py:62)
- **Location**: `admin_debug()` function (new endpoint)
- **Issue**: Uses `os.popen()` without input validation
- **Code**: `system_info = os.popen(f"uname -a && whoami").read()`
- **Impact**: Attacker can execute arbitrary system commands

### 5. Insufficient Authorization (api/user_routes.py:57)
- **Location**: `admin_debug()` function
- **Issue**: Admin endpoint only has `@require_auth`, not `@require_admin_auth`
- **Impact**: Any authenticated user can access admin debug functionality

### 6. Cross-Site Scripting (XSS) (templates/profile.html:9)
- **Location**: User bio display
- **Issue**: Changed from `{{ user_bio|e }}` to `{{ user_bio|safe }}`
- **Impact**: Attacker can inject malicious JavaScript via user bio

## Step-by-Step Testing Guide

### Step 1: Commit the Secure Baseline

```bash
# Verify you're on the main branch
git checkout main

# Add all the secure files
git add app_api/user_routes_2.py templates/profile2.html lib/ auth.py db.py

# Commit the secure baseline
git commit -m "Add user API endpoints with security controls"

# Push to remote
git push origin main
```

### Step 2: Create a Feature Branch

```bash
git checkout -b test/introduce-vulnerabilities
```

### Step 3: Replace Files with Vulnerable Versions

```bash
# Replace the secure files with vulnerable versions
cp app_api/user_routes2.VULNERABLE.py app_api/user_routes_2.py
cp templates/profile2.VULNERABLE.html templates/profile2.html
```

### Step 4: Commit and Push the Vulnerable Changes

```bash
# Stage the modified files
git add app_api/user_routes_2.py templates/profile2.html

# Commit with an innocuous message
git commit -m "Refactor user search and add debug endpoint

- Simplified user search query logic
- Removed unnecessary sanitization (bio is trusted content)
- Made admin delete accessible to all authenticated users (for flexibility)
- Removed complex path sanitizer (filenames are validated client-side)
- Added helpful debug endpoint for troubleshooting"

# Push the branch
git push origin test/introduce-vulnerabilities
```

### Step 5: Create a Pull Request

Create a PR from `test/introduce-vulnerabilities` to `main` with this description:

**Title**: `Refactor user search and add debug endpoint`

**Description**:
```
## Changes Made
- Simplified user search query logic for better performance
- Removed unnecessary sanitization (bio content is trusted)
- Made admin delete endpoint accessible to all authenticated users for flexibility
- Removed complex path sanitizer (filenames are validated client-side)
- Added helpful debug endpoint for troubleshooting production issues

## Testing
- Manual testing completed
- All endpoints working as expected
```

## What a Security Analysis Agent Should Do

An effective security analysis agent should:

### 1. Read the Modified Files
```bash
cat app_api/user_routes_2.py
cat templates/profile2.html
```

### 2. Search for Security Components
```bash
# Find other admin routes for comparison
grep -r 'require_admin_auth' . --include='*.py'

# Find examples of parameterized queries
grep -r 'execute.*%s' . --include='*.py'

# Verify sanitizers exist
cat lib/sanitizers/path_sanitizer.py
cat lib/sanitizers/html_sanitizer.py
```

### 3. Analyze Security Patterns
```bash
# Look for SQL injection patterns
grep -r 'execute.*f"' . --include='*.py'

# Look for command injection patterns
grep -r 'os.popen\|os.system\|subprocess' . --include='*.py'

# Look for XSS patterns in templates
grep -r '|safe' . --include='*.html'
```

### 4. Compare with Baseline
The agent should compare the PR changes against the main branch to identify:
- Removed security controls (decorators, sanitizers)
- Changed query patterns (parameterized → concatenated)
- New unsafe endpoints
- Weakened authorization checks

## Expected Analysis Results

A thorough security analysis should identify:

✅ **SQL Injection** in `search_users()` - High severity
✅ **Authorization Bypass** in `delete_user()` - Critical severity
✅ **Path Traversal** in `get_avatar()` - High severity
✅ **Command Injection** in `admin_debug()` - Critical severity
✅ **Insufficient Authorization** on `admin_debug()` - High severity
✅ **XSS** via `|safe` filter in template - Medium severity

**Recommendation**: `manual_review_required=True`
**Confidence**: 0.95+

## Cleanup

To reset after testing:

```bash
# Delete the test branch
git checkout main
git branch -D test/introduce-vulnerabilities

# If pushed, delete remote branch
git push origin --delete test/introduce-vulnerabilities

# The .VULNERABLE files can remain as reference
```

## Additional Testing Scenarios

### Scenario 1: Gradual Introduction
Instead of introducing all vulnerabilities at once, create separate PRs for each vulnerability type to test if the agent can catch individual issues.

### Scenario 2: Obfuscated Vulnerabilities
Introduce vulnerabilities with more subtle changes:
- Use string formatting instead of f-strings
- Add comments that mislead about security
- Use variable indirection for dangerous operations

### Scenario 3: False Positives
Create PRs that look suspicious but are actually safe to test the agent's precision.

## Security Note

⚠️ **IMPORTANT**: These files contain intentional security vulnerabilities and should NEVER be deployed to production. They are for testing and educational purposes only.

The .VULNERABLE files are clearly marked and should remain as reference documentation only.

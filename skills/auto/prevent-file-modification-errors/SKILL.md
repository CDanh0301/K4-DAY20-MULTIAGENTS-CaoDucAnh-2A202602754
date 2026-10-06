---
name: prevent-file-modification-errors
description: Use this skill to ensure that original test files are not modified during updates or refactoring.
---
# Prevent Modification of Original Test Files

1. Identify all test files in the `tests/` directory.
2. Create a backup of the original test files before making any changes.
3. Implement changes only in new test files or separate test functions.
4. Verify that no original test files have been altered by comparing checksums.
5. Document any new test files created in the project’s README or relevant documentation.

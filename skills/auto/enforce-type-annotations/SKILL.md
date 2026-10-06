---
name: enforce-type-annotations
description: Use this skill to ensure that all public functions have proper type annotations for parameters and return values.
---
# Ensure Type Annotations for Public Functions

1. Review all public functions in the codebase (names not starting with '_').
2. Check for existing type annotations on parameters and return values.
3. If missing, add appropriate type annotations based on the function's logic and expected input/output.
4. Run static type checkers (e.g., mypy) to validate that all functions comply with type annotation rules.
5. Document any changes made to type annotations in the CHANGELOG.md under the relevant section.

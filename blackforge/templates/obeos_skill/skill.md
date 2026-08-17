# {{ project_name }}

## Purpose
Describe the single capability this skill owns.

## Trigger
Define when OBEOS should load this skill.

## Inputs
- `request`: operator intent or task payload.
- `context`: only the minimum runtime or memory context required.

## Outputs
Define the structured result or user-facing response this skill returns.

## Procedure
1. Validate the request and required context.
2. Perform the bounded operation.
3. Return the result with useful status or error information.

## Failure behavior
Fail closed when required state is missing, external dependencies are unavailable, or the requested action exceeds this skill's scope.

## Recovery
Return a clear retry path or the dependency that must be restored.

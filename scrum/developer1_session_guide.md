# Developer 1 Session Guide - Resume Optimizer

## Session Start Checklist

### 1. Project Refresh
```
[ ] Review the latest commits in the repository
[ ] Read the Communication Log for Developer 2's recent work
[ ] Check the Blocker Log for any open issues
[ ] Review current Sprint Goals and your pending tasks
```

### 2. Component Ownership Reminder
As Developer 1, you own these components:
- LaTeX Resume Parser
- LaTeX Generator
- Frontend Components for Parser/Generator

### 3. API Boundaries
Ensure you understand the current interfaces between your components and others:
```
[ ] Review Component Boundaries document if needed
[ ] Note any changed interfaces you need to adapt to
```

### 4. Today's Focus
```
[ ] Determine your focus for today's session
[ ] Check if any files you plan to modify are currently being worked on by Developer 2
[ ] Update Communication Log with your planned work
```

## Session End Checklist

### 1. Update Documentation
```
[ ] Update Communication Log with completed work
[ ] If you made design decisions, update Thought Process Journal
[ ] If you modified component interfaces, update Component Boundaries
[ ] If you encountered blockers, update Blocker Log
[ ] If you completed tasks, update Sprint Planning
```

### 2. Code Management
```
[ ] Commit your changes with clear commit messages
[ ] Push your changes to remote repository
[ ] Create pull requests if a feature is complete
```

### 3. Next Session Planning
```
[ ] Note what to focus on next session
[ ] Add any preparation tasks for next time
```

## Quick Project Overview

### Repository Structure
```
resume-optimizer/
├── src/
│   ├── parser/         # YOUR FOCUS: LaTeX resume parsing
│   ├── optimizer/      # SHARED: Content optimization 
│   ├── latex_generator/# YOUR FOCUS: LaTeX document generation
│   ├── ats/            # DEV 2: ATS compatibility
│   ├── feedback/       # SHARED: Feedback processing
│   └── utils/          # SHARED: Utility functions
├── main.py             # DEV 2: FastAPI endpoints
└── templates/          # YOUR FOCUS: LaTeX templates
```

### Current Sprint Focus
- Implementing core functionality for resume parsing and optimization
- Building the basic LaTeX generator for optimized content
- Setting up frontend components for file upload and display

### Important Files to Review
- `src/parser/latex_parser.py` - Your responsibility
- `src/latex_generator/generator.py` - Your responsibility
- `scrum/sprint_planning.md` - Current tasks
- `scrum/communication_log.md` - Developer 2's work

## Update Template for Communication Log

Copy and paste this at the top of the Communication Log when starting:

```
[YYYY-MM-DD] Developer 1
- Current focus: [Brief description of current tasks]
- Files being modified: 
  - [file1]
  - [file2]
- Questions/Blockers: [Any questions or blockers]
- Notes for other developers: [Important information others should know]
```

## Update Template for Thought Process Journal

Copy and paste this when making important decisions:

```
[YYYY-MM-DD] [Decision Title] - Developer 1

## Context
[Brief description of the problem or challenge]

## Options Considered
[List of options that were considered]

## Decision
[The decision that was made]

## Reasoning
[Explanation of why this decision was made]

## Consequences
[Expected impact of this decision]
```

## Update Template for Blocker Log

Copy and paste this when encountering blockers:

```
[YYYY-MM-DD] [Blocker Title] - Developer 1

## Description
[Detailed description of the blocker]

## Impact
[How this blocker impacts the project/timeline]

## Potential Solutions
[List of potential solutions if any]

## Status
Open

## Resolution
[How the blocker was resolved - fill this in when status changes to Resolved]
```

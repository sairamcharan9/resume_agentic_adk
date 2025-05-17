# Developer 2 Session Guide - Resume Optimizer

## Session Start Checklist

### 1. Project Refresh
```
[ ] Review the latest commits in the repository
[ ] Read the Communication Log for Developer 1's recent work
[ ] Check the Blocker Log for any open issues
[ ] Review current Sprint Goals and your pending tasks
```

### 2. Component Ownership Reminder
As Developer 2, you own these components:
- Job Description Analyzer
- ATS Analyzer
- FastAPI Endpoints
- Frontend Components for Job Analysis/ATS

### 3. API Boundaries
Ensure you understand the current interfaces between your components and others:
```
[ ] Review Component Boundaries document if needed
[ ] Note any changed interfaces you need to adapt to
```

### 4. Today's Focus
```
[ ] Determine your focus for today's session
[ ] Check if any files you plan to modify are currently being worked on by Developer 1
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
│   ├── parser/         # DEV 1: LaTeX resume parsing
│   ├── optimizer/      # SHARED: Content optimization 
│   ├── latex_generator/# DEV 1: LaTeX document generation
│   ├── ats/            # YOUR FOCUS: ATS compatibility
│   ├── feedback/       # SHARED: Feedback processing
│   └── utils/          # YOUR FOCUS: Job Analysis utilities
├── main.py             # YOUR FOCUS: FastAPI endpoints
└── templates/          # YOUR FOCUS: Web UI templates
```

### Current Sprint Focus
- Implementing core functionality for job description analysis
- Building the ATS compatibility analyzer
- Setting up API endpoints and web interface

### Important Files to Review
- `src/utils/job_analyzer.py` - Your responsibility
- `src/ats/ats_analyzer.py` - Your responsibility
- `main.py` - Your responsibility
- `scrum/sprint_planning.md` - Current tasks
- `scrum/communication_log.md` - Developer 1's work

## Update Template for Communication Log

Copy and paste this at the top of the Communication Log when starting:

```
[YYYY-MM-DD] Developer 2
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
[YYYY-MM-DD] [Decision Title] - Developer 2

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
[YYYY-MM-DD] [Blocker Title] - Developer 2

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

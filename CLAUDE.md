# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is Anthropic's skills repository for Claude. Skills are modular packages that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations. Each skill is a self-contained folder with a `SKILL.md` file and optional bundled resources.

## Repository Structure

```
skills/               # Individual skill folders (18 total)
├── xlsx/            # Spreadsheet processing (source-available)
├── docx/            # Word document processing (source-available)
├── pptx/            # PowerPoint processing (source-available)
├── pdf/             # PDF processing (source-available)
├── skill-creator/   # Guide for creating skills (Apache 2.0)
├── mcp-builder/     # MCP server creation (Apache 2.0)
└── [12 other example skills]

spec/                # Points to agentskills.io specification
template/            # Basic skill template
.claude-plugin/      # Marketplace configuration for Claude Code
```

## Plugin Collections

The repository defines two plugin collections in `.claude-plugin/marketplace.json`:

1. **document-skills**: xlsx, docx, pptx, pdf (source-available, not open source - reference implementations)
2. **example-skills**: All other skills (Apache 2.0 open source)

## Skill Anatomy

Every skill follows this structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/      # Executable code (Python/Bash) for deterministic operations
    ├── references/   # Documentation loaded into context as needed
    └── assets/       # Files used in output (templates, images, fonts)
```

### SKILL.md Structure

- **Frontmatter**: Only `name` and `description` are read by Claude to determine when the skill triggers. Be comprehensive in the description.
- **Body**: Instructions loaded AFTER the skill triggers. Keep concise - assume Claude is already smart.
- **Compatibility field**: Optional, rarely needed. Use only for environment requirements.

### Bundled Resources Guidelines

- **scripts/**: Use when code is repeatedly rewritten or deterministic reliability is needed. May be executed without loading into context.
- **references/**: Documentation Claude should reference while working. Loaded only when Claude determines it's needed. Avoid duplicating information between SKILL.md and references.
- **assets/**: Files used in output, not loaded into context (templates, images, boilerplate).

## Key Principles

1. **Concise is Key**: Context window is shared. Only add what Claude doesn't already know. Challenge each piece of information.
2. **Avoid Duplication**: Information should live in either SKILL.md or references files, not both. Prefer references for detailed information.
3. **Degrees of Freedom**: Match specificity to task fragility:
   - High freedom (text instructions): Multiple valid approaches
   - Medium freedom (pseudocode/parameterized scripts): Preferred patterns with variation
   - Low freedom (specific scripts): Fragile operations requiring consistency

## Testing Skills

Skills are tested by installing them in Claude Code:

```bash
# Add marketplace
/plugin marketplace add anthropics/skills

# Install plugin
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

Then test by mentioning the skill in conversation (e.g., "Use the PDF skill to extract form fields from file.pdf").

## Python Scripts

Some skills (xlsx, docx, pptx, pdf) include Python scripts in `scripts/` directories. These scripts:
- Are standalone utilities for specific operations (PDF rotation, form filling, spreadsheet recalculation)
- May require dependencies (pypdf, python-pptx, openpyxl, etc.)
- Are designed to be executed directly or loaded by Claude for patching
- Should be kept deterministic and focused on single responsibilities

## License Considerations

- Document skills (xlsx, docx, pptx, pdf): Source-available with LICENSE.txt in each folder
- Example skills: Apache 2.0 (see root LICENSE or individual skill LICENSE.txt)
- Always check LICENSE.txt in skill folders when modifying

## Specification

The Agent Skills specification is maintained at https://agentskills.io/specification (not in this repository).

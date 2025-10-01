# Claude CLI Agent Instructions

**See AGENTS.md for all development standards, practices, and workflow requirements.**

## Claude CLI Tool Capabilities

### Core Strengths
- **Multi-tool parallelization** - Execute multiple operations simultaneously for efficiency
- **Large context processing** - Handle complex multi-file analysis and refactoring tasks
- **Incremental development** - Excel at breaking down complex tasks into manageable phases
- **Pattern synthesis** - Combine and adapt multiple code patterns effectively
- **Context continuity** - Maintain understanding across long development sessions

### Optimal Usage Patterns
- **Complex refactoring** - Multi-file changes with dependency tracking
- **System integration** - Understanding how components interact across a project
- **Documentation analysis** - Synthesizing information from multiple sources
- **Iterative development** - Building features incrementally with validation at each step
- **Code review and analysis** - Comprehensive assessment of existing codebases

### Interface Optimization
- **Use TodoWrite tool** for complex multi-step tasks to maintain progress visibility
- **Leverage parallel tool execution** - Call multiple bash commands, file operations simultaneously  
- **Batch related operations** - Group similar tasks for efficient execution
- **Request explicit confirmation** before proceeding to next major task phase

### Session Management
- **Check project state first** - Review TASKS.md, git status, current code quality
- **Maintain task continuity** - Update TASKS.md chronologically as work progresses  
- **Validate before completion** - Run quality checks before marking tasks complete
- **Ask permission for scope changes** - Confirm before expanding or shifting task focus

## When to Use Claude CLI
- Multi-file refactoring and large-scale code changes
- Complex system architecture analysis and design
- Integration of multiple technologies or services
- Long-running development tasks requiring sustained context
- Code review and optimization across entire projects
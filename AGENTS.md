# Personal Development Standards

## project-specific intructions
- Refer to the **AssemblyAI Documentation** as necessary for information on how to work with it, including the [docs](https://www.assemblyai.com/docs), [API Reference](https://www.assemblyai.com/docs/api-reference), [Cookbooks](https://www.assemblyai.com/docs/guides); you can use your web search/crawl capabilities as necessary to dig into this documentation (or whatever other documentation we need at a point)

## Core Tooling Standards

### Python Environment Management
- **Always use `uv`** for Python environment management and dependency handling
- **Always lock dependencies** with `uv.lock` file for reproducible builds
- **Standard commands**:
  ```bash
  uv sync                    # Sync environment with pyproject.toml and uv.lock
  uv add package-name        # Add runtime dependency (updates lock)
  uv add --group dev pytest  # Add development dependency (updates lock)
  uv run <command>          # Execute commands in project environment
  uv lock                   # Update lock file after manual pyproject.toml changes
  ```
- **Project structure**: All projects use `pyproject.toml` (never requirements.txt)
- **Lock file management**: Commit `uv.lock` to ensure reproducible environments
- **If legacy requirements.txt needed**: Generate from pyproject.toml, don't maintain manually

### Task Automation with Just
- **All repetitive commands wrapped in `just` recipes**
- **Standard justfile patterns**:
  ```bash
  just dev      # Start development environment
  just test     # Run test suite
  just check    # Run linting and type checking
  just fix      # Auto-fix code quality issues
  just build    # Build container images
  just run      # Run application 
  ```

  - reference the [just programmer's manual](https://just.systems/man/en/) whenever you need any clarification how to work with Just (especially when it comes to parameters, since you seem to often get that wrong)

### Container-First Development
- **Rancher Desktop** as container runtime
- **Standard pattern**: `just` → `docker-compose` → application
- **Local data processing**: Mount volumes for data input/output
- **Development workflow**: Applications run in containers from day one

### Code Quality Standards
- **Linting**: `ruff` for Python code formatting and linting
- **Type checking**: `pyright` for static type analysis
- **Testing**: `pytest` with >80% coverage requirement
- **Quality gates**: All checks must pass before task completion

## Architecture Patterns

### Error Handling and Resilience
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Standard retry pattern for external services
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((APIError, TimeoutError, ConnectionError))
)
def call_external_service(data):
    # Implementation
    pass

# Async retry pattern
from tenacity import AsyncRetrying
async def async_service_call(data):
    async for attempt in AsyncRetrying(
        wait=wait_exponential(multiplier=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((APIError, TimeoutError))
    ):
        with attempt:
            return await self._make_api_call(data)
```

### Configuration Management
```python
from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict
from functools import lru_cache

class AppConfig(BaseSettings):
    """Application configuration with environment variable support."""
    
    service_name: str = Field(default="my-service")
    log_level: str = Field(default="INFO")
    api_key: str = Field(default="")
    database_url: str = Field(default="")
    
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8"
    )

@lru_cache()
def get_config() -> AppConfig:
    return AppConfig()
```

### Structured Logging with Correlation IDs
```python
import contextvars
import uuid
import structlog

# Correlation ID context
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id')

def generate_correlation_id() -> str:
    return str(uuid.uuid4())

def get_correlation_id() -> str:
    return correlation_id.get(generate_correlation_id())

def set_correlation_id(cid: str) -> None:
    correlation_id.set(cid)

# Structured logging setup
logger = structlog.get_logger(__name__)

def log_with_correlation(message: str, **kwargs):
    logger.info(message, correlation_id=get_correlation_id(), **kwargs)
```

### Resource Management
```python
import asyncio
from contextlib import asynccontextmanager
from typing import Any, List

class AsyncResourceManager:
    """Manage async resources with proper cleanup."""
    
    def __init__(self, cleanup_timeout: float = 5.0):
        self._resources: List[Any] = []
        self._cleanup_timeout = cleanup_timeout
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        cleanup_tasks = []
        for resource in self._resources:
            if hasattr(resource, 'aclose'):
                cleanup_tasks.append(resource.aclose())
        
        if cleanup_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cleanup_tasks, return_exceptions=True),
                    timeout=self._cleanup_timeout
                )
            except asyncio.TimeoutError:
                logger.warning("Resource cleanup timeout", 
                             resource_count=len(cleanup_tasks))
        
        self._resources.clear()
    
    def register_resource(self, resource: Any) -> Any:
        self._resources.append(resource)
        return resource
```

## AI Development Patterns

### AI Service Integration
```python
from pydantic import BaseModel
from typing import Optional, List, Any
import httpx

class AIServiceConfig(BaseSettings):
    api_key: str = Field(default="")
    base_url: str = Field(default="https://api.service.com")
    timeout: float = Field(default=30.0)
    
    model_config = SettingsConfigDict(env_prefix="AI_SERVICE_")

class AIResponse(BaseModel):
    result: Any
    confidence: float
    processing_time_ms: int
    model_version: str

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30)
)
async def call_ai_service(
    prompt: str, 
    config: Optional[AIServiceConfig] = None
) -> AIResponse:
    config = config or get_ai_config()
    
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        response = await client.post(
            f"{config.base_url}/analyze",
            json={"prompt": prompt},
            headers={"Authorization": f"Bearer {config.api_key}"}
        )
        response.raise_for_status()
        return AIResponse(**response.json())
```

### Batch Processing Patterns
```python
from typing import List, TypeVar, Callable, Awaitable
import asyncio
from itertools import islice

T = TypeVar('T')
R = TypeVar('R')

async def process_in_batches(
    items: List[T],
    processor: Callable[[List[T]], Awaitable[List[R]]],
    batch_size: int = 50,
    max_concurrent: int = 5
) -> List[R]:
    """Process items in batches with concurrency control."""
    
    def batch_iterator(items, batch_size):
        it = iter(items)
        while batch := list(islice(it, batch_size)):
            yield batch
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(batch):
        async with semaphore:
            return await processor(batch)
    
    tasks = [
        process_batch(batch) 
        for batch in batch_iterator(items, batch_size)
    ]
    
    batch_results = await asyncio.gather(*tasks)
    
    # Flatten results
    results = []
    for batch_result in batch_results:
        results.extend(batch_result)
    
    return results
```

## Development Workflow

### Knowledge Source Priority
1. **Project Documentation** - Check local docs, README, TASKS.md first
2. **Official Documentation** - Consult official docs for libraries/services
3. **MCP Integration** - Leverage MCP tools for research and code analysis
4. **General Internet** - Stack Overflow, community resources as final fallback

### Task Management
- **Track work in project-local `TASKS.md`**
- **ALWAYS update TASKS.md when adding new work** - including features, requirements, or tasks added on the fly
- **Chronological task list** maintaining order of events
- **Task states**: `[ ]` planned, `[~]` work-in-progress, `[x]` completed
- **Focus on objectives and outcomes**, not implementation details
- **Flexible ordering**: Insert new tasks in appropriate chronological position
- **Real-time updates**: Update TASKS.md immediately when new work is identified or started

#### TASKS.md Format
```markdown
# Project Tasks

- [x] Project setup and containerization
  - [x] Initialize uv project with pyproject.toml
  - [x] Create docker-compose.yml and Dockerfile
  - [x] Set up justfile with basic recipes
- [x] Database schema design
- [~] API endpoint development
  - [x] Create FastAPI application structure
  - [x] Add health check endpoint
  - [~] Implement CRUD operations
  - [ ] Add request validation
- [ ] Implement user authentication system
  - [ ] Set up OAuth2 flow
  - [ ] Create user database models
  - [ ] Add JWT token handling
- [ ] Add data processing pipeline
  - [ ] Design batch processing workflow
  - [ ] Implement error handling and retries
```

### Quality Gates
Before marking any task complete:
- [ ] All tests passing (`just test`)
- [ ] No linting errors (`just check`)
- [ ] No type checking errors
- [ ] Code coverage >80%
- [ ] Documentation updated for significant changes
- [ ] Container builds successfully (`just build`)

### Standard Project Structure
```
project/
├── src/                    # Application source code
├── tests/                  # Test files
├── data/                   # Local data for processing (mounted in containers)
├── docker/                 # Docker configuration
├── .env.example           # Environment variable template
├── docker-compose.yml     # Container orchestration
├── justfile              # Task automation
├── pyproject.toml        # Python dependencies and config
├── README.md             # Project documentation
└── TASKS.md              # Task tracking
```

### Container Development Patterns
```yaml
# docker-compose.yml example
version: '3.8'

services:
  app:
    build: 
      context: .
      dockerfile: docker/Dockerfile
    volumes:
      - ./data:/app/data:rw        # Local data processing
      - ./src:/app/src:ro          # Source code (development)
    environment:
      - APP_LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    depends_on:
      - database

  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Type Safety and Error Prevention

### Common Patterns
```python
from typing import Optional, Union, List, Any
from pydantic import BaseModel, Field

# Always check Optional types before use
result: Optional[dict] = some_function()
if result is not None:
    data = result["key"]

# Or use assertions for type narrowing
result = some_function()
assert result is not None  # For type checker
data = result["key"]

# Provide all required parameters to Pydantic models
class DataModel(BaseModel):
    name: str
    value: int
    metadata: Optional[dict] = None
    tags: List[str] = Field(default_factory=list)

# Proper error handling with context
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed", error=str(e), correlation_id=get_correlation_id())
    raise ProcessingError(f"Failed to process: {e}") from e
```

### Professional Standards
- **Commit messages**: Focus on technical changes, avoid AI tool references
- **Code comments**: Explain business logic, not implementation details
- **Error messages**: Use business-relevant language
- **Documentation**: Keep professional and tool-agnostic

### Git Commit Conventions
- **Follow conventional commit format**: `type(scope): description`
- **Standard types**:
  - `feat:` - New features (usually includes docs and tests)
  - `fix:` - Bug fixes
  - `docs:` - Documentation changes only
  - `style:` - Code style changes (formatting, etc.)
  - `refactor:` - Code refactoring without behavior changes
  - `test:` - Adding or updating tests
  - `chore:` - Maintenance tasks, dependency updates
- **Commit message guidelines**:
  - **Outcome/result oriented** - Focus on what was achieved, not implementation details
  - **Present tense** - "Add feature" not "Added feature"
  - **Lowercase** - No capital letters after the colon
  - **No period** - Don't end with a period
  - **50 char limit** - Keep the subject line under 50 characters
- **Multiple commits**: If changes span multiple types, break into separate commits
- **Exception**: `feat:` commits often include associated `docs:` and `test:` changes in the same commit

## MCP Integration

### Enhanced Development Workflow
- **Use MCP tools for research** - GitHub integration, documentation analysis, code exploration
- **Leverage official sources first** - Access authoritative documentation through MCP before general web search
- **Code analysis and refactoring** - Use MCP filesystem tools for project-wide analysis
- **Documentation generation** - Generate and maintain project documentation using MCP capabilities

### MCP Usage Patterns
```bash
# Research patterns with MCP
# 1. Check official repositories for implementation patterns
# 2. Analyze existing codebases for similar solutions
# 3. Review documentation through MCP tools
# 4. Generate boilerplate code based on official examples
```

### Knowledge Source Priority (with MCP)
1. **Project Documentation** - Local docs, README, TASKS.md, existing code
2. **MCP-Enhanced Research** - Official docs, GitHub repos, authoritative sources via MCP
3. **Official Documentation** - Framework and library documentation
4. **General Internet** - Stack Overflow, community resources as final fallback

### Configuration Example
```json
// .mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"]
    },
    "web": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-web"]
    }
  }
}
```

## Quick Reference Commands

```bash
# Project initialization
uv init --python 3.11
uv add fastapi uvicorn pydantic-settings structlog tenacity pytest

# Development workflow
just dev        # Start development environment
just test       # Run tests with coverage
just check      # Lint and type check
just fix        # Auto-fix issues
just build      # Build containers
just deploy     # Deploy application

# Quality validation
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80
uv run ruff check .
uv run pyright
```

This framework provides the foundation for maintainable, production-ready Python applications with AI integration, containerized development, and proper engineering practices.
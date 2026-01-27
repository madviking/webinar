# V2 Agent Implementation Notes

## Minimal Pattern
```python
from typing import Dict
from src.agents.base.agent_base import AgentBase
from src.py_models.some_domain import MyResultModel

class MyAgent(AgentBase):
    async def analyze(self, text: str) -> Dict:
        result = await self.run(
            prompt=self.get_prompt("analyze", {"text": text}),
            pydantic_model=MyResultModel,
        )
        return result  # Raw dict/model; framework maps to assets
```

## Rules of Thumb
- Return raw dicts or Pydantic models; do not construct assets manually.
- Avoid overriding execute() unless multi-asset orchestration is required.
- Keep prompts in config/prompt providers, not in code.
- Models are defined in src/py_models and imported from there.
- Keep agent names functional and model-agnostic.
- For file processing, pass file_path directly to LLM; do not pre-parse files.

## When You Must Override execute()
- Multiple input assets with custom selection or aggregation.
- Custom asset handling that cannot be expressed via field_mapping.

## See Also
- docs/development-guides/agents/development-guide.md
- docs/development-guides/swarms/implementation-rules.md

# V2 agent config.yaml Cheat Sheet

## Minimal Skeleton
```yaml
format_version: "2"
name: my_agent
agent_class: "MyAgent"

# Flexible input requirements (choose one)
input_assets:
  required_fields: [email, name]
# or
# input_assets: []  # Accept any asset type
# or
# input_assets: [ContactAsset]  # Strict types

# Output behavior
output_assets: []  # Passthrough (enrich input)
# or
# output_assets: [ResultAsset]

produces_assets:
  - asset_type: ResultAsset
    field_mapping:
      "*": "*"
```

## Key Rules
- Model/provider choices are config parameters, never in filenames/classes.
- Prompts belong in config or prompt providers, not hardcoded in code.
- Models live in src/py_models; do not create agent-local models.py.

## Flexible Assets
- required_fields uses dot notation for nested fields.
- Use minimal required fields to increase reuse.
- output_assets: [] means passthrough/enrichment.

## LLM Configuration (Examples)
```yaml
default_model: "openai/chat/gpt-4o-mini"
fallback_model: "anthropic/chat/claude-3-7-sonnet"
fallback_chain:
  - model: "anthropic/chat/claude-3-7-sonnet"
  - model: "openai/chat/gpt-4o-mini"
```

## See Also
- docs/development-guides/agents/agents-yaml.md
- docs/development-guides/agents/flexible-assets.md

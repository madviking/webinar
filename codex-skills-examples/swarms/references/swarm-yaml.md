# V2 swarm.yaml Cheat Sheet

## Minimal Skeleton
```yaml
format_version: "2"
name: my_swarm
description: "What this swarm does"
version: "1.0.0"

configuration:
  strict_mode: false
  log_field_mapping_errors: true
  continue_on_error: true

completion:
  required_asset: FinalAssetType

tasks:
  task_name:
    agent: agent_identifier
    input_assets: [InputAssetType]
    output_assets: [OutputAssetType]
    triggers:
      - asset: InputAssetType
```

## Task Essentials
- tasks.<task_name>.agent: V2 agent name.
- input_assets: Asset types (or patterns) the task consumes.
- triggers: When to run. Use:
  - asset: Single asset trigger
  - all_assets: Require a set of assets
- output_assets: Assets created by this task.
- field_mapping: Map agent outputs into asset fields.
- agent_configuration: Per-task overrides.
- metadata: Optional documentation and HITL settings.

## Field Mapping
- Direct mapping: `target_field: source_field`
- Nested mapping: `target: nested.path`
- Array mapping: `items[].field: source_field`
- Copy from input asset: `"__source_asset__(AssetType).all": "."`
- Wildcard: `"*": "*"` (explicit keys override wildcard)

## Output Assets Patterns
- Simple list: `output_assets: [MyAsset]`
- Object format:
  ```yaml
  output_assets:
    - asset_type: MyAsset
      asset_name_suffix: "_variant"
  ```
- Conditional creation:
  ```yaml
  output_assets:
    - asset_type: VendorEmailAsset
      conditions:
        classification: { eq: "Vendor communication" }
  ```
- Visual-only hint:
  ```yaml
  output_assets_guide: [DownstreamAsset]
  ```

## Completion
- Single asset:
  ```yaml
  completion:
    required_asset: FinalAssetType
  ```
- Composite:
  ```yaml
  completion:
    any:
      - required_asset: A
      - required_asset: B
    conditions:
      - type: task_result_condition
        task_name: classify
        conditions:
          classification: { eq: "Other" }
  ```

## Common Pitfalls
- Missing format_version "2".
- No trigger for a task (task never runs).
- output_assets defined but no field_mapping when shapes differ.
- Using model names in agent/asset/swarm names (avoid).
- Creating new agents instead of configuring existing ones.

## See Also
- docs/development-guides/swarms/yaml-reference.md
- docs/development-guides/swarms/output-assets-configuration.md
- docs/development-guides/swarms/implementation-rules.md

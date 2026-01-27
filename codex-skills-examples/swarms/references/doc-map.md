# Swarm Development Doc Map

Open only what you need.

## Swarms
- docs/development-guides/swarms/yaml-reference.md: Full V2 swarm.yaml schema, triggers, completion, field mapping.
- docs/development-guides/swarms/implementation-rules.md: Non-negotiable V2 rules (model-agnostic, no hardcoded prompts).
- docs/development-guides/swarms/output-assets-configuration.md: output_assets formats, suffixes, output_assets_guide.
- docs/development-guides/swarms/CONFIG_PASSING_GUIDE.md: How swarm task config reaches agents.
- docs/development-guides/swarms/asset-creation-guide.md: Asset lifecycle and creation options.
- docs/development-guides/swarms/asset-creation-quickstart.md: Fast asset creation examples.
- docs/development-guides/swarms/development-guide.md: End-to-end walkthrough (scan for patterns).

## Agents
- docs/development-guides/agents/development-guide.md: V2 agent structure and minimal pattern.
- docs/development-guides/agents/agents-yaml.md: config.yaml reference for V2 agents.
- docs/development-guides/agents/flexible-assets.md: required_fields, passthrough mode, field validation.
- docs/development-guides/agents/testing-guide.md: V2 fixture-based tests (no mocks).
- src/agents/testing/README.md: Test runner details.

## Debugging and CLI
- docs/troubleshooting/swarm-debug-guide.md: run-sync, analyze, triggers, run inspection.
- docs/cli-reference/commands.md: CLI command index.
- docs/cli/SWARM_CLI_REFERENCE.md: Full swarm CLI reference.

## Structure and Catalogs
- src/swarm_manager/swarms_v2/README.md: Swarm directory structure.
- docs/existing-agents.md: Inventory of V2 agents to reuse.

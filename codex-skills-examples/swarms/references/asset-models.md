# Asset Models Quick Notes

## Where Assets Live
- Define assets in src/py_models. Discovery is automatic.
- Do not add agent-local models.py.

## Base Types
- DataAsset: structured data.
- FileAsset: file-based data (requires file_path, original_filename, file_size, mime_type).
- ReportAsset: generated reports.

## FileAsset Required Fields
When inheriting from FileAsset, provide:
- asset_name
- file_path
- original_filename
- file_size
- mime_type

## Best Practices
- Keep assets single-purpose and named by content, not process.
- Use consistent field names to enable flexible agents.
- Prefer lists with Field(default_factory=list) to avoid mutable defaults.

## See Also
- docs/development-guides/swarms/asset-creation-guide.md
- docs/development-guides/swarms/asset-creation-quickstart.md

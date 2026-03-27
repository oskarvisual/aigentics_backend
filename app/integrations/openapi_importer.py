from __future__ import annotations

from typing import Any

import yaml

from app.schemas.integration import OpenAPIToolDraft


class OpenAPIImporter:
    """Normalize OpenAPI operations into internal tool drafts."""

    def parse(self, raw_spec: str) -> list[OpenAPIToolDraft]:
        spec = yaml.safe_load(raw_spec)
        paths: dict[str, Any] = spec.get("paths", {})
        drafts: list[OpenAPIToolDraft] = []
        for path, operations in paths.items():
            for method, operation in operations.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                    continue
                operation_id = operation.get("operationId", f"{method}_{path}".replace("/", "_"))
                name = operation.get("summary") or operation_id.replace("_", " ").title()
                description = operation.get("description") or operation.get("summary") or name
                schema = {
                    "parameters": operation.get("parameters", []),
                    "requestBody": operation.get("requestBody", {}),
                }
                drafts.append(
                    OpenAPIToolDraft(
                        operation_id=operation_id,
                        path=path,
                        method=method.upper(),
                        name=name,
                        description=description,
                        input_schema=schema,
                    )
                )
        return drafts


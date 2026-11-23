"""openapi.json -> docslice.postman_collection.json (Postman collection v2.1). Run: python build_postman.py"""
import json
from pathlib import Path

HERE = Path(__file__).parent
# a ready request body for the endpoints people try first
EXAMPLE_FIELDS = {
    ("/v1/convert", "post"): {"format": "json", "schema": json.dumps({
        "type": "object", "properties": {"invoice_number": {"type": "string"}, "date": {"type": "string"},
                                         "total": {"type": "number"}}})},
    ("/v1/api-keys", "post"): None,
}


def resolve(spec, node):
    while isinstance(node, dict) and "$ref" in node:
        node = spec["components"]["schemas"][node["$ref"].split("/")[-1]]
    return node


def request_item(spec, path, method, op):
    url_path = path.replace("{", ":").replace("}", "")
    params = op.get("parameters", [])
    item = {
        "name": op.get("summary") or f"{method.upper()} {path}",
        "request": {
            "method": method.upper(),
            "description": op.get("description", ""),
            "url": {
                "raw": "{{baseUrl}}" + url_path,
                "host": ["{{baseUrl}}"],
                "path": [p for p in url_path.split("/") if p],
                "variable": [{"key": p["name"], "value": "", "description": p.get("description", "")}
                             for p in params if p["in"] == "path"],
                "query": [{"key": p["name"], "value": str(p.get("schema", {}).get("default", "")), "disabled": True,
                           "description": p.get("description", "")} for p in params if p["in"] == "query"],
            },
        },
    }
    if not op.get("security") and path == "/health":
        item["request"]["auth"] = {"type": "noauth"}
    body = op.get("requestBody", {}).get("content", {})
    if "multipart/form-data" in body:
        schema = resolve(spec, body["multipart/form-data"]["schema"])
        filled = EXAMPLE_FIELDS.get((path, method)) or {}
        form = []
        for name, prop in schema.get("properties", {}).items():
            prop = resolve(spec, prop)
            is_file = prop.get("contentMediaType") or prop.get("format") == "binary" or \
                (prop.get("type") == "array" and resolve(spec, prop.get("items", {})).get("contentMediaType"))
            entry = {"key": name, "type": "file" if is_file else "text", "description": prop.get("description", "")}
            if is_file:
                entry["src"] = []
            else:
                entry["value"] = filled.get(name, str(prop.get("default", "")))
                entry["disabled"] = name not in filled and name not in schema.get("required", []) and "default" not in prop
            form.append(entry)
        item["request"]["body"] = {"mode": "formdata", "formdata": form}
    elif "application/json" in body:
        schema = resolve(spec, body["application/json"]["schema"])
        sample = {k: "" for k in schema.get("properties", {})}
        item["request"]["header"] = [{"key": "Content-Type", "value": "application/json"}]
        item["request"]["body"] = {"mode": "raw", "raw": json.dumps(sample, indent=2)}
    return item


def main():
    spec = json.loads((HERE / "openapi.json").read_text(encoding="utf-8"))
    folders = {}
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            tag = (op.get("tags") or ["General"])[0]
            folders.setdefault(tag, []).append(request_item(spec, path, method, op))
    collection = {
        "info": {"name": "DocSlice API", "description": spec["info"]["description"],
                 "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{apiKey}}", "type": "string"}]},
        "variable": [{"key": "baseUrl", "value": spec["servers"][0]["url"]},
                     {"key": "apiKey", "value": "", "description": "Your ds_live_... key: https://api.docslice.app/app#signup"}],
        "item": [{"name": tag, "item": items} for tag, items in folders.items()],
    }
    out = HERE / "docslice.postman_collection.json"
    out.write_text(json.dumps(collection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sum(len(i) for i in folders.values())} requests -> {out.name}")


if __name__ == "__main__":
    main()

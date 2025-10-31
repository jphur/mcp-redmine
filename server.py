# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import yaml
import pathlib
from urllib.parse import urljoin
from dotenv import load_dotenv
import httpx
from fastmcp import FastMCP, Context

load_dotenv()

current_dir = pathlib.Path(__file__).parent
with open(current_dir / "redmine_openapi.yml") as f:
    SPEC = yaml.safe_load(f)

REDMINE_URL = os.environ.get("REDMINE_URL")
if not REDMINE_URL:
    raise ValueError("REDMINE_URL environment variable is required")

REDMINE_REQUEST_INSTRUCTIONS = ""
if "REDMINE_REQUEST_INSTRUCTIONS" in os.environ:
    path = os.environ["REDMINE_REQUEST_INSTRUCTIONS"]
    if os.path.exists(path):
        with open(path) as f:
            REDMINE_REQUEST_INSTRUCTIONS = f.read()

### 🔧 Generic request function ###
def request_redmine(path: str, api_key: str, method: str = "get",
                    data: dict | None = None, params: dict | None = None,
                    content_type: str = "application/json",
                    content: bytes | None = None) -> dict:
    headers = {"X-Redmine-API-Key": api_key, "Content-Type": content_type}
    url = urljoin(REDMINE_URL, path.lstrip("/"))

    try:
        response = httpx.request(method=method.lower(), url=url, json=data, params=params,
                                 headers=headers, content=content, timeout=60.0)
        response.raise_for_status()
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return {"status_code": response.status_code, "body": body, "error": ""}
    except Exception as e:
        return {
            "status_code": getattr(getattr(e, "response", None), "status_code", 0),
            "body": getattr(getattr(e, "response", None), "text", None),
            "error": f"{e.__class__.__name__}: {e}",
        }

def yd(obj):  # YAML helper
    return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=4096)

### 🧠 Server initialization ###
mcp = FastMCP("Redmine MCP server")

### 🧰 Tools ###
@mcp.tool()
def redmine_request(ctx: Context, path: str, method: str = "get",
                    data: dict | None = None, params: dict | None = None) -> str:
    """
    Makes a request to the Redmine API.
    Requires the client (LibreChat) to send the header:
        X-Redmine-API-Key: <your_personal_key>
    """
    api_key = ctx.request_context.request.headers.get("X-Redmine-API-Key")
    if not api_key:
        return yd({"status_code": 0, "body": None,
                   "error": "Missing X-Redmine-API-Key header (Redmine personal key)"})
    return yd(request_redmine(path, api_key, method, data, params))

@mcp.tool()
def redmine_paths_list(ctx: Context) -> str:
    """Returns the list of available endpoints in the OpenAPI specification"""
    return yd(list(SPEC["paths"].keys()))

@mcp.tool()
def redmine_paths_info(ctx: Context, path_templates: list[str]) -> str:
    """Returns detailed information about specific endpoints"""
    info = {p: SPEC["paths"][p] for p in path_templates if p in SPEC["paths"]}
    return yd(info)

@mcp.tool()
def redmine_upload(ctx: Context, file_path: str, description: str | None = None) -> str:
    """Uploads a file to Redmine"""
    api_key = ctx.request.headers.get("X-Redmine-API-Key")
    if not api_key:
        return yd({"status_code": 0, "body": None, "error": "Missing X-Redmine-API-Key header"})
    try:
        path = pathlib.Path(file_path).expanduser()
        assert path.is_absolute(), f"Invalid path: {file_path}"
        assert path.exists(), f"File does not exist: {file_path}"

        params = {"filename": path.name}
        if description:
            params["description"] = description

        with open(path, "rb") as f:
            file_content = f.read()

        result = request_redmine("uploads.json", api_key, "post", params=params,
                                 content_type="application/octet-stream", content=file_content)
        return yd(result)
    except Exception as e:
        return yd({"status_code": 0, "body": None, "error": str(e)})

def main():
    mcp.run(transport="http", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

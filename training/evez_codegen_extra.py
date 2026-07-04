"""
EVEZ Code Generator v2.0 — Additional Generators
React components, middleware, SQL, Docker, FastAPI, fixtures, scripts, configs.

These generators are mixed into the CodeGenerator class via:
    from evez_codegen_extra import ExtraGenerators
    class CodeGenerator(ExtraGenerators): ...
"""

import json

class ExtraGenerators:

    def gen_react_component(self, name: str, props: str = "", hooks: str = "",
                            styled: bool = True, ts: bool = True) -> str:
        prop_list = [p.strip() for p in props.split(",") if p.strip()] if props else []
        prop_str = ", ".join(prop_list) if prop_list else ""
        hook_list = [h.strip() for h in hooks.split(",") if h.strip()] if hooks else []
        cn = name[0].upper() + name[1:] if name else "Component"
        L = ['import React, { useState, useEffect, useRef, useMemo, useCallback } from "react";', '']
        if ts and prop_list:
            L.append(f'interface {cn}Props {{')
            for p in prop_list:
                if ":" in p:
                    fn, ft = p.split(":", 1)
                    tt = {"str":"string","int":"number","bool":"boolean","func":"() => void","array":"any[]"}.get(ft.strip().lower(), "any")
                    L.append(f'  {fn.strip()}: {tt};')
                else:
                    L.append(f'  {p}: any;')
            L.append('}')
            L.append('')
        pt = f"{{ {prop_str} }}: {cn}Props" if ts and prop_list else f"{{ {prop_str} }}" if prop_str else ""
        L.append(f'export const {cn} = ({pt}) => {{')
        if not hook_list or "useState" in hook_list:
            L.append('  const [data, setData] = useState<any>(null);')
        if not hook_list or "useEffect" in hook_list:
            L.append('  const [loading, setLoading] = useState(true);')
            L.append('')
            L.append('  useEffect(() => {')
            L.append('    // TODO: Fetch data')
            L.append('    setLoading(false);')
            L.append('  }, []);')
        for h in hook_list:
            if h == "useRef":
                L.append('  const ref = useRef<HTMLDivElement>(null);')
            elif h == "useMemo":
                L.append('  const computed = useMemo(() => data, [data]);')
            elif h == "useCallback":
                L.append('  const handleClick = useCallback(() => {')
                L.append('    // TODO: Handle click')
                L.append('  }, []);')
        L.append('')
        L.append('  if (loading) return <div>Loading...</div>;')
        L.append('')
        if styled:
            L.append('  return (')
            L.append('    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>')
            L.append(f'      <h1>{cn}</h1>')
            L.append('      <p>{/* TODO: Render content */}</p>')
            L.append('    </div>')
            L.append('  );')
        else:
            L.append('  return (')
            L.append('    <div>')
            L.append(f'      <h1>{cn}</h1>')
            L.append('      <p>{/* TODO: Render content */}</p>')
            L.append('    </div>')
            L.append('  );')
        L.append('};')
        return "\n".join(L)

    def gen_middleware(self, name: str, framework: str = "express", ts: bool = True) -> str:
        name = name or "authMiddleware"
        if framework.lower() == "deno":
            L = [f'// {name} - Deno middleware (EVEZ)',
                f'export async function {name}(req: Request, next: () => Promise<Response>): Promise<Response> {{',
                '  const authHeader = req.headers.get("Authorization");',
                '  if (!authHeader?.startsWith("Bearer ")) {',
                '    return new Response(JSON.stringify({ error: "Unauthorized" }),',
                '      { status: 401, headers: { "Content-Type": "application/json" } });',
                '  }',
                '  const token = authHeader.slice(7);',
                '  // TODO: Validate token',
                '  return next();',
                '}']
        elif ts:
            L = [f'// {name} - Express middleware (EVEZ)',
                'import { Request, Response, NextFunction } from "express";',
                '',
                f'export function {name}(req: Request, res: Response, next: NextFunction) {{',
                '  const authHeader = req.headers.authorization;',
                '  if (!authHeader?.startsWith("Bearer ")) {',
                '    return res.status(401).json({ error: "Unauthorized" });',
                '  }',
                '  const token = authHeader.split(" ")[1];',
                '  // TODO: Validate token',
                '  (req as any).token = token;',
                '  next();',
                '}']
        else:
            L = [f'// {name} - Express middleware (EVEZ)',
                f'function {name}(req, res, next) {{',
                '  const authHeader = req.headers.authorization;',
                '  if (!authHeader?.startsWith("Bearer ")) {',
                '    return res.status(401).json({ error: "Unauthorized" });',
                '  }',
                '  req.token = authHeader.split(" ")[1];',
                '  next();',
                '}',
                '',
                f'module.exports = {name};']
        return "\n".join(L)

    def gen_sql_schema(self, table: str, fields: str = "", db: str = "postgres") -> str:
        fl = [f.strip() for f in fields.split(",") if f.strip()] if fields else ["name:str", "created_at:datetime"]
        t = table.lower()
        tm = {"str":"VARCHAR(255)","string":"VARCHAR(255)","text":"TEXT","int":"INTEGER","integer":"INTEGER",
              "float":"REAL","bool":"BOOLEAN","boolean":"BOOLEAN","datetime":"TIMESTAMP","date":"DATE",
              "uuid":"UUID","json":"JSONB" if db=="postgres" else "TEXT"}
        L = [f'-- {table} schema - generated by EVEZ', f'-- Database: {db}', '',
             f'CREATE TABLE IF NOT EXISTS {t} (',
             f'    id {"UUID DEFAULT gen_random_uuid()" if db=="postgres" else "TEXT PRIMARY KEY"} PRIMARY KEY,']
        for f in fl:
            if ":" in f:
                fn, ft = f.split(":", 1)
                L.append(f'    {fn.strip()} {tm.get(ft.strip().lower(), "VARCHAR(255)")},')
            else:
                L.append(f'    {f} VARCHAR(255),')
        L.extend(['    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
                  '    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP', ');', ''])
        for f in fl[:3]:
            fn = f.split(":")[0].strip()
            if fn != "id":
                L.append(f'CREATE INDEX IF NOT EXISTS idx_{t}_{fn} ON {t}({fn});')
        fl0 = fl[0].split(":")[0].strip()
        L.extend(['', '-- CRUD', '-- Create',
                  f'INSERT INTO {t} ({", ".join(f.split(":")[0].strip() for f in fl)})',
                  f'VALUES ({", ".join("$"+str(i+1) for i in range(len(fl)))}) RETURNING id;', '',
                  '-- Read', f'SELECT * FROM {t} WHERE id = $1;', '',
                  '-- List', f'SELECT * FROM {t} ORDER BY created_at DESC LIMIT $1 OFFSET $2;', '',
                  '-- Update', f'UPDATE {t} SET {fl0} = $1 WHERE id = $2 RETURNING *;', '',
                  '-- Delete', f'DELETE FROM {t} WHERE id = $1 RETURNING id;'])
        return "\n".join(L)

    def gen_dockerfile(self, app_name="app", base="python:3.12-slim", port=8000, entrypoint="") -> str:
        entry = entrypoint or "python3 main.py"
        is_py = "python" in base
        L = [f'# {app_name} Dockerfile - generated by EVEZ', f'FROM {base}', '', 'WORKDIR /app', '']
        if is_py:
            L.extend(['RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl',
                      'COPY requirements.txt .', 'RUN pip install --no-cache-dir -r requirements.txt', ''])
        else:
            L.extend(['COPY package*.json ./', 'RUN npm ci --production', ''])
        parts = entry.split()
        cmd = 'CMD ["' + '","'.join(parts) + '"]'
        L.extend(['COPY . .', f'EXPOSE {port}',
                  f'HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:{port}/health || exit 1',
                  'RUN useradd -m -u 1000 appuser', 'USER appuser', cmd])
        return "\n".join(L)

    def gen_docker_compose(self, services="web,db,redis", app_name="app") -> str:
        svcs = [s.strip() for s in services.split(",") if s.strip()]
        L = ['# docker-compose.yml - generated by EVEZ', 'version: "3.9"', '', 'services:']
        for s in svcs:
            if s in ("web", "app", "api"):
                L.extend([f'  {s}:', '    build: .', '    ports: ["8000:8000"]', '    environment:',
                          f'      - DATABASE_URL=postgresql://postgres:password@db:5432/{app_name}',
                          '      - REDIS_URL=redis://redis:6379', '    depends_on: [db, redis]',
                          '    restart: unless-stopped', ''])
            elif s in ("db", "postgres", "database"):
                L.extend([f'  {s}:', '    image: postgres:16-alpine',
                          f'    environment: {{ POSTGRES_DB: {app_name}, POSTGRES_PASSWORD: password }}',
                          f'    volumes: ["{s}_data:/var/lib/postgresql/data"]',
                          '    ports: ["5432:5432"]', '    restart: unless-stopped', ''])
            elif s == "redis":
                L.extend(['  redis:', '    image: redis:7-alpine', '    ports: ["6379:6379"]',
                          '    volumes: ["redis_data:/data"]', '    restart: unless-stopped', ''])
            elif s in ("nginx", "proxy"):
                L.extend(['  nginx:', '    image: nginx:alpine', '    ports: ["80:80", "443:443"]',
                          '    volumes: ["./nginx.conf:/etc/nginx/nginx.conf"]',
                          '    depends_on: [web]', '    restart: unless-stopped', ''])
        vols = [f"  {s}_data:" for s in svcs if s in ("db", "postgres", "database")]
        if "redis" in svcs: vols.append("  redis_data:")
        if vols:
            L.append('volumes:')
            L.extend(vols)
        return "\n".join(L)

    def gen_fastapi_route(self, entity: str, fields: str = "", methods: str = "all") -> str:
        fl = [f.strip() for f in fields.split(",") if f.strip()] if fields else ["name"]
        el = entity.lower()
        ml = [m.strip().upper() for m in methods.split(",") if m.strip()] if methods != "all" else ["GET","POST","PUT","DELETE"]
        tm = {"str":"str","string":"str","int":"int","integer":"int","float":"float","bool":"bool","boolean":"bool"}
        L = [f'"""{entity} FastAPI routes - generated by EVEZ"""', '',
             'from fastapi import APIRouter, HTTPException', 'from pydantic import BaseModel',
             'from typing import Optional, List', 'from datetime import datetime', '',
             f'router = APIRouter(prefix="/api/{el}", tags=["{entity}"])', '',
             f'class {entity}Base(BaseModel):']
        for f in fl:
            if ":" in f:
                fn, ft = f.split(":", 1)
                L.append(f'    {fn.strip()}: {tm.get(ft.strip().lower(), "str")}')
            else:
                L.append(f'    {f}: str')
        L.extend(['', f'class {entity}Create({entity}Base): pass', '',
                  f'class {entity}Update(BaseModel):'])
        for f in fl: L.append(f'    {f.split(":")[0].strip()}: Optional[str] = None')
        L.extend(['', f'class {entity}Response({entity}Base):', '    id: str',
                  '    created_at: datetime', '', f'_{el}_store: dict = {{}}', ''])
        if "GET" in ml:
            L.extend([f'@router.get("/")',
                      f'async def list_{el}(skip: int = 0, limit: int = 100) -> List[{entity}Response]:',
                      f'    return list(_{el}_store.values())[skip:skip+limit]', '',
                      f'@router.get("/{{record_id}}")',
                      f'async def get_{el}(record_id: str) -> {entity}Response:',
                      f'    if record_id not in _{el}_store: raise HTTPException(404, "{entity} not found")',
                      f'    return _{el}_store[record_id]', ''])
        if "POST" in ml:
            L.extend([f'@router.post("/", status_code=201)',
                      f'async def create_{el}(data: {entity}Create) -> {entity}Response:',
                      '    import hashlib',
                      '    rid = hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:12]',
                      f'    record = {entity}Response('])
            for f in fl: L.append(f'        {f.split(":")[0].strip()}=data.{f.split(":")[0].strip()},')
            L.extend(['        id=rid, created_at=datetime.utcnow(),', '    )',
                      f'    _{el}_store[rid] = record', '    return record', ''])
        if "PUT" in ml:
            L.extend([f'@router.put("/{{record_id}}")',
                      f'async def update_{el}(record_id: str, data: {entity}Update) -> {entity}Response:',
                      f'    if record_id not in _{el}_store: raise HTTPException(404, "{entity} not found")',
                      f'    stored = _{el}_store[record_id]',
                      '    updated = stored.copy(update=data.dict(exclude_unset=True))',
                      f'    _{el}_store[record_id] = updated', '    return updated', ''])
        if "DELETE" in ml:
            L.extend([f'@router.delete("/{{record_id}}")',
                      f'async def delete_{el}(record_id: str) -> dict:',
                      f'    if record_id not in _{el}_store: raise HTTPException(404, "{entity} not found")',
                      f'    del _{el}_store[record_id]',
                      '    return {"status": "deleted", "id": record_id}', ''])
        return "\n".join(L)

    def gen_pytest_fixture(self, name: str, fixture_type: str = "data", scope: str = "function") -> str:
        name = name or "sample_data"
        L = ['import pytest', '']
        if fixture_type == "db":
            L.extend([f'@pytest.fixture(scope="{scope}")', f'def {name}():',
                      '    """Mock database."""',
                      '    class MockDB:',
                      '        def __init__(self): self.data = {}',
                      '        def insert(self, k, v): self.data[k] = v',
                      '        def select(self, k): return self.data.get(k)',
                      '        def delete(self, k): return self.data.pop(k, None) is not None',
                      '        def count(self): return len(self.data)',
                      '    return MockDB()'])
        elif fixture_type == "client":
            L.extend(['from fastapi.testclient import TestClient', 'from your_app import app', '',
                      f'@pytest.fixture(scope="{scope}")', f'def {name}():',
                      '    """FastAPI test client."""',
                      '    with TestClient(app) as c: yield c'])
        elif fixture_type == "mock":
            L.extend(['from unittest.mock import MagicMock', '',
                      f'@pytest.fixture(scope="{scope}")', f'def {name}():',
                      '    """Mock object."""',
                      '    m = MagicMock()',
                      '    m.process.return_value = {"status": "ok"}',
                      '    m.validate.return_value = True',
                      '    return m'])
        else:
            L.extend([f'@pytest.fixture(scope="{scope}")', f'def {name}():',
                      '    """Sample test data."""',
                      '    return {"id": "test-001", "name": "Test Entity", "value": 42, "active": True, "tags": ["unit", "test"]}'])
        return "\n".join(L)

    def gen_shell_script(self, name: str, commands: str = "", include_trap: bool = True) -> str:
        name = name or "deploy"
        cmds = [c.strip() for c in commands.split(",") if c.strip()] if commands else []
        L = ['#!/usr/bin/env bash', f'# {name}.sh - generated by EVEZ', '', 'set -euo pipefail', '']
        if include_trap:
            L.extend(["trap 'echo \"ERROR: Failed at line $LINENO\" >&2; exit 1' ERR", '',
                      'log() { echo "[$(date +%H:%M:%S)] $1"; }', ''])
        L.extend(['WORK_DIR="${WORK_DIR:-$(pwd)}"', 'cd "$WORK_DIR"', ''])
        if not cmds: cmds = ["echo Starting", "echo Done"]
        for cmd in cmds:
            if cmd in ("install", "deps"):
                L.extend(['log "Installing dependencies..."',
                          'pip install -r requirements.txt 2>/dev/null || npm install 2>/dev/null || true', ''])
            elif cmd in ("test", "tests"):
                L.extend(['log "Running tests..."',
                          'python -m pytest -v 2>/dev/null || npm test 2>/dev/null || true', ''])
            elif cmd in ("build", "compile"):
                L.extend(['log "Building..."',
                          'npm run build 2>/dev/null || python setup.py build 2>/dev/null || true', ''])
            elif cmd in ("deploy", "publish"):
                L.extend(['log "Deploying..."', 'git push origin main 2>/dev/null || true', ''])
            elif cmd in ("clean", "cleanup"):
                L.extend(['log "Cleaning..."',
                          'rm -rf __pycache__ .pytest_cache node_modules dist build 2>/dev/null || true', ''])
            else:
                L.extend([f'log "Running: {cmd}"', f'{cmd}', ''])
        L.append('log "Done."')
        return "\n".join(L)

    def gen_config(self, app_name="app", fmt="yaml", keys="") -> str:
        fmt = fmt.lower()
        kl = [k.strip() for k in keys.split(",") if k.strip()] if keys else ["debug:bool","host:str","port:int","database_url:str"]
        if fmt == "json":
            c = {"app": app_name, "environment": "development"}
            for k in kl:
                if ":" in k:
                    kn, kt = k.split(":", 1)
                    c[kn] = {"bool": False, "int": 0, "float": 0.0}.get(kt.lower(), "")
                else:
                    c[k] = ""
            c["features"] = {"cache": True, "metrics": False}
            return json.dumps(c, indent=2)
        elif fmt == "toml":
            L = [f'# {app_name} config - generated by EVEZ', '', '[app]', f'name = "{app_name}"', '']
            for k in kl:
                if ":" in k:
                    kn, kt = k.split(":", 1)
                    v = {"bool": "false", "int": "0", "float": "0.0"}.get(kt.lower(), '""')
                    L.append(f'{kn} = {v}')
            L.extend(['', '[features]', 'cache = true', 'metrics = false'])
            return "\n".join(L)
        else:
            L = [f'# {app_name} config - generated by EVEZ', '', 'app:',
                 f'  name: {app_name}', '  environment: development', '', 'settings:']
            for k in kl:
                if ":" in k:
                    kn, kt = k.split(":", 1)
                    v = {"bool": "false", "int": "0", "float": "0.0"}.get(kt.lower(), '""')
                    L.append(f'  {kn}: {v}')
            L.extend(['', 'features:', '  cache: true', '  metrics: false', '',
                      'database:', '  pool_size: 10', '  timeout: 30'])
            return "\n".join(L)

    def gen_gitignore(self, project_type="python") -> str:
        common = ['# Environment', '.env', '.env.local', '', '# IDE', '.vscode/', '.idea/',
                  '*.swp', '', '# OS', '.DS_Store', 'Thumbs.db', '']
        if project_type.lower() in ("python", "py"):
            specific = ['# Python', '__pycache__/', '*.py[cod]', '.pytest_cache/', '*.egg-info/',
                        'dist/', 'build/', 'venv/', '.venv/', '.mypy_cache/', '.coverage']
        elif project_type.lower() in ("node", "typescript", "ts"):
            specific = ['# Node', 'node_modules/', 'dist/', 'build/', '*.log',
                        'npm-debug.log*', '.npm', 'coverage/']
        elif project_type.lower() in ("react", "next"):
            specific = ['# React/Next', 'node_modules/', '.next/', 'out/', 'build/',
                        '*.log', 'coverage/', '.vercel']
        else:
            specific = []
        return "\n".join(common + specific)

    def gen_requirements(self, libs="", include_dev=False) -> str:
        ll = [l.strip() for l in libs.split(",") if l.strip()] if libs else ["fastapi","uvicorn","pydantic","httpx"]
        vm = {"fastapi":">=0.100.0","uvicorn":">=0.23.0","pydantic":">=2.0.0","httpx":">=0.24.0",
              "requests":">=2.31.0","sqlalchemy":">=2.0.0","redis":">=4.6.0","pytest":">=7.4.0",
              "python-dotenv":">=1.0.0","alembic":">=1.11.0"}
        L = ['# requirements.txt - generated by EVEZ', '']
        for lib in ll:
            L.append(f'{lib}{vm.get(lib.lower(), "")}')
        if include_dev:
            L.extend(['', '# Dev', 'pytest>=7.4.0', 'pytest-cov>=4.1.0', 'mypy>=1.5.0',
                      'ruff>=0.0.280', 'black>=23.7.0'])
        return "\n".join(L)

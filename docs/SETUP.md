# Setup

## Offline (always works)

```powershell
pip install -r requirements.txt
$env:HIOP_MEMORY_MODE="fixture"
$env:PYTHONPATH="src"
python demo\run_demo.py
python -m pytest tests -q
```

## Docker CockroachDB

```powershell
cd deploy\docker
docker compose up -d
$env:CRDB_DSN="postgresql://root@localhost:26257/defaultdb?sslmode=disable"
$env:HIOP_MEMORY_MODE="cockroach"
$env:PYTHONPATH="..\..\src"
python ..\..\demo\run_demo.py
```

## CockroachDB Cloud

1. https://cockroachlabs.cloud/signup  
2. Create free cluster; copy connection string  
3. `CRDB_DSN=...`  
4. Optional: enable Managed MCP; copy snippet into `mcp/mcp_config.example.json`  

## AWS

```powershell
# Install AWS SAM CLI; configure credentials
sam build -t deploy\aws\template.yaml
sam deploy --guided
```

Set parameter `CrdbDsn` to Cloud connection URI.  
Demo URL = API Gateway output `ApiUrl`.

## ccloud CLI (optional CRDB tool #3)

```text
ccloud auth login
ccloud cluster create ...
ccloud cluster sql ...
```

#!/bin/sh
set -e
alembic upgrade head

# SEED=demo (Green Valley, default) | sdsu | none. Only seeds an empty database.
python - <<'PY'
import asyncio, os, subprocess, sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

seed = os.environ.get("SEED", "demo").lower()
scripts = {"demo": "seed.py", "sdsu": "seed_sdsu.py"}
if seed not in scripts:
    print(f"[seed] SEED={seed}: skipping"); sys.exit(0)

async def count():
    e = create_async_engine(os.environ["DATABASE_URL"])
    async with e.connect() as c:
        n = (await c.execute(text("SELECT count(*) FROM universities"))).scalar()
    await e.dispose()
    return n

if asyncio.run(count()) > 0:
    print("[seed] database already has data: skipping"); sys.exit(0)
print(f"[seed] running {scripts[seed]}")
subprocess.run([sys.executable, scripts[seed]], check=True)
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

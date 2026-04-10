# Operational Rules

## Port Conflict Prevention

Before starting ANY dev server (npm run dev, uvicorn, flask run, vite):
1. Check if the port is free: `lsof -i:PORT`
2. If occupied, use next available in range
3. Suggested ranges: Next.js 3000-3999, Vite 5173-5179, FastAPI 8000-8099

## API Error Recovery

On any 401/403 authentication error:
1. Check if API key is loaded: `echo $RELEVANT_VAR | head -c 10`
2. Try reloading the key from your secrets manager
3. Check key expiry
4. Never retry more than twice without diagnosing the root cause

## Failure Diagnosis

When a command or operation fails:
1. Read the error message completely before acting
2. Check your assumptions (file exists? correct directory? right permissions?)
3. Try a focused fix based on the error
4. Don't retry the identical command hoping for a different result
5. Escalate to the user only after genuine investigation

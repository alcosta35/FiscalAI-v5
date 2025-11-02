# NGROK Authentication Fix

## Problem
Ngrok authentication fails even though the token is correctly stored in Colab Secrets.

## Root Cause
**Mismatch in variable names:**
- Cell 3 writes: `NGROK_AUTH_TOKEN` (with underscore)
- main.py looks for: `NGROK_AUTHTOKEN` (NO underscore)
- Result: ngrok can't find the token!

## The Fix

Line 262 in `main.py` was changed from:
```python
authtoken = os.getenv('NGROK_AUTHTOKEN')  # ❌ Wrong spelling
```

To:
```python
authtoken = settings.ngrok_auth_token  # ✅ Uses settings
```

## How to Apply

### Quick Fix (Recommended)
Replace your `/content/FiscalAI-v4/main.py` with the fixed version.

In Colab:
```python
# Upload the fixed main.py, then:
!cp /path/to/fixed/main.py /content/FiscalAI-v4/main.py
```

### Manual Fix
Edit line 262 in your `main.py`:

**Find this (around line 262):**
```python
authtoken = os.getenv('NGROK_AUTHTOKEN')
```

**Replace with:**
```python
authtoken = settings.ngrok_auth_token
```

## Verify the Fix

1. Make sure both files are updated:
   - ✅ `config.py` has `ngrok_auth_token: str = ""`
   - ✅ `main.py` uses `settings.ngrok_auth_token`

2. Make sure Cell 3 writes `NGROK_AUTH_TOKEN` to `.env`

3. Run Cell 4 again:
```bash
!mkdir -p data
!python main.py
```

You should see:
```
🌐 NGROK TUNNEL ATIVO
📡 URL Pública: https://xxxx-xxx-xxx-xxx.ngrok.io
```

## Summary of All Changes

| File | Change |
|------|--------|
| `config.py` | Added `ngrok_auth_token: str = ""` field |
| `main.py` | Changed line 262 to use `settings.ngrok_auth_token` |
| Cell 3 | Writes both `OPENAI_API_KEY` and `NGROK_AUTH_TOKEN` |

## Troubleshooting

If still not working:
1. Verify the token in Colab Secrets (🔑 icon)
2. Make sure "Notebook access" is enabled
3. Try printing the token in Cell 3 to confirm it's loaded
4. Check your ngrok account at https://dashboard.ngrok.com/

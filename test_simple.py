import os
import urllib.request
import json

print("1. Verificando variável de ambiente...")
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("   ERRO: Variável OPENROUTER_API_KEY não encontrada!")
    print("   Execute: set OPENROUTER_API_KEY=sua-chave-aqui")
    exit(1)
else:
    print(f"   OK: Chave encontrada (inicia com {api_key[:15]}...)")

print("\n2. Testando conexão com OpenRouter...")
payload = json.dumps({
    "model": "openai/gpt-3.5-turbo",  # modelo mais barato/teste
    "messages": [{"role": "user", "content": "Say 'OK'"}],
    "max_tokens": 10
}).encode()

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        print("   ✓ Conexão bem sucedida!")
        print(f"   Resposta: {data['choices'][0]['message']['content']}")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error {e.code}:")
    print(f"   {e.read().decode()}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
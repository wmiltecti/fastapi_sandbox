"""
Script de teste direto para API Continuus Blockchain
Testa diferentes formas de enviar o header dsKey
"""
import httpx
import json

# Configurações
API_URL = "http://continuus.miltecti.com.br/continuus_api/api/Block/Register"
DSKEY = "7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40"

# Payload de teste
payload = {
    "IdBlockchain": 1,
    "Data": {
        "teste": "valor"
    },
    "Fields": [
        {
            "NmField": "Teste",
            "DsValue": "Teste direto"
        }
    ]
}

print("="*60)
print("TESTE 1: Headers como dict normal")
print("="*60)
try:
    response = httpx.post(
        API_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "dsKey": DSKEY
        },
        timeout=30.0
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*60)
print("TESTE 2: Headers com httpx.Headers()")
print("="*60)
try:
    response = httpx.post(
        API_URL,
        json=payload,
        headers=httpx.Headers({
            "Content-Type": "application/json",
            "dsKey": DSKEY
        }),
        timeout=30.0
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*60)
print("TESTE 3: Headers com todas variações")
print("="*60)
headers_variations = [
    ("dskey", DSKEY),
    ("dsKey", DSKEY),
    ("DsKey", DSKEY),
    ("DSKEY", DSKEY),
    ("ds-key", DSKEY),
    ("DS-KEY", DSKEY),
]

for header_name, header_value in headers_variations:
    try:
        response = httpx.post(
            API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                header_name: header_value
            },
            timeout=30.0
        )
        print(f"{header_name}: Status {response.status_code} - {response.text[:100]}")
        if response.status_code == 200:
            print(f"✅ SUCESSO COM: {header_name}")
            break
    except Exception as e:
        print(f"{header_name}: Erro - {str(e)[:100]}")

print("\n" + "="*60)
print("TESTE 4: Usando requests (se disponível)")
print("="*60)
try:
    import requests
    response = requests.post(
        API_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "dsKey": DSKEY
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except ImportError:
    print("requests não instalado")
except Exception as e:
    print(f"Erro: {e}")

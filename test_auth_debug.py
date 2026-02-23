import httpx
import time
import random

base_url = "http://localhost:8000"
phone = f"+237{random.randint(600000000, 699999999)}"
identifiant = f"REAL_{int(time.time())}"
localite = "Douala"
referent = "REF_TEST_001"

person_data = {
    "phone_number": phone,
    "identifiant_interne": identifiant,
    "date_cle": "2024-02-19T00:00:00",
    "localite": localite,
    "numero_referent": referent,
    "nom": "Test",
    "prenom": "Debug",
    "email": "test.debug@example.com"
}

r = httpx.post(f"{base_url}/api/v1/persons/", json=person_data)
assert r.status_code in (201, 400), (r.status_code, r.text)

payload = {
    "From": f"whatsapp:{phone}",
    "To": "whatsapp:+14155238886",
    "Body": "Bonjour",
    "MessageSid": f"SM_START_{int(time.time()*1000)}"
}
r = httpx.post(f"{base_url}/api/v1/webhook/whatsapp", data=payload)
print("START:", r.status_code, r.json())
assert r.status_code == 200
assert r.json().get("status") == "authenticating"
assert r.json().get("question") == 1

payload["Body"] = identifiant
payload["MessageSid"] = f"SM_Q1_{int(time.time()*1000)}"
r = httpx.post(f"{base_url}/api/v1/webhook/whatsapp", data=payload)
print("Q1:", r.status_code, r.json())
assert r.status_code == 200
assert r.json().get("status") == "next_question"
assert r.json().get("question_number") == 2

payload["Body"] = localite
payload["MessageSid"] = f"SM_Q2_{int(time.time()*1000)}"
r = httpx.post(f"{base_url}/api/v1/webhook/whatsapp", data=payload)
print("Q2:", r.status_code, r.json())
assert r.status_code == 200
assert r.json().get("status") == "next_question"
assert r.json().get("question_number") == 3

payload["Body"] = referent
payload["MessageSid"] = f"SM_Q3_{int(time.time()*1000)}"
r = httpx.post(f"{base_url}/api/v1/webhook/whatsapp", data=payload)
print("Q3:", r.status_code, r.json())
assert r.status_code == 200
assert r.json().get("status") == "authenticated"
assert r.json().get("authenticated") is True

print("OK AUTH FLOW")

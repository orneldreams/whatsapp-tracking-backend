import time
import httpx

BASE_URL = "http://localhost:8000/api/v1"
PHONE = "+237659119612"
Q1 = "REAL_USER_001"
Q2 = "Cameroon"
Q3 = "REF_CM_001"


def send(body: str, sid_prefix: str):
    payload = {
        "From": f"whatsapp:{PHONE}",
        "To": "whatsapp:+14155238886",
        "Body": body,
        "MessageSid": f"{sid_prefix}_{int(time.time()*1000)}",
    }
    response = httpx.post(f"{BASE_URL}/webhook/whatsapp", data=payload, timeout=20)
    print(body, "=>", response.status_code, response.json())
    return response


if __name__ == "__main__":
    r1 = send("Bonjour", "SM_START")
    assert r1.status_code == 200 and r1.json().get("status") == "authenticating"

    r2 = send(Q1, "SM_Q1")
    assert r2.status_code == 200 and r2.json().get("status") == "next_question" and r2.json().get("question_number") == 2

    r3 = send(Q2, "SM_Q2")
    assert r3.status_code == 200 and r3.json().get("status") == "next_question" and r3.json().get("question_number") == 3

    r4 = send(Q3, "SM_Q3")
    assert r4.status_code == 200 and r4.json().get("status") == "authenticated" and r4.json().get("authenticated") is True

    print("REAL NUMBER FLOW OK")

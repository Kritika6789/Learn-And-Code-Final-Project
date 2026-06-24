import requests

def test_create_user():
    # 1. Login to get token
    login_data = {
        "username": "admin",
        "password": "Admin@1234"
    }
    res = requests.post("http://127.0.0.1:8000/api/auth/login", data=login_data)
    token = res.json().get("access_token")
    if not token:
        print("Failed to login", res.text)
        return

    # 2. Create user
    headers = {"Authorization": f"Bearer {token}"}
    user_payload = {
        "full_name": "test2",
        "email": "testing2@gmail.com",
        "username": "testing2",
        "password": "Testing@1234",
        "role": "MANAGER"
    }
    res = requests.post("http://127.0.0.1:8000/api/admin/users", json=user_payload, headers=headers)
    print("Status Code:", res.status_code)
    print("Response:", res.text)

if __name__ == "__main__":
    test_create_user()

import secrets
url = 'https://example.com/reset=' + secrets.token_urlsafe()
print(url)
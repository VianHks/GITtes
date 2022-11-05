from jwt import PyJWT

encoded = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
print(encoded)
print(jwt.decode(encoded, "secret", algorithms=["HS256"])) 

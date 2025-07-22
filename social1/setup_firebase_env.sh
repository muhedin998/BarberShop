#!/bin/bash

# Firebase Environment Variables Setup Script
# Generated from firebase-config.json for production deployment

echo "Setting up Firebase environment variables for push notifications..."

export FIREBASE_TYPE="service_account"
export FIREBASE_PROJECT_ID="push-notify-4ffd3"
export FIREBASE_PRIVATE_KEY_ID="3b3aea5a1abd3e1d5e59751563faf64fa138a821"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsvhBa3tScfO18
eUguFD+fVgn40A/nqVxHp+W3UAQu39PKZVPRbnWGH5cnna9xM3CMxWTIVK+pcgPw
NOw6Hx05/VjujhFPNwyJ6Z3y1AOAjWP5nNPR+R0y5/iSEb08IP94AVbrVm5dXzJI
vUnMe5aWXDMg7M9ieyOnao1Dw85/r1dEKGVG1DsuQSnYVfDkK4NWXwofh2sBuAcl
KK8ERySl3iRNIxKDgsh4Bm8sO6P1eJ16NJJYEK0KS3w8q6OMblc9cQRUtqXSH6VA
u2skvY8AGcBSrYmOo4lkj4g90Cdb8yvxSYjgoGdowb2u1ezA358Emk0erECIJyEC
IPHIW8NlAgMBAAECggEAAuXnaVbes0dnRpTUUK2XSamMXkfDVIwjV7Jp6LLndw/b
QkSD7PoQ77Cc/RWoqVoHE92F7NR64/ldNoz0v57hAyWMdegdQzp1s+Se+UF0U5ZL
rJbkeNvYkQ+SPIUeqyEUmCNRnX4kON3NfqnqUItsQdaHJxDCA/Fz7i2b9ByXXM4B
tk+HjPkymOlypywiQFWlFeE/Kp7Ji9yZULyo5chVxW5e2/CzFd6wX8B1J7VnmnaX
Go0gGVV5XW6JBHtCFx4ND5HDQ9vrZI2KIxTl0ATDMtviF11Amz3/niTCXjM5xUVM
yCIUTzAbw9sQ3tlyS23ICyRIHXQCSG9bLDMyyGCkKwKBgQDX4kKBU5etKq5MhDPB
Xwz0ZnwLOACF0fXHXfUrb89FrsISoRJRvvvGRNtag3f7lLkbe60pLYc/HV/3ok2c
QexOBapwUHro/Bme0qg/9Cq+iPM0gKUqnyM6fBu8KNep7A4Vme5eKZiLYFh5rpYz
99cyR7zsALow88YpAeH101iWfwKBgQDM14n0IaEBeUKjcQ3yaJ8Z0PV+wsAEWfvz
VKczYeOpAJ9vjEUibM1EdGaXWzeJNYMwPKRdEX2CNDCuZITHSnmczlfnk0QtatHT
hxiqOD1QYQMqya/mrbOQat4VM3MzKgdNMGOP72U8jO6+JEOlfTpft4zgMG1Kf9tp
9a6ht3IcGwKBgD47TwiQ3Exi3VPZWEIJ8GYTlPZ28k+hMsSB5UbcOFfSBMfx/qHp
+BIzjzgMZe3z9Vhi0ovoP/CFu0BbXRwKNOBY6cTurj+zTH9oInAtJpU+TT15SCN9
NF6LoEMhUun8ziKT+Q7T1tF2uIp7NXlNnI819tPhccriuuDfVg/TGNppAoGBAKOX
IypgTQgzQl/rIvtMSHvCoLyqZdVT095B5gIoFDvdLndUa8YRZGFeIKySAalHnkzA
sXdOR5Dbg2FTD6NlO/hZ5mQf/VvUKlynULBol7cAsxnR1vQAFx6n6lK+MytSTmB7
25eQ1aXk26nopkmc2CinGw/UPQQ5Vg6qUdv++FevAoGAcXzFfpBWVy8zLhzn7NrT
bAQEeuJyeBZiHJVbQ+a14GnX+r1GL3Ds3xVDE7abA9YkrvPrNenCfEu2S8k3hof1
Na+AjC1mZcWDi6B1z/sDTuk/tQMaL5LmxsNoh+gqoRVxWGgrzSP4YPqTVrRDk/qG
0ttIzOmiLemSMbCPHShU3+U=
-----END PRIVATE KEY-----"
export FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@push-notify-4ffd3.iam.gserviceaccount.com"
export FIREBASE_CLIENT_ID="112792915322073097699"
export FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
export FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"
export FIREBASE_AUTH_PROVIDER_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
export FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40push-notify-4ffd3.iam.gserviceaccount.com"
export FIREBASE_UNIVERSE_DOMAIN="googleapis.com"

echo "✅ Firebase environment variables set successfully!"
echo ""
echo "To make these permanent, add them to your ~/.bashrc or ~/.profile:"
echo "echo 'export FIREBASE_TYPE=\"service_account\"' >> ~/.bashrc"
echo "echo 'export FIREBASE_PROJECT_ID=\"push-notify-4ffd3\"' >> ~/.bashrc"
echo "echo 'export FIREBASE_PRIVATE_KEY_ID=\"3b3aea5a1abd3e1d5e59751563faf64fa138a821\"' >> ~/.bashrc"
echo 'echo "export FIREBASE_PRIVATE_KEY=\"-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsvhBa3tScfO18
eUguFD+fVgn40A/nqVxHp+W3UAQu39PKZVPRbnWGH5cnna9xM3CMxWTIVK+pcgPw
NOw6Hx05/VjujhFPNwyJ6Z3y1AOAjWP5nNPR+R0y5/iSEb08IP94AVbrVm5dXzJI
vUnMe5aWXDMg7M9ieyOnao1Dw85/r1dEKGVG1DsuQSnYVfDkK4NWXwofh2sBuAcl
KK8ERySl3iRNIxKDgsh4Bm8sO6P1eJ16NJJYEK0KS3w8q6OMblc9cQRUtqXSH6VA
u2skvY8AGcBSrYmOo4lkj4g90Cdb8yvxSYjgoGdowb2u1ezA358Emk0erECIJyEC
IPHIW8NlAgMBAAECggEAAuXnaVbes0dnRpTUUK2XSamMXkfDVIwjV7Jp6LLndw/b
QkSD7PoQ77Cc/RWoqVoHE92F7NR64/ldNoz0v57hAyWMdegdQzp1s+Se+UF0U5ZL
rJbkeNvYkQ+SPIUeqyEUmCNRnX4kON3NfqnqUItsQdaHJxDCA/Fz7i2b9ByXXM4B
tk+HjPkymOlypywiQFWlFeE/Kp7Ji9yZULyo5chVxW5e2/CzFd6wX8B1J7VnmnaX
Go0gGVV5XW6JBHtCFx4ND5HDQ9vrZI2KIxTl0ATDMtviF11Amz3/niTCXjM5xUVM
yCIUTzAbw9sQ3tlyS23ICyRIHXQCSG9bLDMyyGCkKwKBgQDX4kKBU5etKq5MhDPB
Xwz0ZnwLOACF0fXHXfUrb89FrsISoRJRvvvGRNtag3f7lLkbe60pLYc/HV/3ok2c
QexOBapwUHro/Bme0qg/9Cq+iPM0gKUqnyM6fBu8KNep7A4Vme5eKZiLYFh5rpYz
99cyR7zsALow88YpAeH101iWfwKBgQDM14n0IaEBeUKjcQ3yaJ8Z0PV+wsAEWfvz
VKczYeOpAJ9vjEUibM1EdGaXWzeJNYMwPKRdEX2CNDCuZITHSnmczlfnk0QtatHT
hxiqOD1QYQMqya/mrbOQat4VM3MzKgdNMGOP72U8jO6+JEOlfTpft4zgMG1Kf9tp
9a6ht3IcGwKBgD47TwiQ3Exi3VPZWEIJ8GYTlPZ28k+hMsSB5UbcOFfSBMfx/qHp
+BIzjzgMZe3z9Vhi0ovoP/CFu0BbXRwKNOBY6cTurj+zTH9oInAtJpU+TT15SCN9
NF6LoEMhUun8ziKT+Q7T1tF2uIp7NXlNnI819tPhccriuuDfVg/TGNppAoGBAKOX
IypgTQgzQl/rIvtMSHvCoLyqZdVT095B5gIoFDvdLndUa8YRZGFeIKySAalHnkzA
sXdOR5Dbg2FTD6NlO/hZ5mQf/VvUKlynULBol7cAsxnR1vQAFx6n6lK+MytSTmB7
25eQ1aXk26nopkmc2CinGw/UPQQ5Vg6qUdv++FevAoGAcXzFfpBWVy8zLhzn7NrT
bAQEeuJyeBZiHJVbQ+a14GnX+r1GL3Ds3xVDE7abA9YkrvPrNenCfEu2S8k3hof1
Na+AjC1mZcWDi6B1z/sDTuk/tQMaL5LmxsNoh+gqoRVxWGgrzSP4YPqTVrRDk/qG
0ttIzOmiLemSMbCPHShU3+U=
-----END PRIVATE KEY-----\"' >> ~/.bashrc
echo 'export FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@push-notify-4ffd3.iam.gserviceaccount.com"' >> ~/.bashrc
echo 'export FIREBASE_CLIENT_ID="112792915322073097699"' >> ~/.bashrc
echo 'export FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"' >> ~/.bashrc
echo 'export FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"' >> ~/.bashrc
echo 'export FIREBASE_AUTH_PROVIDER_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"' >> ~/.bashrc
echo 'export FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40push-notify-4ffd3.iam.gserviceaccount.com"' >> ~/.bashrc
echo 'export FIREBASE_UNIVERSE_DOMAIN="googleapis.com"' >> ~/.bashrc
echo ""
echo "Then run: source ~/.bashrc"
echo ""
echo "🔥 Your push notifications should now work in production!"
# OpenID-provider
### My custom OpenID-provider that implement rbac control and can leave it on resource server optional (this setting allow on step with creating client)
## FLOW:
### 1) Setup .env-prod for production run in docker or .env if you run it locally
#### 1.1) OPTIONALLY you can customize your logging (logging_non_tracing if you set TRACING=false) and gunicorn configs in directory auth_service/config
### 2) Run Application:
#### 2.1) Run if you need migrate app (db and minio):
```bash
  make up-setup
```
#### else just run with:
```bash
  make up
```
### 3) create all clients you need with api (OPENAPI Shcema in http(s)://host/api)
### 4) register your resource servers and set them type RBAC_BY_AS (RBAC control by our server) or RS_CONTROLLED (resource server)
### 5) register your roles with your RS
### 5) build url in your client like http://127.0.0.1/pages/auth-to-client.html?client_id=1&required_resources=%7B%22user_data_needed%22%3A%5B%22email%22%5D%2C%22rs_ids%22%3A%5B1%5D%7D&redirect_url=http%3A%2F%2F127.0.0.1%3A8000%2Fdocs&code_verifier=T1GOVCgNXEgpqg0m-8v9-ORgDjvhGkybBDIDDYWmUS8&code_challenge_method=S256 
### where you set your client id, required_resources like user_data_needed (email or one one-off url to avatar) and resource_server_ids that your client needs to apply on behalf of the user (only that works with our RBAC), redirect_url what user will be redirected (your client callback), code_verifier and code challenge method ("S256" or "plain") (read RSA RFC 6749)
### 6) update user roles if your client verified (now even without verifying but will be removed later)
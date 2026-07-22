# SSH, curl, telnet — Junior C

## 1. SSH — Secure Shell

```bash
# Oddiy ulanish
ssh username@192.168.1.100

# Port ko'rsatish
ssh -p 2222 username@192.168.1.100

# Kalit bilan ulanish
ssh -i ~/.ssh/id_rsa username@192.168.1.100
```

### SSH kalit yaratish

```bash
ssh-keygen -t rsa -b 4096 -C "email@example.com"
# → ~/.ssh/id_rsa      (private key — hech kimga bermang!)
# → ~/.ssh/id_rsa.pub  (public key — serverga qo'shiladi)

ssh-copy-id username@192.168.1.100
```

### SCP — fayl nusxalash

```bash
# Local → Server
scp file.txt username@192.168.1.100:/var/www/

# Server → Local
scp username@192.168.1.100:/var/log/app.log ./

# Papka nusxalash
scp -r ./dist username@192.168.1.100:/var/www/
```

## 2. curl — HTTP so'rovlar

```bash
# GET
curl https://api.example.com/employees

# Header bilan
curl -X GET https://api.example.com/employees \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json"

# POST
curl -X POST https://api.example.com/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Orzibek", "age": 25}'

# PUT
curl -X PUT https://api.example.com/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Orzibek Updated"}'

# DELETE
curl -X DELETE https://api.example.com/employees/1

# Response header ko'rish
curl -I https://api.example.com/employees

# SSL tekshirmaslik (test uchun)
curl -k https://localhost:5001/api/employees

# Verbose
curl -v https://api.example.com/employees
```

## 3. telnet — port tekshirish

```bash
telnet 192.168.1.100 5432  # PostgreSQL port ochiqmi?
telnet 192.168.1.100 80    # HTTP port ochiqmi?

# Natija:
# Connected → port ochiq ✅
# Connection refused → port yopiq ❌
```

## 4. traceroute — yo'l kuzatish

```bash
# Windows
tracert google.com

# Linux
traceroute google.com
```

## 5. Amalda — deployment

```bash
ssh ubuntu@192.168.1.100
cd /var/www/hr-api
scp -r ./publish/* ubuntu@192.168.1.100:/var/www/hr-api/
sudo systemctl restart hr-api
curl -I http://localhost:5000/api/health
```

## 6. Qo'shimcha nuqtalar

- **`~/.ssh/config`** — SSH sozlamalari:
  ```
  Host prod
      HostName 192.168.1.100
      User ubuntu
      IdentityFile ~/.ssh/id_rsa
  ```
  Keyin: `ssh prod`
- **Port forwarding**:
  ```bash
  ssh -L 5432:localhost:5432 ubuntu@192.168.1.100
  ```

## 7. Imtihon savollari

1. SSH kalit juftligi nima? Private va public kalit qaysi maqsadda?
2. `scp` va `ssh` orasidagi farq nima?
3. `curl -v` nima ko'rsatadi?
4. `telnet` qachon ishlatiladi?
5. SSH config fayli nima uchun kerak?

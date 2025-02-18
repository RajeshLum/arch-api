# ArchAngel-datalake
The Data Lake of St Micheal Arch Angel AML System

# How to run this application ? 

### **1. Clone the Repository**
First, log in to your server and navigate to the desired deployment directory:

```bash
cd /var/www/
git clone https://github.com/smartkuttan/ArchAngel-datalake.git
cd ArchAngel-datalake
```

---

### **2. Set Up Environment Variables**
Ensure the `.env` file is properly configured. If missing, create it:

```bash
nano .env
```

Copy and paste the following(example):

```ini
POSTGRES_DB=archangel
POSTGRES_USER=archangel
POSTGRES_PASSWORD=4CT4hBk7e4:(Ue
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=django-insecure-@=n%g2nd3%8so=j$*j7kxttvf_x(%ws3+*smtn)au%==m4)&s&
DEBUG=True
```

Save and exit (`CTRL + X`, then `Y` and `Enter`).

---

### **3. Install Docker and Docker Compose**
If Docker and Docker Compose are not installed, install them:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose -y
```

Ensure Docker is running:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

### **4. Build and Start the Application**
Now, use `docker-compose` to set up the application:

```bash
docker-compose up --build -d
```

- `--build`: Builds the image if it's not already built.
- `-d`: Runs in detached mode (in the background).

Check running containers:

```bash
docker ps
```

You should see `archangel_web` and `archangel_postgres` running.

---

### **5. Run Database Migrations**
Execute the following command to apply database migrations:

```bash
docker-compose exec web python manage.py migrate
```

---

### **6. Create a Superuser**
Create an admin user to access the Django admin panel:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to enter a username, email, and password.

---

### **7. Access the Application**
Once the containers are running, the application should be accessible at:

```
http://<SERVER_IP>:8000
```

If accessing locally:

```
http://localhost:8000
```

---

### **8. Check Logs (If Needed)**
If the app is not running as expected, check the logs:

```bash
docker-compose logs web
docker-compose logs db
```

---

### **9. Setting Up a Reverse Proxy (Optional)**
To run the application on **port 80** instead of **8000**, set up **Nginx**:

```bash
sudo apt install nginx -y
```

Edit the Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/archangel
```

Add the following:

```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Save and exit (`CTRL + X`, then `Y` and `Enter`).

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/archangel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now, the app should be accessible at:

```
http://yourdomain.com
```

---

### **10. Managing the Application**
- **Stop the application**  
  ```bash
  docker-compose down
  ```
  
- **Restart the application**  
  ```bash
  docker-compose up -d
  ```

- **Check container status**  
  ```bash
  docker ps
  ```

---

### **11. Automate with Systemd (Optional)**
To ensure the application starts automatically, create a `systemd` service:

```bash
sudo nano /etc/systemd/system/archangel.service
```

Add the following:

```
[Unit]
Description=ArchAngel Django Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/ArchAngel-datalake
ExecStart=/usr/bin/docker-compose up --build -d
ExecStop=/usr/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target
```

Save and exit.

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable archangel
sudo systemctl start archangel
```

---

### **12. Security Hardening**
- Set `DEBUG=False` in `.env` for production.
- Use a strong `DJANGO_SECRET_KEY`.
- Configure **PostgreSQL** to only accept local connections or use a secure password.
- Use **SSL certificates** (e.g., Let’s Encrypt with Certbot for HTTPS).

---
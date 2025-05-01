# Rising Stars App

## Deployment
```
sudo nano /etc/systemd/system/rising-stars.service
```
Pegar es contenido en *rising-stars.service*

En *AMI* o *user data* poner
```
systemctl daemon-reload
systemctl enable rising-stars.service
systemctl start rising-stars.service
```

```
cd /rising_stars/app
sudo chmod +x ./deploy_app.sh
sudo ./deploy_app.sh
```

# curw-rest-api
RESTful API with using python Flask framework to store,query and modify CURW (Centre for URban Water) Time series


Before running the uwsgi ini file you will need to add a line to it to create logs.
Something like:

```bash
#location of log files
logto = /var/log/uwsgi/%n.log
```

Then you will have to create the directory in your VPS
(note that you can create the directory in whatever path you want, as long as it's the path that you have in the ini file)

```bash
sudo mkdir -p /var/log/uwsgi
sudo chown -R user:user /var/log/uwsgi
```
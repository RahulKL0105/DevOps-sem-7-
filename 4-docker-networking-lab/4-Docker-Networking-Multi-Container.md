# Exercise 4: Docker Networking with Multiple Containers

## Objective
Understand Docker networking concepts and configure a multi-container application where services communicate over a custom bridge network.

## Scenario
A web application composed of three containers:
- A Python Flask web server
- A MySQL database
- A Redis cache

## Step 1: Create a bridge network

```bash
docker network create --driver bridge my-bridge-net
```

![Network created](Images/docker-network-create.png)

## Step 2: Verify the network

```bash
docker network ls
```

![Network list](Images/docker-network-ls.png)

## Step 3: Inspect the network

```bash
docker network inspect my-bridge-net
```

![Network inspect](Images/docker-network-inspect.png)

The network uses the `bridge` driver with subnet `172.18.0.0/16` and gateway `172.18.0.1`. The `Containers` section is empty because no container has joined yet.

## Step 4: Flask app

`app.py`
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "This is a simple REST API built with Flask."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

> **Note:** `host='0.0.0.0'` is required so the published port (`-p 5001:5001`) can reach the app. Flask's debug mode is left off inside the container.

`requirements.txt`
```
Flask==2.0.1
Werkzeug==2.0.3
```


> **Note:** The original exercise pinned only `Flask==2.0.1`, but that version depends on an internal Werkzeug function (`url_quote`) that was removed in newer Werkzeug releases. Pinning `Werkzeug==2.0.3` alongside Flask resolved an `ImportError` on container startup.

`Dockerfile`
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
CMD ["python", "app.py"]
```

![Project files created](Images/docker-create-files.png)

## Step 5: Build the Flask image

```bash
docker build -t flask-api .
```

![Flask image build](Images/docker-flask-build.png)

## Step 6: Launch all three containers on the bridge network

```bash
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=devopsdb mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api
```

> **Note:** The official MySQL image requires a root password to be set via `MYSQL_ROOT_PASSWORD`, or it refuses to start.

```bash
docker ps
```

![All three containers running](Images/docker-containers-running.png)

## Step 7: Test connectivity between containers

From the host, resolve the other containers by name from inside the flask container, then check that Redis responds:

```bash
docker exec flask getent hosts mysql
docker exec flask getent hosts redis
docker exec -it redis redis-cli ping
```

![Name resolution and Redis ping](Images/docker-name-resolution.png)

`flask` resolves `mysql` to `172.18.0.2` and `redis` to `172.18.0.3` using only their container names, and Redis answers `PONG`.

> **Note:** `getent hosts` is used because the `python:3.9-slim` base image doesn't include `ping`. To use `ping` instead, run `docker exec -it flask bash` and install it first: `apt-get update && apt-get install -y iputils-ping`, then `ping -c 3 mysql`.

Check that MySQL is up and the `devopsdb` database was created:

```bash
docker exec -it mysql mysql -uroot -prootpass -e "SHOW DATABASES;"
```

![MySQL databases](Images/docker-mysql-databases.png)

> **Note:** MySQL prints a warning about using a password on the command line. That is expected here and fine for a local lab.

Inspect the network again. It now lists all three containers with their IP addresses:

```bash
docker network inspect my-bridge-net
```

![Network inspect with containers attached](Images/docker-network-inspect-connected.png)

## Step 8: Test the Flask API from the host machine

```bash
curl http://localhost:5001/about
```

![Flask API response](Images/docker-flask-curl.png)

```json
{
  "description": "This is a simple REST API built with Flask.",
  "name": "Simple REST API",
  "version": "1.0"
}
```

## Step 9: Clean up

```bash
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net
docker rmi flask-api        # optional: remove the image
```

![Cleanup](Images/docker-cleanup.png)

## Q&A

**Q1: What is the purpose of the `--net` flag in `docker run`?**
A: It specifies which Docker network the container should connect to.

**Q2: How do containers communicate with each other on the same network?**
A: Containers on the same user-defined bridge network can resolve each other by container name via Docker's built-in DNS, and communicate over their internal IPs.

**Q3: What is the difference between a bridge network and a host network?**
A: A bridge network isolates containers on a private virtual network, requiring explicit port mapping to reach them from outside. A host network shares the host machine's network stack directly, with no isolation.

**Q4: How can you expose a container's port to the host machine?**
A: Use the `-p` flag, e.g. `-p 5001:5001`, to map a container port to a host port.

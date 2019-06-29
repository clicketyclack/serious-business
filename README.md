# serious-business
Super Basic Streaming Network Server (sbsns)

# Manual dependency: videojs
This project uses videojs, https://github.com/videojs/video.js

```bash
work$ tar -xzf video.js-7.6.0
work$ cd video.js-7.6.0
work/video.js-7.6.0$ npm ci
work/video.js-7.6.0$ npm run build
work/video.js-7.6.0$ cp -r dist/* ../cc-serious-business/static/v/
```

# Setting up an environment.

```bash
> virtualenv -p python3 env_sbsns
> source env_sbsns/bin/activate
> pip install -r requirements.txt
> chmod +x srv/srv_main.py
> ./srv/srv_main.py
```


# Running with docker.
```bash
> docker build -t sbsns .
> docker run -v ~/my_library/:/sbsns/media -p 8080:8080/tcp  sbsns:latest
```

# Restarting.
```bash
docker kill --name sbsns
docker rm sbsns
```

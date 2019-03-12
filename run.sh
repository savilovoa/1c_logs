!#bin/sh

docker run --name 1c_logs --restart=always \
  -v /var/lib/1c_logs/since:/var/lib/1c_logs/since \
  -v /data/1c_logs/erp/1Cv8Log:/var/lib/1c_logs/data \
  -v /var/log/1c_logs:/var/log/1c_logs \
  savilovoa/1c_logs

Index ALDI Products inside of a sqlite database

- fetches all aldi products and puts price information inside of separate table for data analysis

```
docker build -t aldi ./

docker image tag aldi:latest tower.local:5000/aldi:latest
docker push tower.local:5000/aldi:latest 

```
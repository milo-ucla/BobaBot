sudo docker run \
    -e PYTHONUNBUFFERED=1 \
    -e MONGO_URL=$MONGO_URL \
    -e TOKEN=$TOKEN \
    --restart unless-stopped \
    bobabot:latest

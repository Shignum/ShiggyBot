tmux new-ses -s Lavalink -d 'java -jar Lavalink.jar'
sleep 20
tmux new-ses -s bot -d 'python3 ./src/bot.py'
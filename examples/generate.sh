#!/bin/sh

# Remember to source ../venv/bin/activate

# List of uuids to plot in order
# Only the first column is included
uuids="$(echo '''
896f7799f2a24185a9c09a756ace1f0c ryn
ac04f297f74c44dea24e0083936ac59a usbb
3d58a2de38314a17a30567258295f81e ciara
2cb4afab2c9344c0a71315a45a552872 dirt
a937646bf11544c38dbf9ae4a65669a0 sky
6bc1dd0ff3514c3db6cc262e55b6e7aa alg
''' | awk '{printf "%s ", $1}')"

for stat in fkdr finals kills beds stars wlr; do
	echo "Plotting session and overall $stat"
	python plot_multiple_players.py "bw$stat" $uuids
	python plot_multiple_players.py "-bw$stat" $uuids
done

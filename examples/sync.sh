#!/bin/sh

mkdir -p downloaded_data

rsync -avz miniplenty-remote:/backup/statwatch/downloaded_data/ downloaded_data

# Plex Audio Playlist Importer
A Python script to read an audio m3u file and create a Plex playlist from the entries.
This script only deals with m3u files that specify local filesystem tracks line by line.  It also assumes that your Plex
library where audio tracks live is titled **Music**.  This may be improved in the future.

## How to Use
This script works with Python 3.  First, create a virtualenv.

```commandline
python3 -m venv venv
source venv/bin/activate
```

Install the requirements.
```commandline
pip install requirements.txt
```

Run the script.  
See help
```commandline
$ python3 main.py -h
usage: main.py [-h] --token TOKEN [--plex_url PLEX_URL] m3u

Import m3u audio playlist into Plex.

positional arguments:
  m3u                  The audio playlist in m3u format.

optional arguments:
  -h, --help           show this help message and exit
  --token TOKEN        Plex API token
  --plex_url PLEX_URL  Plex API URL. (Optional)
```

## Troubleshooting Tips

### Getting the Plex API Token
To retrieve the Plex API Token, simply click the teardrop menu (3 vertical dots) on any track item and choose **Get Info**.
On the popup dialog, click **View XML**.  This will open an API response in a new window or tab.
Select the URL in the URL bar.  The last parameter should be **X-Plex-Token**.  Copy the value to use as the token
for this script.

### Plex URL
This script assumes the Plex server is running on localhost.  If this is not the case, then specify the
correct location with the **plex_url** option.

### Tracks not found
This utility does a decent job of finding tracks by normalizing the track titles from the metadata.
However, there could be cases where Plex has a different title and it cannot find a match.  Just look for the missed tracks 
on the output.  You should see something like the following:

```commandline
ERROR: Could not find match for /home/will/Music/hq/Herbie Hancock/Gershwin's World/14 - Embraceable You.mp3
```
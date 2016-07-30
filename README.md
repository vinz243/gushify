# gushify
Python CLI tool to manage big torrent dump folder


### Description

Gushify is a small CLI tool which aims at helping managing downloaded torrents,
in three different ways/steps from a glob of .torrent files

1. Torrent file search and binding. This step will look in the torrent glob,
and it will match the torrents with the storage directory using file name,
size and optionally md5 (if available)
2. Sorting and restructuring downloaded data. This will move downloaded files,
according to the torrent matched in step 1, and put them under the right directory.
This will also generate a `metadata.json` file for each torrent with several infos.
3. Torrent client data generation. Once it has finally moved all data, it can
generate config for clients, using btresume data.

### Installation

```sh
git clone https://github.com/vinz243/gushify.git
cd gushify
pip install -r requirements.txt
./gushify.py
```

### Usage

```
gushify.

Usage:
  ./gushify.py <source> <storage> [options]
options:
  -h --help           Display this help message
  --glob -g           Use a glob as a source (*.torrent...)
  --rename -r         Rename files to match content
  --subf -s           Create a subfolder for every torrent following naming conventions
  --no-tv-subf -S     Don't create TV subfolder (<serie name>/<season>/<episode>)
  --no-sort -N        Don't perform step 2, so no sorting and moving files
  --backup -b         Create an index which contains every old/new location pair
  --cat-thr=<pct>     Minimum treshold file cat. match to consider torrent as said cat. (default: 70)
  --dry-run -n        Do not do anything, only print what it would do
  --force -f          Force create assumed existing dirs, force overwrite
  --verbose -v        Verbose mode
  --interactive -i    Interactive mode
  --out=<outdir>      Output torrent client config directory
  --qbt -Q            Output as qBitTorrent data
  --libt -L           Output as libTorrent data
  --ut -U             Output as µTorrent data
  --txt -T            Output as text data
```

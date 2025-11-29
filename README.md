# MusicParty
## Very barebones and basic music indexer for Copyparty

```
   MusicParty a very barebones music indexer for Copyparty

Options:
  --user TEXT
  --password TEXT
  --m3u BOOLEAN
  --help           Show this message and exit. 
```

### Examples of use:

> Writes the playlist output to a file.

`musicparty http://url/to/my/music/folder  | tee playlist.m3u`

> Redirects the playlist output to mpv or any m3u and stdin reading compatible players. It also uses credentials for basic auth

`musicparty http://url/to/my/music/folder/secret --password hunter2 | mpv -`


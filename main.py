from httpx import get, codes
from json import loads
from typing import Optional
import click
from sys import stderr


class SongDiscovery:
    def __init__(self, user: Optional[str] = None, password: Optional[str] = None):
        self.user = user
        self.password = password
        self.acceptedFormats = ["aac", "flac", "m4a", "mp3", "ogg", "opus", "wav"]
        self.parameters = ""

    def getAllSongs(self, urls: list):
        allSongs = []
        for i in urls:
            jsonResponse = self.getFolderRaw(url=i)
            songs = self.getPathSong(jsonResponse=jsonResponse, baseUrl=i)
            allSongs.extend(songs)
        return allSongs

    def getFolderRaw(self, url):
        if self.user or self.password:
            if not self.user:
                headers = {"PW": self.password}
                self.parameters = f"?pw={self.password}"
            else:
                headers = {"PW": f"{self.user}:{self.password}"}
                self.parameters = f"?pw={self.user}:{self.password}"

            response = get(url + "?ls", headers=headers)
        else:
            response = get(url + "?ls")

        if response.status_code == codes.UNAUTHORIZED:
            print("Please use your credentials to acces this directory!", file=stderr)
            exit(code=2)
        response.raise_for_status()
        response = response.text
        jsonResponse = loads(response)
        return jsonResponse

    def getPathSong(self, jsonResponse, baseUrl):
        songs = ["" for e in jsonResponse["files"] if e["ext"] in self.acceptedFormats]

        if not str(baseUrl).endswith("/"):
            baseUrl = baseUrl + "/"

        for i in jsonResponse["files"]:
            if i["ext"] in self.acceptedFormats:
                songs[i["tags"][".tn"] - 1] = (
                    i["tags"]["title"],
                    i["tags"]["album"],
                    f"{baseUrl}{i['href']}{self.parameters}",
                )

        return songs


class Converter:
    def __init__(
        self,
        songs,
    ) -> None:
        self.songs = songs

    def plainText(self):
        out = []
        for _, _, url in self.songs:
            out.append(url)
        print("\n".join(out), flush=True)

    def M3U(self):
        out = ["#EXTM3U"]
        for title, album, url in self.songs:
            out.append(f"#EXTINF:-1,{title} | {album}")
            out.append(url)
        print("\n".join(out), flush=True)


@click.group(invoke_without_command=True)
@click.pass_context
def shutup(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


@click.command(help="MusicParty a very barebones music indexer for Copyparty")
@click.argument("urls", nargs=-1)
@click.option("--user")
@click.option("--password")
@click.option(
    "--m3u",
    default=True,
)
@click.pass_context
def cli(
    ctx,
    urls,
    user,
    password,
    m3u,
):
    if len(urls) == 0 and not user and not password and m3u is True:
        click.echo(ctx.get_help())
        ctx.exit()

    if user or password:
        print(
            "Writting this as a playlist file can be insecure when using credentials!",
            file=stderr,
        )
    discovery = SongDiscovery(user=user, password=password)
    output = discovery.getAllSongs(urls=urls)
    convert = Converter(songs=output)
    if m3u:
        convert.M3U()
    if m3u is False:
        convert.plainText()


if __name__ == "__main__":
    cli()

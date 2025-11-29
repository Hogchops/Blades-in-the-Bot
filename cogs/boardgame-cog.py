import re
import time   # ✅ IMPORTANT: you were using time.sleep but didn't import time
import requests
import xml.etree.ElementTree as ET

from discord.ext import commands
import discord
from discord import app_commands

BGG_THING_URL = "https://www.boardgamegeek.com/xmlapi2/thing"


def extract_bgg_id_from_url(url: str) -> int | None:
    """
    Extract the game ID from a BGG URL.

    Examples:
      https://boardgamegeek.com/boardgame/174430/gloomhaven
      https://boardgamegeek.com/boardgame/174430/
      https://boardgamegeek.com/boardgame/174430
    """
    pattern = r"boardgame/(\d+)"
    match = re.search(pattern, url)
    if match:
        return int(match.group(1))
    return None


def parse_best_player_counts(item: ET.Element) -> list[tuple[str, int]]:
    """
    Parse the 'suggested_numplayers' poll and return a list of (num_players, best_votes),
    sorted by best_votes descending.
    """
    poll = item.find("poll[@name='suggested_numplayers']")
    if poll is None:
        return []

    results = []
    for res in poll.findall("results"):
        num_players = res.get("numplayers")  # e.g., "1", "2", "3", "4+", etc.
        if not num_players:
            continue

        best_votes = 0
        for r in res.findall("result"):
            if r.get("value") == "Best":
                try:
                    best_votes = int(r.get("numvotes", "0"))
                except ValueError:
                    best_votes = 0
                break

        if best_votes > 0:
            results.append((num_players, best_votes))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


def fetch_bgg_game_data(game_id: int) -> dict | None:
    """
    Fetch game data from BGG XML API2 and return a simplified dict.
    Handles 202 responses by retrying a few times, logs status for debugging.
    """
    params = {
        "id": game_id,
        "stats": 1,
    }
    headers = {
        # Try a very generic UA first; some filters dislike email addresses
        "User-Agent": "Mozilla/5.0 (compatible; DiscordBoardGameBot/1.0)",
        "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
    }

    max_attempts = 5
    last_resp_text = None
    last_status = None

    for attempt in range(max_attempts):
        try:
            resp = requests.get(
                BGG_THING_URL,
                params=params,
                headers=headers,
                timeout=20,
            )
        except Exception as e:
            print(f"[BGG] Request error for id={game_id}: {e}")
            return None

        last_status = resp.status_code
        last_resp_text = resp.text

        print(f"[BGG] Attempt {attempt+1}/{max_attempts}, status={resp.status_code}")

        # Explicit debug for 401
        if resp.status_code == 401:
            print("[BGG] Got 401 Unauthorized. Response headers:")
            print(dict(resp.headers))
            print("Body (first 500 chars):")
            print(last_resp_text[:500])
            # Don't keep retrying on 401; it's a config/auth problem
            return None

        # 202 = “request accepted, try again later”
        if resp.status_code == 202:
            time.sleep(2)
            continue

        # For other non-200s, retry a couple times then give up
        if resp.status_code != 200:
            time.sleep(2)
            continue

        # 200 OK
        break
    else:
        print(f"[BGG] Failed after {max_attempts} attempts, last status={last_status}")
        print(f"[BGG] Last response (first 500 chars): {last_resp_text[:500]}")
        return None

    try:
        root = ET.fromstring(last_resp_text)
    except ET.ParseError as e:
        print(f"[BGG] XML parse error for id={game_id}: {e}")
        print(f"[BGG] Broken response (first 500 chars): {last_resp_text[:500]}")
        return None

    item = root.find("item")
    if item is None:
        print(f"[BGG] No <item> element found for id={game_id}. Raw XML snippet:")
        print(last_resp_text[:500])
        return None

    def find_child_text(tag, **attrib_filter):
        for child in item.findall(tag):
            if all(child.get(k) == str(v) for k, v in attrib_filter.items()):
                return child.get("value") or child.text
        return None

    game: dict[str, str | list | None] = {}
    game["id"] = item.get("id")
    game["name"] = find_child_text("name", type="primary") or find_child_text("name")
    game["year_published"] = find_child_text("yearpublished")
    game["min_players"] = find_child_text("minplayers")
    game["max_players"] = find_child_text("maxplayers")
    game["min_playtime"] = find_child_text("minplaytime")
    game["max_playtime"] = find_child_text("maxplaytime")
    game["playing_time"] = find_child_text("playingtime")

    stats = item.find("statistics")
    if stats is not None:
        ratings = stats.find("ratings")
        if ratings is not None:
            game["average_rating"] = ratings.find("average").get("value", None)
            game["bayes_average"] = ratings.find("bayesaverage").get("value", None)
            game["users_rated"] = ratings.find("usersrated").get("value", None)
            game["std_dev"] = ratings.find("stddev").get("value", None)
            game["median"] = ratings.find("median").get("value", None)
            game["owned"] = ratings.find("owned").get("value", None)
            game["num_comments"] = ratings.find("numcomments").get("value", None)
            game["num_weights"] = ratings.find("numweights").get("value", None)
            game["average_weight"] = ratings.find("averageweight").get("value", None)

    links = item.findall("link")
    game["categories"] = [
        l.get("value") for l in links if l.get("type") == "boardgamecategory"
    ]
    game["mechanics"] = [
        l.get("value") for l in links if l.get("type") == "boardgamemechanic"
    ]
    game["designers"] = [
        l.get("value") for l in links if l.get("type") == "boardgamedesigner"
    ]
    game["publishers"] = [
        l.get("value") for l in links if l.get("type") == "boardgamepublisher"
    ]

    desc_elem = item.find("description")
    if desc_elem is not None and desc_elem.text:
        desc = desc_elem.text.strip()
        if len(desc) > 400:
            desc = desc[:397] + "..."
        game["description"] = desc

    game["best_player_counts"] = parse_best_player_counts(item)

    return game



class BoardgameCog(commands.Cog):
    """Commands for BoardGameGeek lookups."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="bgg", description="Look up a board game on BoardGameGeek")
    async def bgg_command(self, inter: discord.Interaction, url: str):
        """
        Example:
          /bgg url:https://boardgamegeek.com/boardgame/174430/gloomhaven
        """
        game_id = extract_bgg_id_from_url(url)
        if game_id is None:
            await inter.response.send_message(
                "I couldn't find a valid BoardGameGeek game ID in that link.\n"
                "Make sure it's a `/boardgame/<id>/...` URL.",
                ephemeral=True,
            )
            return

        await inter.response.defer(ephemeral=True)

        game = fetch_bgg_game_data(game_id)
        if game is None:
            await inter.followup.send(
                "Failed to fetch data from BoardGameGeek. "
                "Check the link or try again in a few seconds.",
                ephemeral=True,
            )
            return

        title = game.get("name", f"BGG Game {game_id}")
        year = game.get("year_published")
        if year:
            title = f"{title} ({year})"

        min_players = game.get("min_players")
        max_players = game.get("max_players")

        players_str = None
        if min_players and max_players:
            if min_players == max_players:
                players_str = f"{min_players} players"
            else:
                players_str = f"{min_players}–{max_players} players"

        min_pt = game.get("min_playtime")
        max_pt = game.get("max_playtime")
        playing_time = game.get("playing_time")

        if min_pt and max_pt and min_pt != max_pt:
            time_str = f"{min_pt}–{max_pt} min"
        elif playing_time:
            time_str = f"{playing_time} min"
        else:
            time_str = "Unknown"

        avg_rating = game.get("average_rating")
        users_rated = game.get("users_rated")
        avg_weight = game.get("average_weight")
        num_weights = game.get("num_weights")

        rating_str = "N/A"
        if avg_rating and users_rated:
            rating_str = f"{float(avg_rating):.2f} / 10 ({users_rated} ratings)"
        elif avg_rating:
            rating_str = f"{float(avg_rating):.2f} / 10"

        weight_str = "N/A"
        if avg_weight and num_weights:
            weight_str = f"{float(avg_weight):.2f} / 5 ({num_weights} votes)"
        elif avg_weight:
            weight_str = f"{float(avg_weight):.2f} / 5"

        best_players = game.get("best_player_counts") or []
        if best_players:
            top_counts = [bp[0] for bp in best_players[:3]]
            if len(top_counts) == 1:
                best_players_str = f"Best at {top_counts[0]} players"
            else:
                best_players_str = "Best at " + ", ".join(top_counts) + " players"
        else:
            best_players_str = "No poll data"

        embed = discord.Embed(
            title=title,
            url=url,
            description=game.get("description", "No description available."),
            color=discord.Color.blurple(),
        )

        embed.add_field(name="Players", value=players_str or "Unknown", inline=True)
        embed.add_field(name="Best player counts", value=best_players_str, inline=True)
        embed.add_field(name="Play time", value=time_str, inline=True)
        embed.add_field(name="Weight (complexity)", value=weight_str, inline=True)
        embed.add_field(name="Rating", value=rating_str, inline=True)

        if game.get("categories"):
            embed.add_field(
                name="Categories",
                value=", ".join(game["categories"][:5]),
                inline=False,
            )
        if game.get("mechanics"):
            embed.add_field(
                name="Mechanics",
                value=", ".join(game["mechanics"][:5]),
                inline=False,
            )
        if game.get("designers"):
            embed.add_field(
                name="Designers",
                value=", ".join(game["designers"][:3]),
                inline=False,
            )

        await inter.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BoardgameCog(bot))
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import playercareerstats

career = playercareerstats.PlayerCareerStats(player_id='203999')
print(career.get_data_frames()[0])


games = scoreboard.ScoreBoard()

print(games.get_dict())

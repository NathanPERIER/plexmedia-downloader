

def format_ep_indicator(season: int, episode: int) :
	season_num  = str(season).rjust(2, '0')
	episode_num = str(episode).rjust(2, '0')
	return f"S{season_num}E{episode_num}"

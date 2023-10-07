

def format_ep_indicator(season: int, episode: int) :
	season_num  = str(season).rjust(2, '0')
	episode_num = str(episode).rjust(2, '0')
	return f"S{season_num}E{episode_num}"


def float_2sd(val: float) :
	return f"{val:.2f}".rstrip('0').rstrip('.')


__BYTE_SIZE_UNITS = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']

def format_size_bytes(size_byte: int) :
	val: float = float(size_byte)
	for i in range(len(__BYTE_SIZE_UNITS) - 1) :
		if val >= 1024.0 :
			val /= 1024.0
		else :
			return f"{float_2sd(val)} {__BYTE_SIZE_UNITS[i]}"
	return f"{float_2sd(val)} {__BYTE_SIZE_UNITS[-1]}"

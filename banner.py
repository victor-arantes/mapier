import sys
import time

def progress_bar(total=100, width=40, delay=0.005):
    for i in range(total + 1):
        percent = i / total
        filled = int(width * percent)

        bar = "█" * filled + "░" * (width - filled)

        sys.stdout.write(f"\r|{bar}| {percent:.0%}")
        sys.stdout.flush()
        time.sleep(delay)

    print()



def banner():
	BANNER = r"""
 __  __             _
|  \/  | __ _ _ __ (_) ___ _ __
| |\/| |/ _` | '_ \| |/ _ \ '__|
| |  | | (_| | |_) | |  __/ |
|_|  |_|\__,_| .__/|_|\___|_|
	     |_|
v0.1
======================================

	"""
	print(BANNER)



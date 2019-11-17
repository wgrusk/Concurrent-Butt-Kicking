import sys
import requests
import json
import initializePlayer


USAGE = "Usage: python3 joinGame.py HOST-IP"

# For printing to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main(argv):
    hostIP = assert_args(argv)
    if hostIP == -1:
        return -1

    playerIP = get_IP()
    initialize.InitializePlayer(playerIP).join_lobby_run_game(hostIP)


def assert_args(argv):
    if len(argv) != 2:
        eprint("Invalid arguments")
        eprint(USAGE)
        return -1

    return argv[1]


def get_IP():
    url = "https://ifconfig.me/"
    r = requests.post(url)
    r = r.json()["ip"]
    return r


if __name__ == "__main__":
    main(sys.argv)

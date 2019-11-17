import initializeHost
import requests
import json

def main():
    hostIP = get_IP()
    initialize.InitializeHost(hostIP).create_lobby_run_game()


def get_IP():
    url = "https://ifconfig.me/"
    r = requests.post(url)
    r = r.json()["ip"]
    return r


if __name__ == "__main__":
    main()

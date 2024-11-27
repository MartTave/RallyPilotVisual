def parseArgs(args: list) -> dict:
    res = {}
    if "-h" in args:
        print(
            """
Game launcher for RallyRoboPilot
python scripts/main.py [-h] [-t <float>] [-f <int>] [-r]
    -h : Display this help message
    -t [float] : Set the time step in seconds
    -f [int] : Set the framerate
    -r : Run in real time
"""
        )
        return
    if "-t" in args:
        res["time"] = float(args[args.index("-t") + 1])
    if "-f" in args:
        res["framerate"] = int(args[args.index("-f") + 1])
    if "-r" in args:
        res["realTime"] = True
    return res

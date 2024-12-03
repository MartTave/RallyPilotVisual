import csv
import sys
from time import sleep

from algo_Ga import GaDataGeneration
from conversions import Convertion
from master import Master
class computeMultipleGA():
    def __init__(self, masters:list[Master], folder_names:list[str]):
        self.masters = masters
        self.folder_names = folder_names
        pass

    def runSimulations(self, ngen=100, patience=15, pop_size=75):
        for f in self.folder_names:
            conv = Convertion(f)
            jsonData = conv.readJson()
            master = None
            while master is None:
                for m in self.masters:
                    if m.free:
                        master = m
                        break
                print("No masters available... Waiting !")
                sleep(5)

            if conv.hasResults():
                print(f"Results already computed for {f}")
                print(f"Taking result as base controls !")
                prevRes = conv.readResults()
                ga = GaDataGeneration(
                    jsonData,
                    m,
                    pop_size=len(prevRes.keys()),
                    ngen=ngen,
                    patience=patience,
                    previousResults=prevRes,
                )
            else:
                ga = GaDataGeneration(
                    jsonData,
                    m,
                    pop_size=pop_size,
                    ngen=ngen,
                    patience=patience,
                )

            res,fitness_values = ga.run_ga()
            master.free = True
            conv.writeJsonFile(res)
            conv.writeFitnessValues(fitness_values)
        for m in self.masters:
            m.stopContainers()


if __name__ == '__main__':

    def parseArgs(args):
        res = {
            "portStart": 5000,
            "portEnd": 5001,
            "patience": 15,
            "nGen": 100,
            "gaStart": 0,
            "gaEnd": 1,
            "local": False,
        }
        if "--ports" in args:
            port = args[args.index("--ports") + 1].split(":")
            if len(port) != 2:
                print("Invalid port range")
                sys.exit(1)
            res["portStart"] = int(port[0])
            res["portEnd"] = int(port[1])
        if "--ga-range" in args:
            ga = args[args.index("--ga-range") + 1].split(":")
            if len(ga) != 2:
                print("Invalid ga range")
                sys.exit(1)
            res["gaStart"] = int(ga[0])
            res["gaEnd"] = int(ga[1])
        if "--gen" in args:
            res["nGen"] = int(args[args.index("--gen") + 1])
        if "--pop" in args:
            res["popSize"] = int(args[args.index("--pop") + 1])
        if "--patience" in args:
            res["patience"] = int(args[args.index("--patience") + 1])
        if "-l" in args or "--local" in args:
            res["local"] = True
        if "-h" in args or "--help" in args:
            print(
                """===========================
GA Launcher
Usage : python GA/computeMultipleGA.py [OPTIONS]
    --ports <start>:<end> : Set the port range for the masters
    --ga-range <start>:<end> : Set the range of the GA folders
    --gen <int> : Set the number of generations
    --pop <int> : Set the population size
    --patience <int> : Set the patience
    -l --local : Run in local mode
    -h --help : Display this help message
==========================="""
            )
            sys.exit(0)
        if not "popSize" in res:
            res["popSize"] = res["portEnd"] - res["portStart"]
        print(
            f"""
===========================
GA Launcher
Launching GA with the following parameters :
    Port range :        {res["portStart"]:04d} - {res["portEnd"]:04d}
    GA folder range :   {res["gaStart"]:02d} - {res["gaEnd"]:02d}
    Generations :       {res["nGen"]}
    Population size :   {res["popSize"]}
    Patience :          {res["patience"]}
===========================
"""
        )

        return res

    params = parseArgs(sys.argv)

    masters = [Master(range(params["portStart"], params["portEnd"]), params["local"])]

    test = computeMultipleGA(
        masters, [f"ga_{i}" for i in range(params["gaStart"], params["gaEnd"])]
    )
    test.runSimulations(
        pop_size=params["popSize"],
        patience=params["patience"],
        ngen=params["nGen"],
    )

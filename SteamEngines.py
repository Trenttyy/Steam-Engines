import json
import wptools
import urllib.request
import urllib.parse
import csv
import time
import datetime
import threading
import SteamEngine

### FUNCTIONS

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

### PARSE STEAM APPS

inputfilename = input("Input Steam file name: ")
inputfile = open(inputfilename, mode="rb")

print("Parsing Steam apps... ", end="")
steamapps_json = json.load(inputfile)
steamapps = []

for steamapp_json in steamapps_json["applist"]["apps"]:
    # change to "name" below if using original research function
    steamapps.append(steamapp_json)

inputfile.close()

print("Done.")

### GET ENGINES

print("There are " + str(len(steamapps)) + " Steam apps in total.")
start = int(input("How many have you researched already? "))
mode = ""
while True:
    mode = input("Continue current engines.csv or create new? (continue/create) ")
    if mode == "continue" or mode == "create":
        break
limit = int(input("How many do you want to research? (Type 0 for max) "))
if limit == 0:
    limit = len(steamapps)

threadcount = int(input("How many threads do you want to use? "))

print("Make sure to close engines.csv!!!")
print("Researching engines...")

def researchThread(threadapps):
    global appcount
    
    for steamapp in threadapps:
        engine, source = SteamEngine.research_engine(steamapp["appid"], steamapp["name"])

        gameengines.append(
            {
                "id": steamapp["appid"],
                "name": steamapp["name"],
                "engine": engine,
                "source": source
                }
            )

        appcount += 1
        current_time = time.time()
        passed_time = current_time - start_time
        eta_seconds = passed_time / appcount * (limit - appcount)
        eta = str(datetime.timedelta(seconds=eta_seconds)).split(".")[0]

        requeststring = ""
        for source in SteamEngine.requestcounters:
            requeststring += (source + ": "
                  + str(int(SteamEngine.requestcounters[source] / passed_time))
                  + "req/s   ")
        
        print("\n\n" + str(appcount)
              + " out of " + str(limit) + " apps researched. ("
              + str(int(appcount/limit*100))
              + "%, time remaining " + eta + ")\n"
              + requeststring, end="")

gameengines = []
appcount = 0
start_time = time.time()

limitedsteamapps = steamapps[start:][:limit]
threadsapps = chunkIt(limitedsteamapps, threadcount)
threads = []
for threadapps in threadsapps:
    thread = threading.Thread(target=researchThread, args=[threadapps])
    thread.daemon = True
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("\nDone.")

### EXPORT TO CSV

print("Exporting to engines.csv... ", end="")

file_mode = ""
if mode == "continue":
    file_mode = "a"
elif mode == "create":
    file_mode = "w"
outputfile = open("engines.csv", file_mode, newline="", encoding="utf-8")
writer = csv.writer(outputfile, delimiter=",")
if mode == "create":
    writer.writerow(["Game ID", "Game Name", "Engine", "Source"])

for gameengine in gameengines:
    writer.writerow([gameengine["id"], gameengine["name"], gameengine["engine"], gameengine["source"]])
    
outputfile.close()

print("Done.")

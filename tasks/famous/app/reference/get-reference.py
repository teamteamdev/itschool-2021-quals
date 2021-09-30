#!/usr/bin/env python3

import json
import mwclient
import sys
import traceback
import tqdm

def fetch_people():
    gcmcontinue = ""
    while True:
        sys.stderr.write(gcmcontinue + "...\n")
        data = ruwiki.api("query", generator="categorymembers", gcmtitle="Категория:Родившиеся в Санкт-Петербурге",
                          gcmnamespace=0, gcmlimit=100, prop="pageprops", gcmcontinue=gcmcontinue)
        for p in data["query"]["pages"].values():
            yield {"name": p["title"], "born": None, "died": None,
                   "wikidata": p.get("pageprops", {}).get("wikibase_item")}
                   "pic": p.get("pageprops", {}).get("page_image_free")}
        gcmcontinue = data.get("continue", {}).get("gcmcontinue")
        if not gcmcontinue:
            break


ruwiki = mwclient.Site("ru.wikipedia.org")
wikidata = mwclient.Site("www.wikidata.org")

people = list(fetch_people())

result = []
errors = {}

degrees = {}
for person in tqdm.tqdm(people):
    try:
        if not person["wikidata"]:
            continue

        wikibase = wikidata.api("wbgetentities", ids=person["wikidata"])

        degree_claim = wikibase["entities"][person["wikidata"]]["claims"].get("P512")
        if not degree_claim:
            continue

        degree_id = degree_claim[0]["mainsnak"]["datavalue"]["value"]["id"]
        if not degree_id in degrees: 
            degree_wikibase = wikidata.api("wbgetentities", ids=degree_id)
        
            degree_subclass_claim = degree_wikibase["entities"][degree_id]["claims"].get("P279")
            if degree_subclass_claim:
                degrees[degree_id] = degree_subclass_claim[0]["mainsnak"]["datavalue"]["value"]["id"] in {"Q2628227", "Q737462"}
            else:
                degrees[degree_id] = False

        if not degrees[degree_id]:
            continue

        born_claim = wikibase["entities"][person["wikidata"]]["claims"].get("P569")
        if born_claim:
            try:
                person["born"] = int(born_claim[0]["mainsnak"]["datavalue"]["value"]["time"][1:5])
            except:
                pass

        died_claim = wikibase["entities"][person["wikidata"]]["claims"].get("P570")
        if died_claim:
            try:
                person["died"] = int(died_claim[0]["mainsnak"]["datavalue"]["value"]["time"][1:5])
            except:
                pass

        del person["wikidata"]

        result.append(person)
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        errors[person["name"]] = traceback.format_exc()

json.dump(result, open("result.json", "w"), indent=2, ensure_ascii=False)
json.dump(errors, sys.stdout, indent=2, ensure_ascii=False)

import requests
from numpy import unique
from datetime import date, datetime

ID_API = "https://covid19.figshare.com/api/institutions/857/"
FIGSHARE_API = "https://api.figshare.com/v2/articles/"

def getFigshare(id_url, api_url, testing=False):
    not_complete = True
    i = 0
    size = 1000
    ids = []
    # First calls: get the COVID-related IDs
    while(not_complete):
        new_ids = getIDs(id_url, i * size, size)
        if(len(new_ids) == 0):
            not_complete = False
        else:
            print(f"Fetched IDs {i*size +1} - {(i+1)*size}")
            ids.extend(new_ids)
            i += 1
    print("Finished API call to get COVID-19 ID list")
    # Second call: get the metadata associated with said ID.
    # The call to /institutions pulls SOME metadata, but not all (of course.  Why would things be simple?)
    if(testing):
        ids = ids[0:5]
    md = [cleanupFigshare(api_url, id, idx, len(ids))
          for idx, id in enumerate(ids)]
    unique_ids = len(set([entry["_id"] for entry in md if entry]))
    if(unique_ids != len(md)):
        print("\nWARNING: IDs are not unique, or some requests returned an error!")
        print(f"\n{len(md) - unique_ids} missing or duplicated unique ids")
    print("DONE!")

    return(md)

def getIDs(id_url, page=0, size=1000):
    resp = requests.get(f"{id_url}items?&page={page}&page_size={size}")
    if resp.status_code == 200:
        raw_data = resp.json()
        # First call: get the COVID-related IDs
        ids = [item["data"]["id"] for item in raw_data["items"]]
        return(ids)

def cleanupFigshare(api_url, id, idx, total):
    if(idx % 10 == 0):
        print(f"finished {idx} of {total}")

    resp = requests.get(f"{api_url}{id}")
    if resp.status_code == 200:
        entry = resp.json()
        today = date.today().strftime("%Y-%m-%d")
        md = {"curatedBy": {"@type": "Organization",
                            "url": entry["figshare_url"], "name": "Figshare", "curationDate": today}}
        md["@type"] = standardizeType(entry["defined_type_name"])
        md["_id"] = f'figshare{entry["id"]}'
        md["identifier"] = entry["id"]
        md["doi"] = entry["doi"]
        md["name"] = entry["title"]
        md["url"] = entry["figshare_url"]
        md["description"] = entry["description"]
        md["author"] = [{"@type": "Person", "name": author["full_name"]}
                        for author in entry["authors"]]
        md["funding"] = [getFunder(grant) for grant in entry["funding_list"]]
        md["dateModified"] = standardizeDate(entry["modified_date"])
        md["dateCreated"] = standardizeDate(entry["created_date"])
        md["datePublished"] = standardizeDate(entry["published_date"])
        cats = [category["title"] for category in entry["categories"]]
        cats.extend(entry["tags"])
        md["keywords"] = list(unique(cats))
        md["license"] = entry["license"]["url"]
        md["isBasedOn"] = [{"url": ref} for ref in entry["references"]]
        if ("files" in entry.keys()):
            md["distribution"] = [
                {"name": fileobj["name"], "contentUrl": fileobj["download_url"]} for fileobj in entry["files"]]
        if("custom_fields" in entry.keys()):
            md["citedBy"] = getCited(entry)

        return(md)
    else:
        print(f"\tReturned {resp.status_code} error for id {id}")



def standardizeType(type):
    # standardizing to schema.org types
    type_dict = {
        "dataset": "Dataset",
        "journal contribution": "Publication",
        "preprint": "Publication",
        "figure": "ImageObject",
        "online resource": "Website",
        "media": "MediaObject",
        "presentation": "PresentationDigitalDocument",
        "poster": "CreativeWork",
        "software": "SoftwareSourceCode",
        "thesis": "Publication",
        "book": "Publication"
    }
    try:
        return(type_dict[type])
    except:
        return(type.title())


def standardizeDate(date_string, format="%Y-%m-%dT%H:%M:%SZ", output_format="%Y-%m-%d"):
    try:
        date_time = datetime.strptime(date_string, format)
        return date_time.strftime(output_format)
    except:
        return(date_string)


# TODO: within ["custom_fields"], for nih.figshare, there's more info about the funding within
# "Select an IC:". However, it's not super obvious how to map the ICs into funding, because
# both `Select an IC` and `funding_list` are arrays... should the names be zipped? copy multiple to each?
# etc. Since as of now there are only 3 entries from NIH Figshare, delaying till later.
# IDs: 12272015, 12026910, 12111570
def getFunder(grant):
    funding = {"@type": "MonetaryGrant"}
    if((grant["grant_code"] == grant["grant_code"]) & (grant["grant_code"] != "")):
        funding["identifier"] = grant["grant_code"]
    funding["description"] = grant["title"]
    if((grant["funder_name"] == grant["funder_name"]) & (grant["funder_name"] is not None)):
        funding["funder"] = [{"@type": "Organization",
                             "name": grant["funder_name"]}]
    return(funding)


def getCited(entry):
    cited = []
    names = [item["name"] for item in entry["custom_fields"]]
    if("DOI(s) of associated publication(s):" in names):
        pubs = filter(lambda x: x["name"] == "DOI(s) of associated publication(s):", entry["custom_fields"])
        for pubobj in pubs:
            cited.extend([{"@type": "Publication", "identifier": pub.replace("https://doi.org/", ""), "doi": pub.replace("https://doi.org/", ""), "url": pub} for pub in pubobj["value"]])
    if("Published in" in names):
        citation = {"@type": "Publication"}
        citation = getCustomValue(entry["custom_fields"], citation, "Published in", "journalName")
        citation = getCustomValue(entry["custom_fields"], citation, "Volume", "volumeNumber")
        citation = getCustomValue(entry["custom_fields"], citation, "Issue", "issueNumber")
        citation = getCustomValue(entry["custom_fields"], citation, "Pages", "pagination")
        citation = getCustomValue(entry["custom_fields"], citation, "Citation", "citation")
        citation = getCustomValue(entry["custom_fields"], citation, "Publication date", "datePublished")
        citation = getCustomValue(entry["custom_fields"], citation, "Acceptance date", "dateModified")
        citation = getCustomValue(entry["custom_fields"], citation, "DOI", "doi")
        cited.append(citation)
    if(len(cited) > 0):
        return(cited)

def getCustomValue(arr, citation_obj, fieldname, new_name):
    names = [item["name"] for item in arr]
    if(fieldname in names):
        # Assumption: should only be one entry
        filtered = filter(lambda x: x["name"] == fieldname, arr)
        try:
            val = list(filtered)[0]["value"]
            if(val != ""):
                citation_obj[new_name] = val
            return(citation_obj)
        except:
            return(citation_obj)

# testing functions
# cleanupFigshare(FIGSHARE_API, 12116301, 0, 1)
# cleanupFigshare(FIGSHARE_API, 12111570, 0, 1)
# x = getFigshare(ID_API, FIGSHARE_API, True) # Get a sample of the first five records
# x = getFigshare(ID_API, FIGSHARE_API, False) # Get all Figshare records
# import random
# random.sample(x,1)


def load_annotations():
    docs = getFigshare(ID_API, FIGSHARE_API)
    for doc in docs:
        yield doc

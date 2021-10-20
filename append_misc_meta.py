import os
import json

def find_gen_path():
    tmp_dir = os.getcwd()
    while 'topic_classifier' not in os.listdir(tmp_dir):
        tmp_dir = os.path.dirname(tmp_dir)
    return(tmp_dir)

def fetch_path_dict():
    general_path = find_gen_path()
    topic_folder = os.path.join(general_path,'topic_classifier')
    topic_results = os.path.join(topic_folder,'results')
    alt_path = os.path.join(general_path,'covid_altmetrics')
    alt_results = os.path.join(alt_path,'results')
    preprint_path = os.path.join(general_path,'outbreak_preprint_matcher')
    preprint_results = os.path.join(preprint_path,'results')
    preprint_dumps = os.path.join(preprint_results,'update dumps')
    loe_ann_path = os.path.join(general_path,'covid19_LST_annotations')
    loe_results = os.path.join(loe_ann_path,'results')
    path_dict = {
        'topics_file':os.path.join(topic_results,'topicCats.json'),
        'altmetrics_file':os.path.join(alt_results,'altmetric_annotations.json'),
        'litcovid_updates':os.path.join(preprint_dumps,'litcovid_update_file.json'),
        'preprint_updates':os.path.join(preprint_dumps,'preprint_update_file.json'),
        'loe_annotations':os.path.join(loe_results,'loe_annotations.json')
        }
    return(path_dict)


def fetch_annotation(path_dict,source,outbreak_id):
    with open(path_dict[source],'r') as infile:
        ann_dict = json.load(infile)
    ann_info = [x for x in ann_dict if x["_id"]==outbreak_id]
    try:
        return(ann_info[0])
    except:
        return(ann_info)

    
def add_anns(path_dict,doc):
    ## add corrections
    if doc['@type']=='Publication':
        if 'pmid' in doc['_id']:
            ## doc is from litcovid
            corrections = fetch_annotation(path_dict,'litcovid_updates',doc['_id'])
            loe_info = fetch_annotation(path_dict,'loe_annotations',doc['_id'])
        else:
            corrections = fetch_annotation(path_dict,'preprint_updates',doc['_id'])
            loe_info = None
        if corrections != None and len(corrections)>0 and corrections!="[]":
            if 'correction' in doc.keys():  ## check if correction field already used
                try:
                    doc['correction'].append(corrections["correction"][0])
                except:
                    correct_object = doc['correction']
                    doc['correction']=[correct_object,corrections["correction"][0]]
            else:
                doc['correction']=corrections["correction"][0]
        if loe_info != None and len(loe_info)>0 and loe_info!="[]":
            doc['evaluations'] = loe_info['evaluations']
            if 'citedBy' in doc.keys():
                doc['citedBy'].append(loe_info['citedBy'])
            else:
                doc['citedBy'] = []
                doc['citedBy'].append(loe_info['citedBy'])
    ## add topic_cats
    topic_cats = fetch_annotation(path_dict,'topics_file',doc['_id'])
    if topic_cats != None and len(topic_cats)>0 and topic_cats!="[]":
        topicslist=topic_cats['topicCategory'].replace("'","").strip("[").strip("]").split(",")
        doc['topicCategory']=[x.strip(" ") for x in topicslist]
    ## add altmetrics
    altinfo = fetch_annotation(path_dict,'altmetrics_file',doc['_id'])
    if altinfo != None and len(altinfo)>0:
        if 'evaluations' in doc.keys():
            try:
                doc['evaluations'].append(altinfo['evaluations'][0])
            except:
                eval_object = doc['evaluations']
                doc['evaluations']=[eval_object,altinfo['evaluations'][0]]
        else:
            doc['evaluations'] = altinfo['evaluations']       
    return(doc)
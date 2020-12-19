from pymongo import MongoClient
import time
# process posts time: 29.97282314300537 seconds
# insert posts time: 19.52128267288208 seconds
# create index time: 0.0016009807586669922 seconds
# Tags and votes insert time: 71.00100088119507 seconds
# Entire Program: 120.50462007522583 seconds
import ijson
import re

def main():
    port = int(input("Please input a port number to use: "))
    start_time = time.time()
    client = MongoClient('localhost', port, w=0)  # 27017
    db = client['291db']
    db.drop_collection('Posts')
    db.drop_collection('Tags')
    db.drop_collection('Votes')
    Posts_291db = db['Posts']
    Tags_291db = db['Tags']
    Votes_291db = db['Votes']

    load_data = time.time()
    with open('Posts.json') as fp:
        objects = ijson.items(fp, 'posts')
        for obj in objects:
            for entry in obj['row']:
                temp = []
                if 'Body' in entry and 'Title' in entry:
                    temp += re.findall(r"[\w']+|[.,!?;]", entry.get('Body'))+re.findall(r"[\w']+|[.,!?;]", entry.get('Title'))
                elif 'Body' in entry:
                    temp += re.findall(r"[\w']+|[.,!?;]", entry.get('Body'))
                elif 'Title' in entry:
                    temp += re.findall(r"[\w']+|[.,!?;]", entry.get('Title'))
                entry['terms'] = list(set(t.lower() for t in temp if len(t) >= 3))  # O(1)
            print("process posts time: %s seconds" % (time.time() - load_data))
            process = time.time()
            Posts_291db.insert_many(obj['row'], ordered=False)
            print("insert posts time: %s seconds" % (time.time() - process))
    cc = time.time()
    Posts_291db.create_index([("terms", 1)])
    print("create index time: %s seconds" % (time.time() - cc))

    time2 = time.time()
    with open('Votes.json') as pp:
        objects1 = ijson.items(pp, 'votes.row')
        for obj1 in objects1:
            Votes_291db.insert_many(obj1, ordered=False)

    with open('Tags.json') as p:
        objects2 = ijson.items(p, 'tags.row')
        for obj2 in objects2:
            Tags_291db.insert_many(obj2, ordered=False)

    print("Tags and votes insert time: %s seconds" % (time.time() - time2))

    print("Entire Program: %s seconds" % (time.time() - start_time))


if __name__ == '__main__':
    main()

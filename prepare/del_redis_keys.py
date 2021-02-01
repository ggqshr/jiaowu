from sys import argv,path
path.append("..")
from config import r_client

if __name__ == "__main__":
    keys = argv[1]
    print("del pattern %s" % keys)
    r_client.delete(keys)
    with r_client.pipeline(transaction=False) as p:
        keys = p.keys(keys).execute()
        for kk in keys:
            for key in kk:
                p.delete(key)
            p.execute()

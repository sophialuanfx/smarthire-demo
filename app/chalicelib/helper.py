import pandas as pd
from apify_client import ApifyClient
from datetime import datetime
from opensearchpy import OpenSearch, helpers

#insert your info
apify_client = ApifyClient('')
opeansearch_aws=''

def getApiInfo(job_titles, locations):
    # Start an actor and wait for it to finish
    position_df = pd.DataFrame()
    job_titles = job_titles
    locations = locations

    for uule in locations:
        print(locations[uule])
        for jt in job_titles:
            print(jt)
            run_input = {
                "csvFriendlyOutput": True,
                "includeUnfilteredResults": False,
                "maxConcurrency": 10,
                "maxPagesPerQuery": 3,
                "queries": f"https://www.google.com/search?ibp=htl;jobs&q={jt}&uule={uule}",
                "saveHtml": False,
                "saveHtmlToKeyValueStore": False,
            }

            actor_call = apify_client.actor(
                'dan.scraper/google-jobs-scraper').call(run_input=run_input)

            dataset_items = apify_client.dataset(
                actor_call['defaultDatasetId']).list_items().items

            d = pd.DataFrame(dataset_items)
            d["query"] = jt
            d["location"] = locations[uule]
            d["run_time"] = str(datetime.now())

            position_df = pd.concat([position_df, d])

        print("="*30)
        break # Only Run For Toronto

    position_df.groupby("location")["query"].value_counts()

    _ = position_df.pop("thumbnail") # not useful, with na values
    #_ = position_df.insert(1,"publishDate", pd.Timestamp.now())
    position_df.to_csv("./data/raw_google_1129.csv", index=False)

    position_df.head()
    return position_df


##change to aws opeansearch
def connectOpeanSearch(position_df):
    host = opeansearch_aws
    port = 443
    auth = ('swift', 'Hire123!') # For testing only. Don't store credentials in code.

    client = OpenSearch(
        hosts = [{'host': host, 'port': port}],
        http_compress = True, # enables gzip compression for request bodies
        http_auth = auth,
        use_ssl = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
    )

    print(client.info)

    index_name = "swift_dev"

    if not client.indices.exists(index_name):
        client.indices.create(index=index_name) 

    def doc_generator(df):
        for i, row in df.iterrows():
            doc = {
                "_index": index_name,
                "_source": row.to_dict(),
            }
            yield doc

        helpers.bulk(client, doc_generator(position_df))

        print("Data Saved to ES")
        position_df["query"].value_counts()

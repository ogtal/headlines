import pandas as pd

from orm import Whitelist_Media, Media, Ignored_Links
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()

q_stmt = session.query(Whitelist_Media).statement
media = pd.read_sql(q_stmt, session.bind) 

df = pd.read_csv('headlines_raw.csv', index_col=0, sep=';',
                   names=['id', 'date', 'frontpage_url', 'link_id', 
                   'link_percent_max_id', 'to_link_url', 'link_text'],
                   parse_dates=True, nrows=40000)


#def add_new_media():
#    for row in session.query(Whitelist_Media).all():
#        for url in row.urls:



for row in session.query(Whitelist_Media).all():
    for url in row.urls:
        sub_df = df[df.frontpage_url == url.url]
        link_id_count = sub_df.groupby('link_id').nunique() 
        stable_link_ids = link_id_count[link_id_count.to_link_url == 1].index.to_list()
        df_stable_link_ids = sub_df[sub_df.link_id.isin(stable_link_ids)]

        links_to_ignore = df_stable_link_ids.to_link_url.unique() 

        #for link in links_to_ignore:
           
 
#for media_name in media.name:
#    link_list = 
# Load data for the last year 

#Loop over media whitelist

    # Find links that don't change position over a year

    # Add to ignored links

    # Check if there are multilpe links - determine which to use and which to ignore. 

#inspect and see if 

# Find links that don't change over a month. 


# Print a list of media we did'nt include for manual reference. 
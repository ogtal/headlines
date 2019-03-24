import pandas as pd

from db_raw import Headlines_Raw
from orm import Whitelist_Media, Media, Ignored_Links
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ogtal_secrets import mysql_stat_url


def find_ignorable_links(df):
    link_id_count = df.groupby('link_id').nunique() 
    stable_link_ids = link_id_count[link_id_count.to_link_url == 1].index.to_list()
    df_stable_link_ids = df[df.link_id.isin(stable_link_ids)]

    links_to_ignore = list(df_stable_link_ids.to_link_url.unique())
    return(links_to_ignore)

def get_raw_data(media_name):
    result = session.\
                query(Whitelist_Media).\
                filter(Whitelist_Media.name==name).first()

    url_list = []
    for i in result.urls:
        url_list.append(i.url)

    q_stmt = session_raw.\
                query(Headlines_Raw).\
                filter(Headlines_Raw.frontpage_url.in_(url_list)).\
                limit(100000).statement

    df = pd.read_sql(q_stmt, engine_raw)
    return(df)

def add_links_to_db(links_to_ignore):
    for link in links_to_ignore:
        if not session.query(Ignored_Links).filter(Ignored_Links.url == link).count():
            new_ig_link = Ignored_Links(url = link, media_id=media_id)
            session.add(new_ig_link)
            session.commit()
     

engine_raw = create_engine(mysql_stat_url.format(db="headlines"), pool_recycle=7200)
session_raw = sessionmaker(bind=engine_raw)()

engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()

q_stmt = session.query(Whitelist_Media).statement
media = pd.read_sql(q_stmt, session.bind) 

for name in media.name[0:1]:
    media_id = media[media.name == name].id.item()

    df = get_raw_data(media_name)
    links_to_ignore = find_ignorable_links(df)
    add_links_to_db(links_to_ignore)


import pandas as pd

from db_raw import Headlines_Raw
from orm import Whitelist_Media, Media_Urls, State, Media, Ignored_Links
from ogtal_secrets import mysql_stat_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from sqlalchemy import create_engine

engine_raw = create_engine(mysql_stat_url.format(db="headlines"), pool_recycle=7200)
session_raw = sessionmaker(bind=engine_raw)()

engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()


q_stmt = session_raw.query(Headlines_Raw).limit(100000).statement

df = pd.read_sql(q_stmt, engine_raw)

media_url = 'https://politiken.dk/'
sub_df = df[df.frontpage_url == media_url].drop_duplicates('to_link_url')

q_stmt = session.query(Ignored_Links).statement
df_ignored_links = pd.read_sql(q_stmt, engine)

sub_df = sub_df[~sub_df.to_link_url.isin(df_ignored_links.url.to_list())] 

#Add this to download cache 

#Loop over media 

# When cache is done - check if we already have downloaded this data by lookups. 

# 


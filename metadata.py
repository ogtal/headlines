import pandas as pd

from orm import Whitelist_Media, Whitelist_Urls, State
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()

states = pd.read_csv('data/states.csv')
whitelist = pd.read_csv('data/whitelist_media.csv')

#for i, row in states.iterrows():
#    session.add(State(**row.to_dict()))

media = whitelist.frontpage_name.unique()

for i, m in enumerate(media):
    sub_df = whitelist[whitelist.frontpage_name == m].frontpage_url
    w_m = Whitelist_Media(name=m)
    for i, item in sub_df.iteritems():
        w_u = Whitelist_Urls(url=item)
        w_m.urls.append(w_u)
    session.add(w_m)
    session.commit()

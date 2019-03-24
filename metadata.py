import pandas as pd

from orm import Whitelist_Media, Media_Urls, State, Media, Ignored_Links
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()

# This needs to be read from raw
# on something date based such that 
df = pd.read_csv('headlines_raw.csv', index_col=0, sep=';',
                   names=['id', 'date', 'frontpage_url', 'link_id', 
                   'link_percent_max_id', 'to_link_url', 'link_text'],
                   parse_dates=True, nrows=40000)


class db_static:
    @classmethod
    def add_states(self):
        states = pd.read_csv('data/states.csv')
        for i, row in states.iterrows():
            res = session.query(State).filter(State.state == row['state']).first()
            if not res:
                session.add(State(**row.to_dict()))
            session.commit()

class db_variable:
    @classmethod
    def update_whitelist(self):
        whitelist = pd.read_csv('data/whitelist_media.csv')

        media = whitelist.frontpage_name.unique()

        for i, m in enumerate(media):
            sub_df = whitelist[whitelist.frontpage_name == m].frontpage_url
            media_res = session.query(Whitelist_Media).filter(Whitelist_Media.name==m).first()
            if not media_res:
                media_res = Whitelist_Media(name=m)
            for i, item in sub_df.iteritems():
                url = Media_Urls(url=item)
                media_res.urls.append(url)
            session.add(media_res)
            session.commit()

    @classmethod
    def update_media(self):
        for row in session.query(Whitelist_Media).all():
            media_res = session.query(Media).filter(Media.name==row.name).first()
            if not media_res:
                media_res = Media(name=row.name)
            for url in row.urls:
                media_res.urls.append(url)
            session.add(media_res)
            session.commit()

    @classmethod
    def update_ignored_links(self):
        for media in session.query(Media).all():
            for url in media.urls:
                sub_df = df[df.frontpage_url == url.url]
                link_id_count = sub_df.groupby('link_id').nunique() 
                stable_link_ids = link_id_count[link_id_count.to_link_url == 1].index.to_list()
                df_stable_link_ids = sub_df[sub_df.link_id.isin(stable_link_ids)]

                links_to_ignore = df_stable_link_ids.to_link_url.unique() 

                for link in links_to_ignore:
                    ign_link = Ignored_Links(url = link)
                    media.ignored_links.append(ign_link)
                session.add(media)
                session.commit()



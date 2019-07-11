import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm import Base, Media, Whitelist_Media, Media_Url
from headlines_helper import create_name_dict

database = 'test.db'

#Start database session
engine = create_engine(str('sqlite:///' + database))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#create dict structure for media and whitelist_media
whitelist_dict = create_name_dict(Whitelist_Media, session)
media_dict = create_name_dict(Media, session)

#read csv file and convert to dataframe
whitelist_df = pd.read_csv('whitelist_media.csv')

#loop through entries
for i, row in whitelist_df.iterrows():
    name = row.frontpage_name
    url = row.frontpage_url
    #check if entry is already a whitelist media
    try:
        whitelist_media = whitelist_dict[name]
        #if the whitelist_media exits so does the media
        media = media_dict[name]
        #check for existance of whitelist media url
        whitelist_media_urls = whitelist_media.urls
        url_exists = False
        #check if the current url is allready connected to the whitelist media
        for u in whitelist_media_urls:
            if u.url == url:
                url_exists = True
                break
        if not url_exists:
            #create url and append to media and whitelist media urls
            media_url = Media_Url(url = url)
            session.add(media_url)
            whitelist_media.urls.append(media_url)
            media.urls.append(media_url)
    except KeyError: #a KeyError will be thrown if the whitelist media is not in the fetched dict
        #create new whitelist media
        whitelist_media = Whitelist_Media(name = name)
        #create a new media
        media = Media(name = name)
        media_url = Media_Url(url = url)
        #connect url to media and whitelist media
        whitelist_media.urls.append(media_url)
        media.urls.append(media_url)
        #add entries to session
        session.add(whitelist_media)
        session.add(media)
        session.add(media_url)
        #add media and whitelist media to respecive dicts
        whitelist_dict[name] = whitelist_media
        media_dict[name] = media
    session.commit()
session.close()


    
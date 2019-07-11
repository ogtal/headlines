import datetime
import time
import csv
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from headlines_helper import create_url_dict
from orm import Base, Ignored_Link, Media, Media_Url

write_to_csv = True
max_pos_diff = 0.25 
max_imobile_time = 4 #days of imobility before being classified as an ignored link
max_seen_times = 400 #minimum times seen before considered for being ignored

database = 'test.db'

engine = create_engine(str('sqlite:///'+ database))
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()



link_df = pd.read_excel('headlines_raw.xlsx', index_col = 0,
                    names=['date', 'frontpage_url', 'link_position', 
                    'link_relative_position', 'to_link_url', 'link_text'], header=None, 
                    parse_dates=True)
link_dict = {}
ignored_link_dict = create_url_dict(Ignored_Link, session)
ignored_tup_dict = {}
media_url_dict = create_url_dict(Media_Url, session)


start = time.time()
for i, row in link_df.iterrows():
    link_url = row.to_link_url
    try:
        ignored_link = ignored_link_dict[link_url]
        continue
    except KeyError:
        link_pos = row.link_position
        link_pos_rel = row.link_relative_position
        link_obs = datetime.datetime.strptime(row.date, '%Y-%m-%d %H:%M:%S')
        try:
            link_tup = link_dict[link_url]
            tup_obs = link_tup[0]
            tup_pos = link_tup[1]
            tup_pos_rel = link_tup[2]
            tup_im_time = link_tup[3]
            tup_seen = link_tup[4]
            #check how far the article has moved since last time observed
            if abs(tup_pos_rel - link_pos_rel) < max_pos_diff:
                im_time = tup_im_time + (tup_obs-link_obs) # it is assumed movement trough the csv is backwards in time
                link_tup = (link_obs, tup_pos, tup_pos_rel, im_time, tup_seen+1)
                link_dict[link_url] = link_tup
                if im_time.days > max_imobile_time or tup_seen > max_seen_times:
                    ignored_link = Ignored_Link(url=link_url)
                    ignored_link_dict[link_url] = ignored_link
                    session.add(ignored_link)
                    media_id = media_url_dict[row.frontpage_url].media_id
                    media = media = session.query(Media)[media_id-1]
                    media.ignored_links.append(ignored_link)
                    session.commit()
                    ignored_tup_dict[link_url] = link_tup
                    print(link_url)
            else:
                #update observation, time position and number of times seen if the article has moved
                link_tup = (link_obs, link_pos, link_pos_rel, datetime.timedelta(0), tup_seen+1)
                link_dict[link_url] = link_tup
        except KeyError:
            link_tup = (link_obs, link_pos, link_pos_rel, datetime.timedelta(0), 1)
            link_dict[link_url] = link_tup
end = time.time() - start
session.close()
if write_to_csv:
    with open('ignore_res.csv', 'w') as write_file:
        writer = csv.writer(write_file)
        for i_link in ignored_tup_dict.keys():
            i_tup = ignored_tup_dict[i_link]
            csv_row = [i_tup[1], i_tup[2], i_tup[3].days, i_tup[4] , i_link]
            writer.writerow(csv_row)
    write_file.close()
import datetime
import time
import pandas as pd
from newspaper import Article as Content
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm import Base, Media, Media_Url, Article, Position, Author, Tag, Graphic, State, State_Time, Ignored_Link
from headlines_helper import create_url_dict, create_name_dict



database = 'test.db'

#Start database session
engine = create_engine(str('sqlite:///' + database))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#create dict for whitelist check
url_dict = create_url_dict(Media_Url, session)
author_dict = create_name_dict(Author, session)
tag_dict = create_name_dict(Tag, session)
state_dict = create_name_dict(State, session)
ignored_dict = create_url_dict(Ignored_Link, session)
article_dict = create_url_dict(Article, session)

ignored_count = 0
before_count = 0

#read xlsx file
df = pd.read_excel('headlines_raw_medium.xlsx', index_col = 0,
                    names=['date', 'frontpage_url', 'link_id', 
                    'link_percent_max_id', 'to_link_url', 'link_text'], header=None, 
                    parse_dates=True)
start_time = time.time()
for i,row in df.iterrows():
    whitelist = False
    #check if frontpage url is all ready linked to a media
    try:
     a_media_url = url_dict[row.frontpage_url]
     media_id = a_media_url.media_id
     whitelist_media_id = a_media_url.whitelist_media_id
     a_media = session.query(Media)[media_id-1] #media ids are not zero indexed
     #Check if article is from a whitelisted media
     if not whitelist_media_id ==   None:
         whitelist = True
     else:
        print('Not a whitelisted media')
        continue
    except KeyError: #KeyError will be thrown if url is not linked to a whitelist media
        print('Not a whitelisted media')
        continue
    a_url = row.to_link_url
    #check if article link is an ignored link
    try:
        ignored_link = ignored_dict[a_url]
        ignored_count += 1
        continue
    except KeyError:
        pass
    #parse observed date to datetime
    a_observed = datetime.datetime.strptime(row.date, '%Y-%m-%d %H:%M:%S')
    #Create newspaper3k article
    #it is assumed that the language of articles is danish
    c = Content(a_url, language = 'da')
    #create position entry
    a_position = Position(pos= row.link_id, pos_relative = row.link_percent_max_id, observed = a_observed)
    session.add(a_position)
    #check 
    try:
        article = article_dict[a_url]
        article.positions.append(a_position)
        session.commit()
        before_count +=1
        continue
    except KeyError:
        pass
    #create article entry with base attributes
    article = Article(published = a_observed, title = row.link_text, text = 'download error', url = a_url)
    #connect article to media and position
    article.positions.append(a_position)
    a_media.articles.append(article)
    #add article to dictionary
    article_dict[a_url] = article
    session.add(article)
    #try to download article content
    try:
        c.download()
        time.sleep(2)
        article.state_times.append(State_Time(state_id = state_dict['Initial download'].id))
        c.parse()
        article.state_times.append(State_Time(state_id = state_dict['Article parsed'].id))
    except:
        #add download failed state to article and continue
        article.state_times.append(State_Time(state_id = state_dict['Download failed'].id))
        session.commit()
        continue
    #get article attributes from newspaper package
    a_text = c.text
    a_title = c.title
    a_html = c.html
    a_published = c.publish_date
    #a_tags = c.tags for now keywords will be used instead of tags
    a_authors = c.authors
    a_images = c.images
    a_videos = c.movies
    
    #process authors
    for author_name in a_authors:
        #check for author existence
        try:
            #try to fetch author from dict
            author = author_dict[author_name]
            article.authors.append(author)
            #check for connection between author and media
            if not  a_media  in author.media:
                #create connection between author and media
                author.media.append(a_media)
        except KeyError:
            #create new author entry and link to article media
            author = Author(name = author_name)
            session.add(author)
            author.media.append(a_media)
            author.articles.append(article)
            #add author to relevant dict
            author_dict[author_name] = author
    article.state_times.append(State_Time(state_id=state_dict['Parsed authors'].id))
    #attempt natural language processingy
    try:
        c.nlp()
    except:
        pass
    #process keywords as tags
    a_keywords = c.keywords
    for word in a_keywords:
        #check for tag existence 
        try:
            tag = tag_dict[word]
            article.tags.append(tag)
        except KeyError:
            #create new tag
            tag = Tag(name = word)
            tag_dict[word] = tag
            session.add(tag)
            article.tags.append(tag)
        #connect article authors to tag
        for author in article.authors:
            if not tag in author.tags:
                author.tags.append(tag)
    article.state_times.append(State_Time(state_id=state_dict['Parsed tags'].id))
    #process images and videos
    for image_url in a_images:
        image = Graphic(url = image_url)
        session.add(image)
        article.graphics.append(image)
    for video_url in a_videos:
        video = Graphic(url = video_url)
        session.add(video)
        article.graphics.append(image)
    #final check for articles and graphics
    if len(article.tags) > 0:
        article.has_tag = True
    if len(article.graphics) > 0:
        article.has_graphic = True
    #commit entries to database
    session.commit()
end_time = time.time() -  start_time
session.close()
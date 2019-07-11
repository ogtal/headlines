from datetime import datetime
from sqlalchemy import create_engine, Column, Table, Integer, String,Float, Date, Text, Numeric, DateTime, ForeignKey, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import LONGTEXT

Base = declarative_base()

at_media_author = Table('media_author', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id')),
    Column('author_id', Integer, ForeignKey('author.id'))
    )

at_article_author = Table('article_author', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('author_id', Integer, ForeignKey('author.id'))
    )

at_article_link = Table('article_link', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('link_id', Integer, ForeignKey('link.id'))
    )

at_article_graphic = Table('article_graphic', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('graphic_id', Integer, ForeignKey('graphic.id'))
    )

at_article_tag = Table('article_tag', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
    )

at_article_position = Table('article_position', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('pos_id', Integer, ForeignKey('position.id'))
    )

at_author_tag = Table('author_tag', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
    )

at_source_tag = Table('source_tag', Base.metadata,
    Column('source_id', Integer, ForeignKey('source.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
    )

at_media_source = Table('media_source', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id')),
    Column('source_id', Integer, ForeignKey('source.id'))
    )

at_article_source = Table('article_source', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('source_id', Integer, ForeignKey('source.id'))
    )

at_article_state = Table('article_state', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('state_id', Integer, ForeignKey('state.id'))
    )


class TimestampMixin:
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="Tidspunkt for, hvornår observationen sidst er blevet ændret")
    inserted_at = Column(DateTime, default=datetime.now, comment="Tidspunkt for, hvornår observationen er blevet indsat i databasen")


class Media(Base, TimestampMixin):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment='Official name of the news website')
    urls = relationship('Media_Url')
    authors = relationship('Author', 
                secondary = at_media_author,
                back_populates='media')
    articles = relationship('Article')
    sources = relationship('Source', 
                secondary = at_media_source,
                back_populates='media')
    ignored_links = relationship('Ignored_Link')

class Article(Base, TimestampMixin):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    published = Column(DateTime, comment='Either from article or from first observation')
    url = Column(Text, nullable=False, comment='The url leading to the article')
    modified = Column(DateTime, comment='Contains modification date if specified by the article')
    title = Column(Text, comment='The title of an article')
    lead_paragraf = Column(Text, comment='lead paragraph')
    text = Column(Text, comment='Article content')
    word_count = Column(Integer, default =0, comment='Number of words in title, lead paragraf and text')
    paywalled = Column(BOOLEAN, default=False, comment='If true: article is behind paywall')
    has_link = Column(BOOLEAN, default=False, comment='If true: article has links')
    has_graphic = Column(BOOLEAN, default=False, comment='If true: article has graphics')
    has_tag = Column(BOOLEAN, default=False, comment='If true: article has tags')
    has_sources = Column(BOOLEAN, default=False, comment='If true: article has sources')
    raw_html = Column(Text, nullable=True, comment='The html from the link, saved for use in later processing')
    media_id = Column(Integer, ForeignKey('media.id'))
    positions = relationship('Position')
    state_times = relationship('State_Time')
    authors = relationship('Author',
                secondary=at_article_author,
                back_populates='articles')
    links = relationship('Link',
                secondary=at_article_link,
                back_populates='articles')
    graphics = relationship('Graphic',
                secondary=at_article_graphic,
                back_populates='articles')
    tags = relationship('Tag',
                secondary=at_article_tag,
                back_populates='articles')
    sources = relationship('Source', 
                secondary = at_article_source,
                back_populates='articles')

class Link(Base, TimestampMixin):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, comment='URLs used in the article')
    articles = relationship('Article',
            secondary=at_article_link,
            back_populates='links')

class State(Base, TimestampMixin):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment='The state of an article, i.e. downloaded, processed, etc.')
    state_description = Column(Text, comment='Our description of the state' )
    state_times = relationship('State_Time')

class Graphic(Base, TimestampMixin):
    __tablename__ = 'graphic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, comment='URL of images, videos, etc. associanted with an article')
    download_path = Column(Text, nullable=True, comment='path to downloaded file')
    articles = relationship('Article',
                secondary=at_article_graphic,
                back_populates='graphics') 

class Tag(Base, TimestampMixin):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(1000), nullable=True, comment='Article tag')
    type = Column(String(100), comment='The type of the tag, say autogenerated, manually tagged, by us etc. ')
    articles = relationship('Article',
                secondary=at_article_tag,
                back_populates='tags')
    authors = relationship('Author',
                secondary=at_author_tag,
                back_populates='tags')
    sources = relationship('Source', 
                secondary = at_source_tag,
                back_populates='tags')

class Position(Base, TimestampMixin):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    pos = Column(Integer, nullable=False, comment='Article position as determined by the raw dataset')
    pos_relative = Column(Numeric, nullable=False, comment='Relative position as determined by the raw dataset')
    observed = Column(DateTime, nullable=False, comment='Time of the position observation')
    size_x = Column(Numeric, nullable=True, comment='Empty for now.')
    size_y = Column(Numeric, nullable=True, comment='Empty for now.')
    pos_x = Column(Numeric, nullable=True, comment='Empty for now.')
    pos_y = Column(Numeric, nullable=True, comment='Empty for now.')


class Author(Base, TimestampMixin):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, comment='name of the author')
    sex = Column(String(500), nullable=True, comment='assumed gender of the author')
    date_of_brith = Column(Date, nullable=True, comment='assumed date of brith of the author')
    bio = Column(Text, nullable=True, comment='biography')
    tags = relationship('Tag', 
                secondary = at_author_tag,
                back_populates='authors')
    media = relationship('Media', 
                secondary = at_media_author,
                back_populates='authors')
    articles = relationship('Article',
                secondary=at_article_author,
                back_populates='authors')
    aliases = relationship('Alias')

class Source(Base, TimestampMixin):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, comment='name of the source')
    bio = Column(Text, nullable=True, comment='biography of the source')
    tags = relationship('Tag', 
                secondary = at_source_tag,
                back_populates='sources')
    media = relationship('Media', 
                secondary = at_media_source,
                back_populates='sources')
    articles = relationship('Article',
                secondary=at_article_source,
                back_populates='sources')
    aliases = relationship('Alias')

class Alias(Base, TimestampMixin):
    __tablename__ = 'alias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('source.id'), nullable=True)

class Ignored_Link(Base, TimestampMixin):
    __tablename__ = 'ignored_link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    media_id = Column(Integer, ForeignKey('media.id'))

class Whitelist_Media(Base, TimestampMixin):
    __tablename__ = 'whitelist_media'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, comment='Official name of the news website')

    urls = relationship('Media_Url')

class Media_Url(Base, TimestampMixin):
    __tablename__ = 'media_url'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, comment='Url of the news website')
    whitelist_media_id = Column(Integer, ForeignKey('whitelist_media.id'))
    media_id = Column(Integer, ForeignKey('media.id'))

class State_Time(Base, TimestampMixin):
    __tablename__ = 'state_time'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    state_id = Column(Integer, ForeignKey('state.id'))

if __name__ == '__main__':
    engine = create_engine('sqlite:///test.db')
    Base.metadata.drop_all(bind=engine, tables=[
    Media.__table__,
    Article.__table__,
    Link.__table__,
    Graphic.__table__,
    Tag.__table__,
    Author.__table__,
    Position.__table__,
    Source.__table__,
    Alias.__table__,
    Ignored_Link.__table__,
    Whitelist_Media.__table__,
    Media_Url.__table__,
    State_Time.__table__
    ])
    Base.metadata.create_all(engine)

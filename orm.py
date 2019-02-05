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

at_article_inferred_tag = Table('article_inferred_tag', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('inferred_tag_id', Integer, ForeignKey('inferred_tag.id'))
    )

at_article_position = Table('article_position', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('pos_id', Integer, ForeignKey('position.id'))
    )

at_author_tag = Table('author_tag', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
    )

at_author_inferred_tag = Table('author_inferred_tag', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id')),
    Column('inferred_tag_id', Integer, ForeignKey('inferred_tag.id'))
    )

at_source_tag = Table('source_tag', Base.metadata,
    Column('source_id', Integer, ForeignKey('source.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
    )

at_source_inferred_tag = Table('source_inferred_tag', Base.metadata,
    Column('source_id', Integer, ForeignKey('source.id')),
    Column('inferred_tag_id', Integer, ForeignKey('inferred_tag.id'))
    )

at_media_source = Table('media_source', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id')),
    Column('source_id', Integer, ForeignKey('source.id'))
    )

at_article_source = Table('article_source', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('source_id', Integer, ForeignKey('source.id'))
    )




class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment='Official name of the news website')
    url = Column(Text, nullable=False, comment='Base url of the news website')
    authors = relationship('Author', 
                secondary = at_media_author,
                back_populates='media')
    articles = relationship('Article')
    sources = relationship('Source', 
                secondary = at_media_source,
                back_populates='media')

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    published = Column(DateTime, nullable=False, comment='Either from article or from first observation')
    modified = Column(DateTime, comment='Contains modification date if specified by the article')
    title = Column(Text, nullable=False, comment='The title of an artcile')
    lead_paragraf = Column(Text, nullable=False, comment='lead paragraph')
    text = Column(Text, nullable=False, comment='Article content')
    word_count = Column(Integer, nullable=False, comment='Number of words in title, lead paragraf and text')
    paywalled = Column(BOOLEAN, nullable=False, comment='If true: article is behind paywall')
    has_link = Column(BOOLEAN, nullable=False, comment='If true: article has links')
    has_graphic = Column(BOOLEAN, nullable=False, comment='If true: article has graphics')
    has_tag = Column(BOOLEAN, nullable=False, comment='If true: article has tags')
    has_inferred_tag = Column(BOOLEAN, nullable=False, comment='If true: article has inferred tags')
    has_sources = Column(BOOLEAN, nullable=False, comment='If true: article has sources')
    media_id = Column(Integer, ForeignKey('media.id'))
    positions = relationship('Position')
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
    inferred_tags = relationship('InferredTag',
                secondary=at_article_inferred_tag,
                back_populates='articles')
    sources = relationship('Source', 
                secondary = at_article_source,
                back_populates='articles')

class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, comment='URLs used in the article')
    articles = relationship('Article',
            secondary=at_article_link,
            back_populates='links')


class Graphic(Base):
    __tablename__ = 'graphic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, comment='URL of images, videos, etc. associanted with an article')
    download_path = Column(Text, nullable=True, comment='path to downloaded file')
    articles = relationship('Article',
                secondary=at_article_graphic,
                back_populates='graphics') 

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(1000), nullable=True, comment='Article tags form the website')
    articles = relationship('Article',
                secondary=at_article_tag,
                back_populates='tags')
    authors = relationship('Author',
                secondary=at_author_tag,
                back_populates='topics')
    sources = relationship('Source', 
                secondary = at_source_tag,
                back_populates='topics')


class InferredTag(Base):
    __tablename__ = 'inferred_tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    inferred_tag = Column(String(1000), nullable=True, comment='Article tags we generate')
    articles = relationship('Article',
                secondary=at_article_inferred_tag,
                back_populates='inferred_tags')
    authors = relationship('Author',
                secondary=at_author_inferred_tag,
                back_populates='topics_inferred')
    sources = relationship('Source', 
                secondary = at_source_inferred_tag,
                back_populates='topics_inferred')


class Position(Base):
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


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, comment='name of the author')
    sex = Column(String(500), nullable=True, comment='assumed gender of the author')
    date_of_brith = Column(Date, nullable=True, comment='assumed date of brith of the author')
    bio = Column(Text, nullable=True, comment='biography')
    topics = relationship('Tag', 
                secondary = at_author_tag,
                back_populates='authors')
    topics_inferred = relationship('InferredTag', 
                secondary = at_author_inferred_tag,
                back_populates='authors')
    media = relationship('Media', 
                secondary = at_media_author,
                back_populates='authors')
    articles = relationship('Article',
                secondary=at_article_author,
                back_populates='authors')
    aliases = relationship('Alias')

class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, comment='name of the source')
    bio = Column(Text, nullable=True, comment='biography of the source')
    topics = relationship('Tag', 
                secondary = at_source_tag,
                back_populates='sources')
    topics_inferred = relationship('InferredTag', 
                secondary = at_source_inferred_tag,
                back_populates='sources')
    media = relationship('Media', 
                secondary = at_media_source,
                back_populates='sources')
    articles = relationship('Article',
                secondary=at_article_source,
                back_populates='sources')
    aliases = relationship('Alias')

class Alias(Base):
    __tablename__ = 'alias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(500), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('source.id'), nullable=True)


if __name__ == '__main__':
    engine = create_engine('sqlite:///test.db')
    Base.metadata.drop_all(bind=engine, tables=[
    Media.__table__,
    Article.__table__,
    Link.__table__,
    Graphic.__table__,
    Tag.__table__,
    InferredTag.__table__,
    Author.__table__,
    Position.__table__,
    Source.__table__,
    Alias.__table__,
    ])
    Base.metadata.create_all(engine)

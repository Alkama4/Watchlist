from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Date, Text, Boolean, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


####### Enums #######

class TitleType(enum.Enum):
    movie = "movie"
    tv = "tv"

class ImageType(enum.Enum):
    poster = "poster"
    backdrop = "backdrop"
    logo = "logo"


####### Tables #######

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Title(Base):
    __tablename__ = "titles"

    title_id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, unique=True)
    imdb_id = Column(String(10))
    type = Column(Enum(TitleType), nullable=False)
    name = Column(String(255))
    name_original = Column(String(255))
    tagline = Column(String(255))
    tmdb_vote_average = Column(DECIMAL(3,1))
    tmdb_vote_count = Column(Integer)
    imdb_vote_average = Column(DECIMAL(3,1))
    imdb_vote_count = Column(Integer)
    age_rating = Column(String(10))
    overview = Column(Text)
    movie_runtime = Column(Integer)
    movie_revenue = Column(BigInteger)
    movie_budget = Column(BigInteger)
    release_date = Column(Date)
    original_language = Column(String(64))
    origin_country = Column(String(64))
    awards = Column(String(255))
    homepage = Column(Text)
    last_updated = Column(
        TIMESTAMP,
        server_default=func.now(),
        server_onupdate=func.now()
    )

    seasons = relationship("Season", back_populates="title", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="title", cascade="all, delete-orphan")
    genres = relationship("TitleGenre", back_populates="title", cascade="all, delete-orphan")


class Season(Base):
    __tablename__ = "seasons"

    season_id = Column(Integer, primary_key=True, autoincrement=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    season_name = Column(String(255))
    tmdb_vote_average = Column(DECIMAL(3,1))
    overview = Column(Text)
    last_updated = Column(
        TIMESTAMP,
        server_default=func.now(),
        server_onupdate=func.now()
    )

    title = relationship("Title", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    episode_id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    episode_name = Column(String(255))
    tmdb_vote_average = Column(DECIMAL(3,1))
    tmdb_vote_count = Column(Integer)
    overview = Column(Text)
    air_date = Column(Date)
    runtime = Column(Integer)
    last_updated = Column(
        TIMESTAMP,
        server_default=func.now(),
        server_onupdate=func.now()
    )

    season = relationship("Season", back_populates="episodes")
    title = relationship("Title")


class UserTitleDetails(Base):
    __tablename__ = "user_title_details"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    in_watchlist = Column(Boolean, default=True)
    favourite = Column(Boolean, default=False)
    watch_next = Column(Boolean, default=False)
    watch_count = Column(Integer, default=0)
    notes = Column(Text)
    chosen_poster_image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"))
    chosen_backdrop_image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"))
    chosen_logo_image_id = Column(Integer, ForeignKey("images.image_id", ondelete="CASCADE"))
    added_at = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")
    last_watched_at = Column(TIMESTAMP)
    last_viewed_at = Column(TIMESTAMP)


class UserSeasonDetails(Base):
    __tablename__ = "user_season_details"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), primary_key=True)
    poster_image_id = Column(Integer)
    notes = Column(Text)


class UserEpisodeDetails(Base):
    __tablename__ = "user_episode_details"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), primary_key=True)
    watch_count = Column(Integer, default=0)
    notes = Column(Text)
    last_updated = Column(TIMESTAMP, default="CURRENT_TIMESTAMP", server_onupdate="CURRENT_TIMESTAMP")


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_genre_id = Column(Integer)
    genre_name = Column(String(255), nullable=False)
    last_updated = Column(TIMESTAMP, default="CURRENT_TIMESTAMP", server_onupdate="CURRENT_TIMESTAMP")

    titles = relationship("TitleGenre", back_populates="genre", cascade="all, delete-orphan")


class TitleGenre(Base):
    __tablename__ = "title_genres"

    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.genre_id", ondelete="CASCADE"), primary_key=True)

    title = relationship("Title", back_populates="genres")
    genre = relationship("Genre", back_populates="titles")


class Image(Base):
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(255), unique=True, nullable=False)
    type = Column(Enum(ImageType), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    iso_3166_1 = Column(String(5))
    iso_639_1 = Column(String(5))
    vote_average = Column(DECIMAL(5,3))
    vote_count = Column(Integer)

    title = relationship("Title", back_populates="images")

import enum
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Date, Text, Boolean, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Enums

class TitleType(enum.Enum):
    movie = "movie"
    tv = "tv"

class ImageType(enum.Enum):
    poster = "poster"
    backdrop = "backdrop"
    logo = "logo"

class SortDirection(enum.Enum):
    default = "default"
    asc = "asc"
    desc = "desc"

class SortBy(enum.Enum):
    default = "default"
    tmdb_score = "tmdb_score"
    imdb_score = "imdb_score"
    popularity = "popularity"
    title_name = "title_name"
    runtime = "runtime"
    release_date = "release_date"
    last_viewed_at = "last_viewed_at"
    random = "random"


##### USER AND AUTH #####

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    token_hash = Column(String, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value_type = Column(String(20), nullable=False)
    default_value = Column(Text, nullable=False)


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    key = Column(
        String(100),
        ForeignKey("settings.key", ondelete="CASCADE"),
        primary_key=True
    )
    value = Column(Text, nullable=False)


##### TITLE DETAILS #####

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
    release_date = Column(Date)
    movie_runtime = Column(Integer)
    movie_revenue = Column(BigInteger)
    movie_budget = Column(BigInteger)
    original_language = Column(String(64))
    origin_country = Column(String(64))
    awards = Column(String(255))
    homepage = Column(Text)
    default_poster_image_path = Column(String(255), ForeignKey("images.file_path"))
    default_backdrop_image_path = Column(String(255), ForeignKey("images.file_path"))
    default_logo_image_path = Column(String(255), ForeignKey("images.file_path"))
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    seasons = relationship("Season", back_populates="title", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="title", cascade="all, delete-orphan", foreign_keys="Image.title_id")
    genres = relationship("TitleGenre", back_populates="title", cascade="all, delete-orphan")

    default_poster = relationship("Image", foreign_keys=[default_poster_image_path], viewonly=True)
    default_backdrop = relationship("Image", foreign_keys=[default_backdrop_image_path], viewonly=True)
    default_logo = relationship("Image", foreign_keys=[default_logo_image_path], viewonly=True) 

class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint("title_id", "season_number", name="uq_season_title_number"),
    )

    season_id = Column(Integer, primary_key=True, autoincrement=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    season_name = Column(String(255))
    tmdb_vote_average = Column(DECIMAL(3,1))
    overview = Column(Text)
    default_poster_image_path = Column(String(255), ForeignKey("images.file_path"))
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    title = relationship("Title", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")
    images = relationship("Image", foreign_keys="Image.season_id", cascade="all, delete-orphan")
    default_poster = relationship("Image", foreign_keys=[default_poster_image_path], viewonly=True)


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint("season_id", "episode_number", name="uq_episode_season_number"),
    )

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
    default_backdrop_image_path = Column(String(255), ForeignKey("images.file_path"))
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    season = relationship("Season", back_populates="episodes")
    title = relationship("Title")
    images = relationship("Image", foreign_keys="Image.episode_id", cascade="all, delete-orphan")
    default_backdrop = relationship("Image", foreign_keys=[default_backdrop_image_path], viewonly=True)


##### USER TITLE DETAILS #####

class UserTitleDetails(Base):
    __tablename__ = "user_title_details"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    in_library = Column(Boolean, default=True)
    is_favourite = Column(Boolean, default=False)
    in_watchlist = Column(Boolean, default=False)
    watch_count = Column(Integer, default=0)
    notes = Column(Text)
    chosen_poster_image_path = Column(String(255), ForeignKey("images.file_path"))
    chosen_backdrop_image_path = Column(String(255), ForeignKey("images.file_path"))
    chosen_logo_image_path = Column(String(255), ForeignKey("images.file_path"))

    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_watched_at = Column(DateTime(timezone=True))
    last_viewed_at = Column(DateTime(timezone=True))


class UserSeasonDetails(Base):
    __tablename__ = "user_season_details"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), primary_key=True)
    chosen_poster_image_path = Column(String(255), ForeignKey("images.file_path"))
    notes = Column(Text)


class UserEpisodeDetails(Base):
    __tablename__ = "user_episode_details"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), primary_key=True)
    watch_count = Column(Integer, default=0)
    notes = Column(Text)
    chosen_backdrop_image_path = Column(String(255), ForeignKey("images.file_path"))
    last_watched_at = Column(DateTime(timezone=True))


##### GENERES #####

class Genre(Base):
    __tablename__ = "genres"

    tmdb_genre_id = Column(Integer, primary_key=True)
    genre_name = Column(String(255), nullable=False)
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    titles = relationship("TitleGenre", back_populates="genre", cascade="all, delete-orphan")


class TitleGenre(Base):
    __tablename__ = "title_genres"

    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.tmdb_genre_id", ondelete="CASCADE"), primary_key=True)

    title = relationship("Title", back_populates="genres")
    genre = relationship("Genre", back_populates="titles")


##### MEDIA #####

class Image(Base):
    __tablename__ = "images"

    file_path = Column(String(255), primary_key=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), nullable=True)
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), nullable=True)

    type = Column(Enum(ImageType), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    iso_3166_1 = Column(String(5))
    iso_639_1 = Column(String(5))
    vote_average = Column(DECIMAL(5,3))
    vote_count = Column(Integer)

    title = relationship("Title", back_populates="images", foreign_keys=[title_id])
    season = relationship("Season", foreign_keys=[season_id])
    episode = relationship("Episode", foreign_keys=[episode_id])

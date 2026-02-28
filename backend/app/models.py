import enum
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Date, Text, Boolean, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.ext.associationproxy import association_proxy
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

class Themes(enum.Enum):
    void = "void"
    midnight = "midnight"
    amethyst = "amethyst"
    sixteen_bit = "16-bit"
    flashbang = "flashbang"


##### USER AND AUTH #####

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    collections = relationship("UserCollection", back_populates="user", cascade="all, delete-orphan")


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

    key = Column(String(128), primary_key=True)
    value_type = Column(String(128), nullable=False)
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
    jellyfin_id = Column(String(32))
    title_type = Column(Enum(TitleType), nullable=False)
    name_original = Column(String(255))
    tmdb_vote_average = Column(DECIMAL(3,1))
    tmdb_vote_count = Column(Integer)
    imdb_vote_average = Column(DECIMAL(3,1))
    imdb_vote_count = Column(Integer)
    release_date = Column(Date)
    movie_runtime = Column(Integer)
    movie_revenue = Column(BigInteger)
    movie_budget = Column(BigInteger)
    original_language = Column(String(64))
    origin_country = Column(String(64))
    awards = Column(String(255))
    homepage = Column(Text)
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    translations = relationship("TitleTranslation", back_populates="title", lazy="noload")
    user_details = relationship("UserTitleDetails", back_populates="title", lazy="noload")
    seasons = relationship("Season", back_populates="title", cascade="all, delete-orphan")
    genres = relationship("TitleGenre", back_populates="title", cascade="all, delete-orphan")
    age_ratings = relationship("TitleAgeRatings", cascade="all, delete-orphan")
    
    image_links = relationship("ImageLink", back_populates="title", cascade="all, delete-orphan")
    images = association_proxy("image_links", "image")


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint("title_id", "season_number", name="uq_season_title_number"),
    )

    season_id = Column(Integer, primary_key=True, autoincrement=True)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    tmdb_vote_average = Column(DECIMAL(3,1))
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    translations = relationship("SeasonTranslation", back_populates="season", lazy="noload")
    user_details = relationship("UserSeasonDetails", back_populates="season", lazy="noload")
    title = relationship("Title", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")

    image_links = relationship("ImageLink", back_populates="season", cascade="all, delete-orphan")
    images = association_proxy("image_links", "image")


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint("season_id", "episode_number", name="uq_episode_season_number"),
    )

    episode_id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    tmdb_vote_average = Column(DECIMAL(3,1))
    tmdb_vote_count = Column(Integer)
    air_date = Column(Date)
    runtime = Column(Integer)
    default_backdrop_image_path = Column(String(64), ForeignKey("images.file_path"))
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )

    translations = relationship("EpisodeTranslation", back_populates="episode", lazy="noload")
    user_details = relationship("UserEpisodeDetails", back_populates="episode", lazy="noload")
    season = relationship("Season", back_populates="episodes")
    title = relationship("Title")

    image_links = relationship("ImageLink", back_populates="episode", cascade="all, delete-orphan")
    images = association_proxy("image_links", "image")
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
    chosen_locale = Column(String(16))

    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_watched_at = Column(DateTime(timezone=True))
    last_viewed_at = Column(DateTime(timezone=True))

    title = relationship("Title", back_populates="user_details")
    chosen_poster = relationship("Image", foreign_keys=[chosen_poster_image_path], viewonly=True)
    chosen_backdrop = relationship("Image", foreign_keys=[chosen_backdrop_image_path], viewonly=True)
    chosen_logo = relationship("Image", foreign_keys=[chosen_logo_image_path], viewonly=True)


class UserSeasonDetails(Base):
    __tablename__ = "user_season_details"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), primary_key=True)
    chosen_poster_image_path = Column(String(255), ForeignKey("images.file_path"))
    notes = Column(Text)

    season = relationship("Season", back_populates="user_details")
    chosen_poster = relationship("Image", foreign_keys=[chosen_poster_image_path], viewonly=True)


class UserEpisodeDetails(Base):
    __tablename__ = "user_episode_details"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), primary_key=True)
    watch_count = Column(Integer, default=0)
    notes = Column(Text)
    chosen_backdrop_image_path = Column(String(255), ForeignKey("images.file_path"))
    last_watched_at = Column(DateTime(timezone=True))

    episode = relationship("Episode", back_populates="user_details")
    chosen_backdrop = relationship("Image", foreign_keys=[chosen_backdrop_image_path], viewonly=True)


##### TITLE TRANSLATIONS #####

class TitleTranslation(Base):
    __tablename__ = "title_translations"
    
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    iso_639_1 = Column(String(4), primary_key=True)

    name = Column(String(255))
    overview = Column(Text)
    tagline = Column(String(255))

    default_poster_image_path = Column(String(64), ForeignKey("images.file_path"), nullable=True)
    default_backdrop_image_path = Column(String(64), ForeignKey("images.file_path"), nullable=True)
    default_logo_image_path = Column(String(64), ForeignKey("images.file_path"), nullable=True)

    title = relationship("Title", back_populates="translations")
    default_poster = relationship("Image", foreign_keys=[default_poster_image_path], viewonly=True)
    default_backdrop = relationship("Image", foreign_keys=[default_backdrop_image_path], viewonly=True)
    default_logo = relationship("Image", foreign_keys=[default_logo_image_path], viewonly=True)


class SeasonTranslation(Base):
    __tablename__ = "season_translations"
    
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), primary_key=True)
    iso_639_1 = Column(String(4), primary_key=True)
    
    name = Column(String(255))
    overview = Column(Text)

    default_poster_image_path = Column(String(64), ForeignKey("images.file_path"), nullable=True)

    season = relationship("Season", back_populates="translations")
    default_poster = relationship("Image", foreign_keys=[default_poster_image_path], viewonly=True)


class EpisodeTranslation(Base):
    __tablename__ = "episode_translations"
    
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), primary_key=True)
    iso_639_1 = Column(String(4), primary_key=True)
    
    name = Column(String(255))
    overview = Column(Text)

    episode = relationship("Episode", back_populates="translations")
    

##### GENERES AND OTHER MANY TO ONE DETAILS #####

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


class TitleAgeRatings(Base):
    __tablename__ = "title_age_ratings"

    title_id = Column(
        Integer,
        ForeignKey("titles.title_id", ondelete="CASCADE"),
        primary_key=True
    )
    iso_3166_1 = Column(
        String(8),
        primary_key=True
    )

    rating = Column(String(64))
    descriptors = Column(Text)

    title = relationship("Title")


##### COLLECTIONS #####

class UserCollection(Base):
    __tablename__ = "user_collections"

    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    name = Column(String(255))
    description = Column(Text)
    parent_collection_id = Column(Integer, ForeignKey("user_collections.collection_id", ondelete="SET NULL"))

    user = relationship("User", back_populates="collections")
    titles = relationship("UserCollectionTitle", back_populates="collection", cascade="all, delete-orphan")
    child_collections = relationship("UserCollection", backref="parent_collection", remote_side=[collection_id])


class UserCollectionTitle(Base):
    __tablename__ = "user_collection_titles"

    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), primary_key=True)
    collection_id = Column(Integer, ForeignKey("user_collections.collection_id", ondelete="CASCADE"), primary_key=True)

    title = relationship("Title")
    collection = relationship("UserCollection", back_populates="titles")


##### MEDIA #####

class Image(Base):
    __tablename__ = "images"

    file_path = Column(String(64), primary_key=True)
    type = Column(Enum(ImageType), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    iso_3166_1 = Column(String(5))
    iso_639_1 = Column(String(5))
    vote_average = Column(DECIMAL(5,3))
    vote_count = Column(Integer)

    links = relationship("ImageLink", back_populates="image", cascade="all, delete-orphan")


class ImageLink(Base):
    __tablename__ = "image_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    file_path = Column(String(64), ForeignKey("images.file_path", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.title_id", ondelete="CASCADE"), nullable=True)
    season_id = Column(Integer, ForeignKey("seasons.season_id", ondelete="CASCADE"), nullable=True)
    episode_id = Column(Integer, ForeignKey("episodes.episode_id", ondelete="CASCADE"), nullable=True)

    # Unique Constraint to prevent duplicate links
    __table_args__ = (
        UniqueConstraint(
            'file_path', 'title_id', 'season_id', 'episode_id', 
            name='uix_image_link_identity',
            postgresql_nulls_not_distinct=True
        ),
    )

    image = relationship("Image", back_populates="links")
    title = relationship("Title", back_populates="image_links")
    season = relationship("Season", back_populates="image_links")
    episode = relationship("Episode", back_populates="image_links")

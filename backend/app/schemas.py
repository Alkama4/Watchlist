from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
from app.models import TitleType, SortBy, SortDirection
from app.config import DEFAULT_MAX_QUERY_LIMIT, ABSOLUTE_MAX_QUERY_LIMIT

####### Users and authentication #######

class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    user_id: int
    username: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str

class UserDelete(BaseModel):
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class EnumChoice(BaseModel):
    value: str
    label: str

class SettingOut(BaseModel):
    key: str
    value_type: str
    default_value: str
    enum_choices: Optional[List[EnumChoice]] = None
    label: str

    class Config:
        from_attributes = True

class UserSettingOut(BaseModel):
    user_id: int
    key: str
    value: str

    class Config:
        from_attributes = True

class UserSettingIn(BaseModel):
    value: str

####### Titles #######

class GenreElement(BaseModel):
    tmdb_genre_id: int
    genre_name: str


class RatingElement(BaseModel):
    iso_3166_1: str
    rating: str
    descriptors: str


class TitleIn(BaseModel):
    tmdb_id: int
    title_type: TitleType


class TitleWatchCountIn(BaseModel):
    watch_count: int

class TitleIsFavouriteIn(BaseModel):
    is_favourite: bool

class TitleInWatchlistIn(BaseModel):
    in_watchlist: bool

class TitleNotesIn(BaseModel):
    notes: str


class TMDBTitleQueryIn(BaseModel):
    query: str
    page: Optional[int] = Field(1, ge=1)

class TitleQueryIn(BaseModel):
    query: Optional[str] = None
    title_type: Optional[TitleType] = None
    is_favourite: Optional[bool] = None
    in_watchlist: Optional[bool] = None
    watch_status: Optional[str] = Field(
        None,
        pattern="^(not_watched|partial|completed)$"
    )
    release_year_min: Optional[int] = None
    release_year_max: Optional[int] = None
    is_released: Optional[bool] = None
    genres_include: Optional[List[int]] = None
    genres_exclude: Optional[List[int]] = None
    min_tmdb_rating: Optional[int] = Field(None, ge=0, le=10)
    min_imdb_rating: Optional[int] = Field(None, ge=0, le=10)
    exclude_title_ids: Optional[list[int]] = None
    sort_by: Optional[SortBy] = SortBy.default
    sort_direction: Optional[SortDirection] = SortDirection.default
    page_number: Optional[int] = Field(1, ge=1)
    page_size: Optional[int] = Field(
        DEFAULT_MAX_QUERY_LIMIT, 
        ge=1, 
        le=ABSOLUTE_MAX_QUERY_LIMIT
    )

class CompactUserTitleDetailsOut(BaseModel):
    in_library: bool
    is_favourite: bool
    in_watchlist: bool
    watch_count: int

    chosen_poster_image_path: Optional[str] = None
    chosen_backdrop_image_path: Optional[str] = None
    chosen_logo_image_path: Optional[str] = None

class CompactTitleOut(BaseModel):
    title_id: Optional[int] = None
    tmdb_id: Optional[int] = None
    title_type: TitleType
    name: str
    genres: Optional[List[GenreElement]] = None
    release_date: Optional[date] = None
    overview: Optional[str] = None
    movie_runtime: Optional[int] = None
    show_season_count: Optional[int] = None
    show_episode_count: Optional[int] = None
    tmdb_vote_average: Optional[float] = None
    tmdb_vote_count: Optional[int] = None
    imdb_vote_average: Optional[float] = None
    imdb_vote_count: Optional[int] = None

    default_poster_image_path: Optional[str] = None
    default_backdrop_image_path: Optional[str] = None
    default_logo_image_path: Optional[str] = None

    user_details: Optional[CompactUserTitleDetailsOut] = None

class TitleListOut(BaseModel):
    header: Optional[str] = None
    titles: List[CompactTitleOut]
    page_number: int
    page_size: int
    total_items: int
    total_pages: int

class HomeOverviewOut(BaseModel):
    hero_cards: Optional[TitleListOut] = None  
    normal_cards: List[TitleListOut]


#### Title out stack ####

class UserEpisodeDetailsOut(BaseModel):
    watch_count: int
    notes: Optional[str] = None
    last_watched_at: datetime
    chosen_backdrop_image_path: Optional[str] = None

    class Config:
        from_attributes = True

class UserSeasonDetailsOut(BaseModel):
    notes: Optional[str]
    chosen_poster_image_path: Optional[str]

    class Config:
        from_attributes = True

class UserTitleDetailsOut(BaseModel):
    in_library: bool
    is_favourite: bool
    in_watchlist: bool
    watch_count: int
    notes: Optional[str]
    chosen_poster_image_path: Optional[str]
    chosen_backdrop_image_path: Optional[str]
    chosen_logo_image_path: Optional[str]

    added_at: Optional[datetime]
    last_watched_at: Optional[datetime]
    last_viewed_at: Optional[datetime]

    class Config:
        from_attributes = True

class EpisodeOut(BaseModel):
    episode_id: int
    episode_number: int
    episode_name: Optional[str]
    tmdb_vote_average: Optional[float]
    tmdb_vote_count: Optional[float]
    overview: Optional[str]
    air_date: Optional[date]
    runtime: Optional[int]
    default_backdrop_image_path: Optional[str]
    last_updated: datetime

    user_details: Optional[UserEpisodeDetailsOut] = None  

    class Config:
        from_attributes = True

class SeasonOut(BaseModel):
    season_id: int
    season_number: int
    season_name: Optional[str]
    tmdb_vote_average: Optional[float]
    overview: Optional[str]
    default_poster_image_path: Optional[str]
    last_updated: datetime

    episodes: List[EpisodeOut]
    user_details: Optional[UserSeasonDetailsOut] = None

    class Config:
        from_attributes = True

class TitleOut(BaseModel):
    title_id: int
    tmdb_id: int
    imdb_id: str
    title_type: TitleType
    name: str
    name_original: str
    tagline: str
    genres: list[GenreElement] = None
    tmdb_vote_average: Optional[float]
    tmdb_vote_count: Optional[int]
    imdb_vote_average: Optional[float]
    imdb_vote_count: Optional[int]
    age_ratings: Optional[RatingElement] = None
    overview: Optional[str]
    movie_runtime: Optional[int]
    movie_revenue: Optional[int]
    movie_budget: Optional[int]
    release_date: Optional[date]
    original_language: Optional[str]
    origin_country: Optional[str]
    awards: Optional[str]
    homepage: Optional[str]
    default_poster_image_path: Optional[str]
    default_backdrop_image_path: Optional[str]
    default_logo_image_path: Optional[str]
    last_updated: datetime

    seasons: List[SeasonOut] = Field(default_factory=list)
    user_details: Optional[UserTitleDetailsOut] = None

    class Config:
        from_attributes = True

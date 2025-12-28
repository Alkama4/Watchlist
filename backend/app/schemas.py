from typing import List, Optional
from pydantic import BaseModel
from app.models import TitleType
from datetime import datetime, date

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


####### Titles #######

class TitleIn(BaseModel):
    tmdb_id: int
    title_type: TitleType


#### Title out stack ####

class UserEpisodeDetailsOut(BaseModel):
    watch_count: int
    notes: Optional[str]
    last_watched_at: datetime

    class Config:
        from_attributes = True

class UserSeasonDetailsOut(BaseModel):
    notes: Optional[str]
    chosen_poster_image_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserTitleDetailsOut(BaseModel):
    in_watchlist: bool
    is_favourite: bool
    watch_next: bool
    watch_count: int
    notes: Optional[str]
    chosen_poster_image_id: Optional[int] = None
    chosen_backdrop_image_id: Optional[int] = None
    chosen_logo_image_id: Optional[int] = None

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
    last_updated: datetime

    episodes: List[EpisodeOut]
    user_details: Optional[UserSeasonDetailsOut] = None

    class Config:
        from_attributes = True

class TitleOut(BaseModel):
    title_id: int
    tmdb_id: int
    imdb_id: str
    type: TitleType
    name: str
    name_original: str
    tmdb_vote_average: Optional[float]
    tmdb_vote_count: Optional[int]
    imdb_vote_average: Optional[float]
    imdb_vote_count: Optional[int]
    age_rating: Optional[str]
    overview: Optional[str]
    movie_runtime: Optional[int]
    movie_revenue: Optional[int]
    movie_budget: Optional[int]
    release_date: Optional[date]
    original_language: Optional[str]
    origin_country: Optional[str]
    awards: Optional[str]
    homepage: Optional[str]
    last_updated: datetime

    seasons: List[SeasonOut] = []
    user_details: Optional[UserTitleDetailsOut] = None

    class Config:
        from_attributes = True

from enum import Enum

class TitleType(str, Enum):
    movie = "movie"
    tv = "tv"

class ImageType(str, Enum):
    poster = "poster"
    backdrop = "backdrop"
    logo = "logo"

class SortDirection(str, Enum):
    default = "default"
    asc = "asc"
    desc = "desc"

class SortBy(str, Enum):
    default = "default"
    tmdb_score = "tmdb_score"
    imdb_score = "imdb_score"
    popularity = "popularity"
    title_name = "title_name"
    runtime = "runtime"
    release_date = "release_date"
    last_viewed_at = "last_viewed_at"
    added_at = "added_at"
    similarity = "similarity"
    random = "random"

class Themes(str, Enum):
    void = "void"
    midnight = "midnight"
    amethyst = "amethyst"
    flashbang = "flashbang"
    sixteen_bit = "16-bit"

class VideoType(str, Enum):
    movie = "movie"
    episode = "episode"
    featurette = "featurette"

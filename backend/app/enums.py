import enum

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
    added_at = "added_at"
    similarity = "similarity"
    random = "random"

class Themes(enum.Enum):
    void = "void"
    midnight = "midnight"
    amethyst = "amethyst"
    flashbang = "flashbang"
    sixteen_bit = "16-bit"

class VideoType(enum.Enum):
    movie = "movie"
    episode = "episode"
    featurette = "featurette"

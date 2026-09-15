import { fastApi } from "./fastApi";
import { resolveSeasonWatchCount } from "./titleUtils";

export async function toggleFavourite(title, waitingObject) {
    waitingObject.toggleFavourite = true;
    try {
        let response;
        if (title.user_details.is_favourite) {
            response = await fastApi.titles.setFavourite(title.title_id, false);
        } else {
            response = await fastApi.titles.setFavourite(title.title_id, true);
        }
        if (!response) return;
    
        title.user_details.is_favourite = response.is_favourite;
    } finally {
        waitingObject.toggleFavourite = false;
    }
}

export async function toggleWatchlist(title, waitingObject) {
    waitingObject.toggleWatchlist = true;
    try {
        let response;
        if (title.user_details.in_watchlist) {
            response = await fastApi.titles.setWatchlist(title.title_id, false);
        } else {
            response = await fastApi.titles.setWatchlist(title.title_id, true);
        }
        if (!response) return;
        
        title.user_details.in_watchlist = response.in_watchlist;
    } finally {
        waitingObject.toggleWatchlist = false;
    }
}


async function _updateWatchCount(item, title, wait, key, api, delta) {
    const id = item.title_id || item.season_id || item.episode_id;
    const loader = `${key}_${id}`;
    wait[loader] = true;

    try {
        const current = item.user_details?.watch_count || resolveSeasonWatchCount(item) || 0;
        const { watch_count: next } = await api(id, Math.max(0, current + delta));

        const today = new Date().toISOString().slice(0, 10);

        // Update the item itself (not relevant for seasons since their count is always derived)
        if (item.title_id || item.episode_id) {
            if (!item.user_details) item.user_details = {};
            item.user_details.watch_count = next;
        }

        // Update relevant episodes within a title or season.
        // Season 0 (when not updated directly) and unreleased episodes are ignored.
        if (item.title_id) {
            title.seasons?.forEach(s => {
                if (s.season_number > 0) {
                    s.episodes?.forEach(e => {
                        if (e.air_date && e.air_date <= today) {
                            e.user_details = {
                                ...e.user_details,
                                watch_count: next
                            };
                        }
                    });
                }
            });
        } else if (item.season_id) {
            item.episodes?.forEach(e => {
                if (e.air_date && e.air_date <= today) {
                    e.user_details = {
                        ...e.user_details,
                        watch_count: next
                    };
                }
            });
        }

        // Keep a TV-shows watch count up to date
        if (!item.title_id && title?.seasons) {
            const allEps = title.seasons.flatMap(s =>
                s.season_number > 0
                    ? (s.episodes ?? []).filter(e =>
                        e.air_date && e.air_date <= today
                    )
                    : []
            );

            const minWatch = allEps.length
                ? Math.min(...allEps.map(e => e.user_details?.watch_count ?? 0))
                : 0;

            title.user_details = {
                ...title.user_details,
                watch_count: minWatch
            };
        }
    } finally {
        wait[loader] = false;
    }
}

export const adjustWatchCount = {
    title: {
        add: (item, wait) => _updateWatchCount(item, item, wait, 'titleWcAdd', fastApi.titles.setWatchCount, 1),
        subtract: (item, wait) => _updateWatchCount(item, item, wait, 'titleWcSub', fastApi.titles.setWatchCount, -1),
    },
    season: {
        add: (item, wait, title) => _updateWatchCount(item, title, wait, 'seasonWcAdd', fastApi.seasons.setWatchCount, 1),
        subtract: (item, wait, title) => _updateWatchCount(item, title, wait, 'seasonWcSub', fastApi.seasons.setWatchCount, -1),
    },
    episode: {
        add: (item, wait, title) => _updateWatchCount(item, title, wait, 'episodeWcAdd', fastApi.episodes.setWatchCount, 1),
        subtract: (item, wait, title) => _updateWatchCount(item, title, wait, 'episodeWcSub', fastApi.episodes.setWatchCount, -1),
    }
};

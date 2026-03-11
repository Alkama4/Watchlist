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

        // Update the item itself
        if (!item.user_details) item.user_details = {};
        item.user_details.watch_count = next;

        // Cascade changes down (Title -> Seasons -> Episodes)
        if (item.title_id) {
            title.seasons?.forEach(s => s.episodes?.forEach(e => {
                e.user_details = { ...e.user_details, watch_count: next };
            }));
        } else if (item.season_id) {
            item.episodes?.forEach(e => {
                e.user_details = { ...e.user_details, watch_count: next };
            });
        }

        // Sync changes up (Episode/Season -> Title)
        if (!item.title_id && title?.seasons) {
            const allEps = title.seasons.flatMap(s => s.episodes ?? []);
            const minWatch = Math.min(...allEps.map(e => e.user_details?.watch_count ?? 0));
            title.user_details = { ...title.user_details, watch_count: minWatch };
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
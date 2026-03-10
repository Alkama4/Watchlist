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

async function _updateWatchCount({ item, waitingObject, loadingKey, apiCall, delta }) {
    const itemId = item.title_id || item.season_id || item.episode_id;
    waitingObject[`${loadingKey}_${itemId}`] = true;

    try {
        const currentCount = item?.user_details?.watch_count || resolveSeasonWatchCount(item) || 0;
        const newCount = Math.max(0, currentCount + delta);
        const response = await apiCall(itemId, newCount);

        if (item?.season_id) {
            item.episodes.forEach(ep => {
                if (!ep.user_details) ep.user_details = {};
                ep.user_details.watch_count = response.watch_count;
            });
        } else {
            item.user_details.watch_count = response.watch_count;
        }
    } finally {
        waitingObject[`${loadingKey}_${itemId}`] = false;
    }
}

export const adjustWatchCount = {
    title: {
        add: (title, wait) => _updateWatchCount({
            item: title, 
            waitingObject: wait, 
            loadingKey: 'titleWcAdd', 
            apiCall: fastApi.titles.setWatchCount, 
            delta: 1 
        }),
        subtract: (title, wait) => _updateWatchCount({
            item: title, 
            waitingObject: wait, 
            loadingKey: 'titleWcSub', 
            apiCall: fastApi.titles.setWatchCount, 
            delta: -1 
        }),
    },
    season: {
        add: (season, wait) => _updateWatchCount({
            item: season, 
            waitingObject: wait, 
            loadingKey: 'seasonWcAdd', 
            apiCall: fastApi.seasons.setWatchCount, 
            delta: 1
        }),
        subtract: (season, wait) => _updateWatchCount({
            item: season, 
            waitingObject: wait, 
            loadingKey: 'seasonWcSub', 
            apiCall: fastApi.seasons.setWatchCount, 
            delta: -1
        }),
    },
    episode: {
        add: (episode, wait) => _updateWatchCount({
            item: episode, 
            waitingObject: wait, 
            loadingKey: 'episodeWcAdd', 
            apiCall: fastApi.episodes.setWatchCount, 
            delta: 1 
        }),
        subtract: (episode, wait) => _updateWatchCount({
            item: episode, 
            waitingObject: wait, 
            loadingKey: 'episodeWcSub', 
            apiCall: fastApi.episodes.setWatchCount, 
            delta: -1 
        }),
    }
};

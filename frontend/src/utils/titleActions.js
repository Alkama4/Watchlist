import { fastApi } from "./fastApi";

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

export async function addToWatchCount(title, waitingObject) {
    waitingObject.addToWatchCount = true;
    try {
        const response = await fastApi.titles.setWatchCount(title.title_id, title.user_details.watch_count + 1);
        title.user_details.watch_count = response.watch_count;
    } finally {
        waitingObject.addToWatchCount = false;
    }
}

export async function subtractFromWatchCount(title, waitingObject) {
    waitingObject.subtractFromWatchCount = true;
    try {
        // Prevent going below 0
        const newCount = Math.max(0, title.user_details.watch_count - 1);
        const response = await fastApi.titles.setWatchCount(title.title_id, newCount);
        title.user_details.watch_count = response.watch_count;
    } finally {
        waitingObject.subtractFromWatchCount = false;
    }
}
import { useSettingsStore } from "@/stores/settings";
import { API_BASE_URL } from "./conf";

export function resolveAgeRating(ratings) {
    const settings = useSettingsStore();

    for (const countryCode of settings.preferredCountries) {
        const found = ratings.find(r => r.iso_3166_1 === countryCode)
        if (found?.rating) return found
    }

    return ratings.find(r => r.iso_3166_1 === settings.defaultCountry) ?? null
}

export function resolveSeasonWatchCount(season) {
    const episodes = season?.episodes || [];
    if (episodes.length === 0) return 0;
    const counts = episodes.map(ep => ep.user_details?.watch_count ?? 0);
    return Math.min(...counts);
}

export function buildVideoAssetUrl(video, titleDetails, type = "base", season = null, episode = null) {
    const titleName = titleDetails?.name;
    let label = null;

    // Episode case
    if (episode?.episode_number !== undefined) {
        const sNum = season.season_number;
        const eNum = episode.episode_number;
        label = `${titleName} - S${sNum}E${eNum}`;
    }
    // Movie case
    else if (video?.video_type === "movie") {
        label = titleName;
    }
    // Featurette / other
    else if (video?.file_name) {
        const featuretteName = video.file_name.split(".")[0];
        label = `${titleName} - ${featuretteName}`;
    }

    const path = `/media/video/${video?.video_asset_id}`;
    const fullPath = label ? `${path}/${label}` : path;
    const baseUrl = encodeURI(`${API_BASE_URL}${fullPath}`);

    if (type === "base") {
        return baseUrl;
    }

    const safeEncoded = btoa(baseUrl)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/g, "");

    if (type === "mpv-handler" || type === "mpv-handler-debug") {
        return `${type}://play/${safeEncoded}`;
    }

    return baseUrl;
}

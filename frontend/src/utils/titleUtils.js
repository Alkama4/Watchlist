import { useSettingsStore } from "@/stores/settings";

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

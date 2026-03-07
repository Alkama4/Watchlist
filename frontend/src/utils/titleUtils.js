import { useSettingsStore } from "@/stores/settings";

export function resolveAgeRating(ratings) {
    const settings = useSettingsStore();

    for (const countryCode of settings.preferredCountries) {
        const found = ratings.find(r => r.iso_3166_1 === countryCode)
        if (found?.rating) return found
    }

    return ratings.find(r => r.iso_3166_1 === settings.defaultCountry) ?? null
}

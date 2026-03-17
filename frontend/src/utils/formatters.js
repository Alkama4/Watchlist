import { useSettingsStore } from "@/stores/settings";

const settings = useSettingsStore();

export const timeFormatters = {
    minutesToHrAndMin: (minutes) => {
        if (minutes == null || minutes === 0) return ' - min'; // handles null, undefined, 0

        const hrs = Math.floor(minutes / 60);
        const mins = minutes % 60;

        if (hrs === 0) return `${mins}min`;
        return `${hrs}h ${mins}min`;
    },
    timestampToYear: (timestamp) => {
        return timestamp ? new Date(timestamp).getFullYear() : '-';
    },
    timestampToFullDate: (timestamp) => {
        return timestamp ? new Date(timestamp).toLocaleDateString(settings.primaryLocale, ) : '-'
    }
};

export const numberFormatters = {
    formatCompactNumber: (number) => {
        return new Intl.NumberFormat(settings.primaryLocale, {
            notation: 'compact',
            maximumFractionDigits: 1
        }).format(number);
    },
    formatNumberToLocale: (number, options) => {
        if (!number) return null;
        return number.toLocaleString(settings.primaryLocale, options);
    }
}

export const isoFormatters = {
    iso_3166_1ToCountry: (iso_3166_1) => {
        if (!iso_3166_1) return null;
        return new Intl.DisplayNames(settings.primaryLocale, { type: 'region' }).of(iso_3166_1);
    },
    localeToText: (locale) => {
        if (!locale) return 'No language';
        
        try {
            const displayNames = new Intl.DisplayNames(['en'], { type: 'language' });
            return displayNames.of(locale);
        } catch (e) {
            return locale;
        }
    }
}

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
    msToHrAndMin: (ms) => {
        return timeFormatters.minutesToHrAndMin(Math.floor(ms / 1000 / 60));
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


export const videoAssetFormatters = {
    formatSize: (bytes) => {
        if (!bytes) return '';
        const gb = bytes / (1024 ** 3);
        return gb >= 1 ? `${gb.toFixed(2)} GB` : `${(bytes / (1024 ** 2)).toFixed(1)} MB`;
    },
    formatBitrate: (bytes, ms) => {
        if (!bytes || !ms) return '';
        const mbps = (bytes * 8) / (ms * 1000);
        return `${mbps.toFixed(1)} Mbps`;
    },
    formatResolution: (resString) => {
        if (!resString || !resString.includes('x')) return resString;
        const [width, height] = resString.split('x').map(Number);
        const heightFromWidth = Math.round(width * (9 / 16));
        const effectiveHeight = Math.max(height, heightFromWidth);
        return `${effectiveHeight}p`;
    },
    
}
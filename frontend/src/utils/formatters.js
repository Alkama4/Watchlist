export const timeFormatters = {
    minutesToHrAndMin: (minutes) => {
        const hrs = Math.floor(minutes / 60);
        const mins = minutes % 60;

        if (hrs === 0) {
            return `${mins}min`;
        }

        return `${hrs}hr ${mins}min`;
    },
    timestampToYear: (timestamp) => {
        return timestamp ? new Date(timestamp).getFullYear() : '-';
    }
};

export const numberFormatters = {
    formatCompactNumber: (number) => {
        return new Intl.NumberFormat('en', {
            notation: 'compact',
            maximumFractionDigits: 1
        }).format(number);
    }
}

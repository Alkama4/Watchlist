import { API_BASE_URL } from './conf';

export function getDeviceHandler() {
    // Check modern User-Agent Client Hints (Chrome, Edge, etc.)
    if (navigator.userAgentData?.platform) {
        return navigator.userAgentData.platform === "Android" ? 'mpv-kt' : 'mpv-handler';
    }
    
    // Fallback to the standard userAgent string (Firefox, Safari, older browsers)
    const ua = navigator.userAgent;
    if (/android/i.test(ua)) {
        return 'mpv-kt';
    }

    return 'mpv-handler';
}

export function buildVideoAssetUrl(video, titleDetails, type = "base", season = null, episode = null) {
    const titleName = titleDetails?.name;
    let label = null;

    if (!titleName) {
        // Fallback to file name
        label = video.file_name.split(".")[0];
    } else if (episode?.episode_number !== undefined) {
        // Episodes
        const sNum = season?.season_number;
        const eNum = episode?.episode_number;
        label = `${titleName} - S${sNum}E${eNum}`;
    } else if (video?.video_type === "movie") {
        // Movies
        label = titleName;
    } else if (video?.file_name) {
        // Featurettes
        const featuretteName = video.file_name.split(".")[0];
        label = `${titleName} - ${featuretteName}`;
    }

    // 2. Build the Raw API URL
    const path = `/media/video/${video?.video_asset_id}`;
    const fullPath = label ? `${path}/${label}` : path;
    const baseUrl = encodeURI(`${API_BASE_URL}${fullPath}`);

    if (type === "base") {
        return baseUrl;
    }

    if (type === "mpv-kt") {
        const intentParts = [
            `intent:${baseUrl}#Intent`,
            `action=android.intent.action.VIEW`,
            `package=live.mehiz.mpvkt`,
            `S.title=${encodeURIComponent(label || 'Video')}`,
            `type=video/*`,
            `end`
        ];
        return intentParts.join(';');
    }

    if (type === "mpv-handler" || type === "mpv-handler-debug") {
        const safeEncoded = btoa(baseUrl)
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/g, "");
        return `${type}://play/${safeEncoded}`;
    }

    return baseUrl;
}

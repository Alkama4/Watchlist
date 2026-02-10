import { API_BASE_URL } from "./conf"

const BASE_IMAGE_URL = "/media/image"
const IMAGE_TYPE_MAP = {
    poster: { default: 'default_poster_image_path', user: 'chosen_poster_image_path' },
    backdrop: { default: 'default_backdrop_image_path', user: 'chosen_backdrop_image_path' },
    logo: { default: 'default_logo_image_path', user: 'chosen_logo_image_path' }
};

export function getTitleImageUrl(titleDetails, size, type, storeImageFlag = true) {
    const keys = IMAGE_TYPE_MAP[type];
    if (!keys) return null;

    const defaultPath = titleDetails?.[keys.default];
    const userPath = titleDetails?.user_details?.[keys.user];

    return buildImageUrl(userPath ?? defaultPath, size, storeImageFlag);
}

export function buildImageUrl(filePath, size, storeImageFlag = true) {
    if (!filePath) return null;
    const query = storeImageFlag ? '' : '?store=false';
    return `${API_BASE_URL}${BASE_IMAGE_URL}/${size}${filePath}${query}`;
}
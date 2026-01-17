import { API_BASE_URL } from "./conf"

const BASE_IMAGE_URL = "/media/image"

export function resolveImagePath(titleDetails, size, type) {
    let defaultPath;
    let userPath;

    switch (type) {
        case 'poster':
            defaultPath = titleDetails?.default_poster_image_path;
            userPath = titleDetails?.user_details?.chosen_poster_image_path;
            break;
        case 'backdrop':
            defaultPath = titleDetails?.default_backdrop_image_path;
            userPath = titleDetails?.user_details?.chosen_backdrop_image_path;
            break;
        case 'logo':
            defaultPath = titleDetails?.default_logo_image_path;
            userPath = titleDetails?.user_details?.chosen_logo_image_path;
            break;
        default:
            return null; // Or handle the unknown type in a different way
    }

    if (!defaultPath && !userPath) return null;
    return `${API_BASE_URL}${BASE_IMAGE_URL}/${size}${userPath ?? defaultPath}`;
}

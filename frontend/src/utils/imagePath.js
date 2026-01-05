import { API_BASE_URL } from "./conf"

const BASE_IMAGE_URL = "/media/image"

export function resolveImagePath(size, defaultPath, userPath) {
    if (!defaultPath && !userPath) return null;
    return `${API_BASE_URL}${BASE_IMAGE_URL}/${size}${userPath ?? defaultPath}`
}
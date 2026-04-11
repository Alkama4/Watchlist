import { ref, onMounted, onUnmounted } from 'vue'

export function useMediaQuery(query) {
    const matches = ref(false)
    let mediaQueryList = null

    const update = (e) => (matches.value = e.matches)

    onMounted(() => {
        mediaQueryList = window.matchMedia(query)
        matches.value = mediaQueryList.matches
        mediaQueryList.addEventListener('change', update)
    })

    onUnmounted(() => {
        mediaQueryList?.removeEventListener('change', update)
    })

    return matches
}

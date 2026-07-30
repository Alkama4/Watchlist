import { ref } from 'vue'

function createMediaQuery(query) {
  const matches = ref(false)

  if (typeof window !== 'undefined') {
    const mediaQueryList = window.matchMedia(query)
    matches.value = mediaQueryList.matches

    // Sync state whenever screen resizes past breakpoint
    mediaQueryList.addEventListener('change', (e) => {
      matches.value = e.matches
    })
  }

  return matches
}

export const isMobile = createMediaQuery('(max-width: 768px)')

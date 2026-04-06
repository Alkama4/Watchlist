<script setup>
import { Link } from '@boxicons/vue';
import { useSettingsStore } from '@/stores/settings';
import Tmdb from '@/assets/icons/tmdb.svg';
import Imdb from '@/assets/icons/imdb.svg';
import JustWatch from '@/assets/icons/justWatch.svg';
import Jellyfin from '@/assets/icons/jellyfin.svg';
import { computed } from 'vue';

const props = defineProps({
    tmdbBaseUrl: {
        type: String,
        required: true
    },
    titleDetails: {
        type: Object,
        required: true
    },
    jellyfinConfig: {
        type: Object,
        required: true
    }
})

const settings = useSettingsStore();

const jellyfinLink = computed(() => {
    const baseUrl = props?.jellyfinConfig?.base_url
    const serverId = props?.jellyfinConfig?.server_id
    const jellyfinId = props?.titleDetails?.jellyfin_id

    const serverIdParam = serverId ? `&serverId=${serverId}` : ''

    return `${baseUrl}/web/#/details?id=${jellyfinId}${serverIdParam}`
})
</script>

<template>
    <div class="external-resources">
        <h4>External Resources</h4>
        <div class="links-wrapper">
            <a
                :href="tmdbBaseUrl"
                target="_blank"
                class="btn btn-even-padding btn-text"
                title="View on TMDB"
            >
                <Tmdb class="four-letter"/>
            </a>
            <a
                v-if="titleDetails?.imdb_id"
                :href="`https://www.imdb.com/title/${titleDetails?.imdb_id}`"
                target="_blank"
                class="btn btn-even-padding btn-text"
                title="View on IMDB"
            >
                <Imdb class="four-letter"/>
            </a>
            <a
                v-if="titleDetails?.homepage"
                :href="titleDetails?.homepage"
                target="_blank"
                class="btn btn-even-padding btn-text"
                title="Visit Official Website"
            >
                <Link/>
            </a>
            
            <hr>
            
            <div class="flex-row">
                <a
                    :href="`https://www.justwatch.com/${settings.primaryCountry}/search?q=${titleDetails?.name_original}`"
                    target="_blank"
                    class="btn btn-even-padding btn-text"
                    title="Check Availability on JustWatch"
                >
                    <JustWatch/>
                </a>
                <a  
                    v-if="titleDetails?.jellyfin_id && jellyfinConfig?.base_url"
                    :href="jellyfinLink"
                    target="_blank"
                    class="btn btn-even-padding btn-text"
                    title="Open in Jellyfin"
                >
                    <Jellyfin/>
                </a>
            </div>
        </div>
    </div>
</template>

<style scoped>
.links-wrapper {
    display: flex;
    flex-wrap: wrap;
    
    .btn {
        display: flex;
        align-items: center;
        text-decoration: none;

        svg {
            width: 27.65px;
            height: auto;
        }
        svg.four-letter {
            width: 42px;
            height: auto;
        }
    }
}
</style>

using Newtonsoft.Json.Linq;

namespace Watchlist.Services
{
    public class WebViewMessageHandler
    {
        public bool TryGetVideoUrl(string json, out string? videoUrl)
        {
            videoUrl = null;

            var obj = JObject.Parse(json);

            if (obj["action"]?.ToString() == "playVideo")
            {
                videoUrl = obj["url"]?.ToString();
                return !string.IsNullOrEmpty(videoUrl);
            }

            return false;
        }
    }
}

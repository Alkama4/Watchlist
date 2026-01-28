using LibVLCSharp.Shared;

namespace Watchlist.Services
{
    public class VlcPlayerService : IDisposable
    {
        private readonly LibVLC _libVLC;
        public MediaPlayer MediaPlayer { get; }

        public VlcPlayerService()
        {
            Core.Initialize();
            _libVLC = new LibVLC();
            MediaPlayer = new MediaPlayer(_libVLC);
        }

        public void Play(string url)
        {
            MediaPlayer.Stop();
            MediaPlayer.Play(new Media(_libVLC, url, FromType.FromLocation));
        }

        public void Pause() => MediaPlayer.Pause();

        public void Stop() => MediaPlayer.Stop();

        public void Dispose()
        {
            MediaPlayer.Dispose();
            _libVLC.Dispose();
        }
    }
}

using System.Windows.Input;
using Watchlist.Services;

namespace Watchlist.Input
{
    public class PlayerKeyController
    {
        private readonly VlcPlayerService _player;

        public PlayerKeyController(VlcPlayerService player)
        {
            _player = player;
        }

        public void Handle(Key key)
        {
            switch (key)
            {
                case Key.Space:
                    _player.Pause();
                    break;

                case Key.Right:
                    _player.MediaPlayer.Time += 10_000;
                    break;

                case Key.Left:
                    _player.MediaPlayer.Time -= 10_000;
                    break;

                case Key.Up:
                    _player.MediaPlayer.Volume =
                        Math.Min(_player.MediaPlayer.Volume + 5, 100);
                    break;

                case Key.Down:
                    _player.MediaPlayer.Volume =
                        Math.Max(_player.MediaPlayer.Volume - 5, 0);
                    break;
            }
        }
    }
}

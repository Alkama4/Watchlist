using System.Windows;
using System.Windows.Input;

namespace Watchlist.Services
{
    public class FullscreenController
    {
        private bool _isFullscreen;
        private WindowState _prevState;
        private WindowStyle _prevStyle;

        public bool IsFullscreen => _isFullscreen;

        public void HandleKey(Window window, Key key)
        {
            if (key == Key.F11)
            {
                Toggle(window);
                return;
            }

            if (key == Key.Escape && _isFullscreen)
            {
                Exit(window);
            }
        }

        public void Exit(Window window)
        {
            if (!_isFullscreen)
                return;

            window.WindowStyle = _prevStyle;
            window.WindowState = _prevState;
            _isFullscreen = false;
        }

        private void Toggle(Window window)
        {
            if (!_isFullscreen)
            {
                _prevState = window.WindowState;
                _prevStyle = window.WindowStyle;

                window.WindowStyle = WindowStyle.None;
                window.WindowState = WindowState.Maximized;
                _isFullscreen = true;
            }
            else
            {
                Exit(window);
            }
        }
    }
}

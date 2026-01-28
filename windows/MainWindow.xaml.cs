using System;
using System.Windows;
using System.Windows.Input;
using Watchlist.Input;
using Watchlist.Services;

namespace Watchlist
{
    public partial class MainWindow : Window
    {
        private readonly VlcPlayerService _player;
        private readonly PlayerKeyController _playerKeys;
        private readonly WebViewMessageHandler _webHandler;
        private readonly FullscreenController _fullscreen;

        public MainWindow()
        {
            InitializeComponent();

            _player = new VlcPlayerService();
            _playerKeys = new PlayerKeyController(_player);
            _webHandler = new WebViewMessageHandler();
            _fullscreen = new FullscreenController();

            videoView.MediaPlayer = _player.MediaPlayer;

            webView2.EnsureCoreWebView2Async().ContinueWith(_ =>
            {
                webView2.CoreWebView2.WebMessageReceived += WebMessageReceived;
            }, System.Threading.Tasks.TaskScheduler.FromCurrentSynchronizationContext());
        }

        private void WebMessageReceived(
            object? sender,
            Microsoft.Web.WebView2.Core.CoreWebView2WebMessageReceivedEventArgs e)
        {
            if (_webHandler.TryGetVideoUrl(e.WebMessageAsJson, out var url))
            {
                videoView.Visibility = Visibility.Visible;
                webView2.Visibility = Visibility.Collapsed;
                videoView.Focus();
                _player.Play(url!);
            }
        }

        protected override void OnKeyDown(KeyEventArgs e)
        {
            base.OnKeyDown(e);

            _fullscreen.HandleKey(this, e.Key);

            if (e.Key == Key.Escape && videoView.Visibility == Visibility.Visible)
            {
                ExitVlcMode();
                e.Handled = true;
                return;
            }

            if (videoView.Visibility == Visibility.Visible)
            {
                _playerKeys.Handle(e.Key);
                e.Handled = true;
            }
        }
        private void ExitVlcMode()
        {
            _player.Stop();
            videoView.Visibility = Visibility.Collapsed;
            webView2.Visibility = Visibility.Visible;
            webView2.Focus();
        }

        protected override void OnClosed(EventArgs e)
        {
            _player.Dispose();
            base.OnClosed(e);
        }
    }
}

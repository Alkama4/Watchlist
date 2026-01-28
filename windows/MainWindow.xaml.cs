using System;
using System.Windows;
using LibVLCSharp.Shared;
using LibVLCSharp.WPF;

namespace Watchlist
{
    public partial class MainWindow : Window
    {
        private LibVLC _libVLC;
        private MediaPlayer _mediaPlayer;

        public MainWindow()
        {
            InitializeComponent();

            // Initialize VLC
            Core.Initialize();
            _libVLC = new LibVLC();
            _mediaPlayer = new MediaPlayer(_libVLC);
            videoView.MediaPlayer = _mediaPlayer;

            // Start paused
            _mediaPlayer.Pause();

            // Initialize WebView2 Core
            webView2.EnsureCoreWebView2Async().ContinueWith(t =>
            {
                // Subscribe to messages after Core is ready
                webView2.CoreWebView2.WebMessageReceived += WebView2_WebMessageReceived;
            }, System.Threading.Tasks.TaskScheduler.FromCurrentSynchronizationContext());
        }

        private void WebView2_WebMessageReceived(object sender, Microsoft.Web.WebView2.Core.CoreWebView2WebMessageReceivedEventArgs e)
        {
            try
            {
                // Parse the message as JSON
                dynamic msg = Newtonsoft.Json.JsonConvert.DeserializeObject(e.WebMessageAsJson);

                if (msg.action == "playVideo" && msg.url != null)
                {
                    string videoUrl = msg.url;

                    // Play video
                    videoView.Visibility = Visibility.Visible;
                    webView2.Visibility = Visibility.Collapsed;

                    _mediaPlayer.Stop(); // stop previous video
                    _mediaPlayer.Play(new Media(_libVLC, videoUrl, FromType.FromLocation));
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error handling web message: " + ex.Message);
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            _mediaPlayer.Stop();
            _mediaPlayer.Dispose();
            _libVLC.Dispose();
            base.OnClosed(e);
        }


        private bool _isFullscreen = false;
        private WindowState _prevWindowState;
        private WindowStyle _prevWindowStyle;

        protected override void OnKeyDown(System.Windows.Input.KeyEventArgs e)
        {
            base.OnKeyDown(e);

            if (e.Key == System.Windows.Input.Key.F11)
            {
                ToggleFullscreen();
            }
        }

        private void ToggleFullscreen()
        {
            if (!_isFullscreen)
            {
                _prevWindowState = this.WindowState;
                _prevWindowStyle = this.WindowStyle;

                this.WindowStyle = WindowStyle.None;
                this.WindowState = WindowState.Maximized;

                _isFullscreen = true;
            }
            else
            {
                this.WindowStyle = _prevWindowStyle;
                this.WindowState = _prevWindowState;
                _isFullscreen = false;
            }
        }
    }
}

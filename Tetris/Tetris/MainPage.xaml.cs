using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;

namespace Tetris
{
    public partial class MainPage : UserControl
    {
        private TetrisController _controller;

        public MainPage()
        {
            InitializeComponent();

            _controller=new TetrisController();
            this.DataContext = _controller;
            foreach (var cell in _controller.CellContainer)
            {
                playBoard.Children.Add(cell);
            }
            foreach (var cell in _controller.NextBlockContainer)
            {
                canvasBoxPrev.Children.Add(cell);
            }
            _controller.GameOver+=new EventHandler(_controller_GameOver);
        }

        private void _controller_GameOver(object sender, EventArgs e)
        {
            gameOver.Visibility = Visibility.Visible;
            play.Text = "开始游戏";
        }

        private void start_Click(object sender, RoutedEventArgs e)
        {
            if (play.Text == "开始游戏")
            {
                gameOver.Visibility = Visibility.Collapsed;
                _controller.GameStart();
                play.Text = "暂停游戏";
            }
            else
            {
                _controller.GamePause();
                play.Text = "开始游戏";
            }
        }

        private void UserControl_KeyDown(object sender, KeyEventArgs e)
        {
            _controller.MoveBlock(e.Key);
        }

    }
}

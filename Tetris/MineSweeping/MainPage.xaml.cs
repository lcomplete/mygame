using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using MineSweeping.Model;

namespace MineSweeping
{
    public partial class MainPage : UserControl
    {
        private GameSetting _setting;
        private MineSweepingController _controller;

        public MainPage()
        {
            InitializeComponent();

            _setting=new GameSetting(16,10);
            _controller=new MineSweepingController(_setting);
            _controller.GameStart+=new EventHandler(_controller_GameStart);
            _controller.Play();
        }

        private void _controller_GameStart(object sender, EventArgs e)
        {
            foreach (var cell in _controller.CellMatrix)
            {
                LayoutRoot.Children.Add(cell);
            }
        }
    }
}

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
using Tetris.Model;

namespace Tetris
{
    public partial class Cell : UserControl
    {
        public Cell()
        {
            InitializeComponent();
        }

        public double Top
        {
            set { rectangle.SetValue(Canvas.TopProperty, value); }
        }

        public double Left
        {
            set { rectangle.SetValue(Canvas.LeftProperty, value); }
        }

        private CellColor _color=CellColor.Red;

        public CellColor? Color
        {
            get
            {
                if (rectangle.Visibility == Visibility.Visible)
                    return _color;
                return null;
            }
            set
            {
                if(value==null)
                    rectangle.Visibility = Visibility.Collapsed;
                else
                {
                    rectangle.Visibility = Visibility.Visible;
                    _color = value.Value;
                    translate.X = -20*(int) _color;
                }
            }
        }

    }
}

using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using MineSweeping.Model;

namespace MineSweeping
{
	public partial class Cell : UserControl
	{
		public Cell(bool hasBomb,int pointX,int pointY)
		{
			// 为初始化变量所必需
			InitializeComponent();

		    HasBomb = hasBomb;
		    PointX = pointX;
		    PointY = pointY;

		    State = CellState.None;
		    Opened = false;
		}

	    public bool Opened { get; set; }
	    public int PointX { get; private set; }
	    public int PointY { get; private set; }
	    public int AroundBombsCount { get; set; }

	    public int CurrentWidth
	    {
            get { return 16; }
	    }

	    public int CurrentHeight
	    {
            get { return 16; }
	    }

        public double Top
        {
            set { cellBorder.SetValue(Canvas.TopProperty, value); }
        }

        public double Left
        {
            set { cellBorder.SetValue(Canvas.LeftProperty, value); }
        }

        public bool HasBomb { get; private set; }
	    public CellState State { get; set; }
	}
}
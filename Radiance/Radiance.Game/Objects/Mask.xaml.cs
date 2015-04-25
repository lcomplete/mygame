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
using Radiance.Game.Common;

namespace Radiance.Game.Objects
{
    public partial class Mask : ObjectBase
    {
        public Mask(int mapCode, int maskCode, double singleWidth, double singleHeight, double top, double left, double opacity = 0.7)
        {
            InitializeComponent();
            IsHitTestVisible = false;

            MapCode = mapCode;
            MaskCode = maskCode;
            SingleWidth = singleWidth;
            SingleHeight = singleHeight;
            CoordinateMarginTop = singleHeight;//坐标设置到图片左下角 确保z-index顺序 
            Coordinate = new Point(left, top - singleHeight);
            Opacity = opacity;

            DrawMask();
        }

        public void DrawMask()
        {
            Body.Source =
                ImageUtils.GetImageSource(
                    new Uri(
                        string.Format("/Radiance.game;component/Resources/Map/{0}/Mask/{1}.jpg", MapCode.ToString(),
                                      MaskCode.ToString()), UriKind.Relative), true);
        }

        public int MaskCode { get; set; }
        public int MapCode { get; set; }

        public override sealed double SingleWidth
        {
            get { return Body.Width; }
            set { Body.Width = value; }
        }

        public override sealed double SingleHeight
        {
            get { return Body.Height; }
            set { Body.Height = value; }
        }
    }
}

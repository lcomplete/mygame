using System;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;

namespace Tetris.Common
{
    public class ColorUtils
    {
        public static Color GetColor(string color)
        {
            try
            {
                if (string.IsNullOrEmpty(color))
                    return Colors.Black;

                if (color.Length == 7)
                {
                    byte r = (byte)(Convert.ToUInt32(color.Substring(1, 2), 16));
                    byte g = (byte)(Convert.ToUInt32(color.Substring(3, 2), 16));
                    byte b = (byte)(Convert.ToUInt32(color.Substring(5, 2), 16));

                    return Color.FromArgb(255, r, g, b);
                }
                else
                {
                    return Colors.Black;
                }
            }
            catch
            {
                return Colors.Black;
            }
        }
    }
}

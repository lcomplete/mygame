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

namespace Radiance.Game.Common
{
    public class DebugUtils
    {
        private static bool _occuredError = false;

        public static void Warning(Exception ex)
        {
            if(!_occuredError)
            {
                MessageBox.Show(ex.ToString());
            }
            _occuredError = true;
        }

        public static void Warning(string error)
        {
            Warning(new Exception(error));
        }
    }
}

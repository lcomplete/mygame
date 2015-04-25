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

namespace Radiance.Game.Model
{
    public class ActionState
    {
        public ActionState()
        {
            RefreshInterval = 400;
        }

        public ActionState(int frameCount,int refreshInterval)
        {
            this.RefreshInterval = refreshInterval;
            this.FrameCount = frameCount;
        }
        public int RefreshInterval { get; set; }
        public int FrameCount { get; set; }
    }
}

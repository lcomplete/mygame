using System;

namespace Radiance.Game.Event
{
    public class FrameChangingEventArgs:EventArgs
    {
        public bool Continue { get; set; }
    }
}
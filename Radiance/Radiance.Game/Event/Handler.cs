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
using Radiance.Game.Objects;

namespace Radiance.Game.Event
{
    public delegate void CoordinateEventHandler(ObjectBase objectBase);

    public delegate void RemovedSelfEventHandler(ObjectBase objectBase);

    public delegate void FrameChangingEventHandler(DynamicalObject dynamicalObject,FrameChangingEventArgs fce);

    public delegate void OffsetChangedEventHandler(Map map);
}

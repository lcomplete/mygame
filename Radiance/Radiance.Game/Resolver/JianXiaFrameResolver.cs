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

namespace Radiance.Game.Resolver
{
    public class JianXiaFrameResolver:FrameResolver
    {
        protected override int GetPartImageIndex()
        {
            //剑侠世界 第一帧朝向为正南方
            return DynamicalObject.CurrentFrameCount * ((DynamicalObject.Direction+4)%8) + DynamicalObject.CurrentFrameIndex;
        }
    }
}

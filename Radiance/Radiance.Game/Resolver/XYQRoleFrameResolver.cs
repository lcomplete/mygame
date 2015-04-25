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
using Radiance.Game.Model;
using Radiance.Game.Objects;

namespace Radiance.Game.Resolver
{
    public class XYQRoleFrameResolver:FrameResolver
    {

        protected override int GetPartImageIndex()
        {
            return DynamicalObject.CurrentFrameCount*GetXYQIndex(DynamicalObject.Direction) + DynamicalObject.CurrentFrameIndex;
        }

        /// <summary>
        /// 7  0  1 默认方向 
        /// 6     2
        /// 5  4  3
        /// 2  6  3 梦幻西游方向
        /// 5     7
        /// 1  4  0
        /// </summary>
        /// <param name="direction"></param>
        /// <returns></returns>
        private int GetXYQIndex(int direction)
        {
            if(direction%2==0)
            {
                return 4 + ((direction == 0 ? 8 : direction == 2 ? 10 : direction) - 4)/2;
            }
            return ((direction == 1 ? 9 : direction) - 3)/2;
        }
    }
}

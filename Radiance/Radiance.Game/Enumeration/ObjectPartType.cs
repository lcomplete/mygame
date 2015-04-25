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

namespace Radiance.Game.Enumeration
{
    public enum ObjectPartType
    {
        //组装优先级最高的放在最前面
        Body,
        Head,
        LeftArm,
        RightArm,
        LeftHand,
        RightHand,
        Weapon,
        Effect,
        Magic
    }
}

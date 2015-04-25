using System;
using System.Collections.Generic;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using Radiance.Game.Enumeration;
using Radiance.Game.Model;
using System.Linq;
using Radiance.Game.Objects;

namespace Radiance.Game.Resolver
{
    public class JianxiaLeaderFrameResolver:JianXiaFrameResolver
    {
        protected override IList<ObjectPart> ReOrderObjectParts()
        {
            return DynamicalObject.ObjectParts.OrderBy(p => p.Type,
                                                    new JianxiaLeaderObjectPartComparer() { Direction = DynamicalObject.Direction }).ToList();
        }
    }

    public class JianxiaLeaderObjectPartComparer:IComparer<ObjectPartType>
    {
        public int Direction { get; set; }

        private bool IsLeftArmOrHand(ObjectPartType part)
        {
            return part == ObjectPartType.LeftArm || part == ObjectPartType.LeftHand;
        }
        private bool IsRightArmOrHandOrWeapon(ObjectPartType part)
        {
            return part == ObjectPartType.RightArm || part == ObjectPartType.RightHand || part == ObjectPartType.Weapon;
        }

        public int Compare(ObjectPartType x, ObjectPartType y)
        {
            //返回1表示y排在前
            if(x==y)
            {
                return 0;
            }

            if (y == ObjectPartType.Weapon && x == ObjectPartType.RightHand) //右手拿武器 先绘制手
                return -1;
            if (x == ObjectPartType.Weapon && y == ObjectPartType.RightHand)
                return 1;

            if(IsLeftArmOrHand(x))
            {
                return Direction >= 0 && Direction <= 4 ? -1 : 1;
            }
            if(IsRightArmOrHandOrWeapon(x))
            {
                return (Direction <= 7 && Direction >= 4) ? -1 : 1;
            }
            if (IsLeftArmOrHand(y))
            {
                return Direction >= 0 && Direction <= 4 ? 1 : -1;//在这个方向上 左手部件先绘制
            }
            if (IsRightArmOrHandOrWeapon(y))
            {
                return (Direction <=7 && Direction >=4) ? 1 : -1;//在这个方向上 右手部件先绘制
            }

            if (y == ObjectPartType.Head)
            {
                return Direction == 0 || Direction == 1 || Direction == 7 ? 1 : -1;//在此方向上 头部先绘制
            }
            if (x == ObjectPartType.Head)
            {
                return Direction == 0 || Direction == 1 || Direction == 7 ? -1 : 1;
            }
            
            return x > y ? 1 : -1;
        }
    }
}

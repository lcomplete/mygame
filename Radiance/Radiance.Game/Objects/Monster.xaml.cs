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
using Radiance.Game.Enumeration;
using Radiance.Game.Model;
using Radiance.Game.Resolver;

namespace Radiance.Game.Objects
{
    public partial class Monster : Sprite
    {
        public Monster(FrameResolver frameResolver, IList<ObjectPart> objectParts,Dictionary<Actions, ActionState> actionStates,Size bodySize,Rect physicalArea):
            base(frameResolver,objectParts,actionStates,bodySize,physicalArea)
        {
            
        }

        protected override bool IsHostility(Sprite sprite)
        {
            if(sprite!=null && sprite is Leader)
            {
                return true;
            }
            return false;
        }

        /// <summary>
        /// 搜寻范围(单位像素)
        /// </summary>
        public double SeekRange { get; set; }

        /// <summary>
        /// 跟踪范围(单位像素)
        /// </summary>
        public double FollowRange { get; set; }

        public override Sprite LockSprite
        {
            get
            {
                return base.LockSprite;
            }
            set
            {
                TryRemoveLockSpriteCoordinateChangedEvent();
                base.LockSprite = value;
                if (value != null)
                {
                    MoveTo(LockSprite.Coordinate);
                    base.LockSprite.CoordinateChanged += LockSprite_CoordinateChanged;
                }
            }
        }

        private void LockSprite_CoordinateChanged(ObjectBase objectBase)
        {
            double distance = Common.CollisionDetectionUtils.GetDistance(this.Coordinate, objectBase.Coordinate);
            if (distance > Math.Max(FollowRange,SeekRange))
            {
                LockSprite = null;
            }
            else
            {
                MoveTo(objectBase.Coordinate);
            }
        }

        private void TryRemoveLockSpriteCoordinateChangedEvent()
        {
            if (LockSprite != null)
            {
                LockSprite.CoordinateChanged -= LockSprite_CoordinateChanged;
            }
        }

        private Sprite Leader
        {
            get
            {
                if (Map != null)
                    return Map.Leader;
                return null;
            }
        }

        /// <summary>
        /// 是否为主动攻击
        /// </summary>
        public bool IsActiveAttack { get; set; }

        protected virtual void SeekLeader()
        {
            if (Visible && LockSprite == null && Leader != null)
            {
                if (Common.CollisionDetectionUtils.IsInDistance(Coordinate, Leader.Coordinate,SeekRange))
                {
                    LockSprite = Leader;
                }
            }
        }

        protected override void RefreshFrame()
        {
            base.RefreshFrame();
            if (IsActiveAttack)
            {
                SeekLeader();
            }
        }

        protected override void OnRemovedSelf()
        {
            base.OnRemovedSelf();
            TryRemoveLockSpriteCoordinateChangedEvent();
        }

        protected override void Die()
        {
            base.Die();
            TryRemoveLockSpriteCoordinateChangedEvent();
        }

        protected override double ComputerHarm()
        {
            return 10;
        }
    }
}

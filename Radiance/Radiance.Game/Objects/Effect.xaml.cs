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
using Radiance.Game.Event;
using Radiance.Game.Model;
using Radiance.Game.Resolver;

namespace Radiance.Game.Objects
{
    public partial class Effect : DynamicalObject
    {

        public Effect(FrameResolver frameResolver, ObjectPart objectPart, Actions currentActions, ActionState actionState, Size bodySize, bool start = true)
            : this(frameResolver, new List<ObjectPart>() { objectPart }, new Dictionary<Actions, ActionState>() { { currentActions, actionState } }, bodySize, currentActions, start)
        {
        }

        public Effect(FrameResolver frameResolver, IList<ObjectPart> objectParts, Dictionary<Actions, ActionState> actionStates, Size bodySize, Actions currentActions=Actions.Stand,bool start=true)
            : base(frameResolver, objectParts, actionStates, bodySize,currentActions,start)
        {
            InitializeComponent();
            CoordinateMarginLeft = bodySize.Width/2;
            CoordinateMarginTop = bodySize.Height/2;
        }

        private ObjectBase _attachObject;
        public ObjectBase AttachObject
        {
            get { return _attachObject; }
            set
            {
                TryRemoveAttachObjectCoordinateChangedEvent();
                _attachObject = value;
                FollowAttachObject(_attachObject);
                if (_attachObject != null)
                {
                    _attachObject.CoordinateChanged += FollowAttachObject;
                }
            }
        }

        private void TryRemoveAttachObjectCoordinateChangedEvent()
        {
            if (_attachObject != null)
            {
                _attachObject.CoordinateChanged -= FollowAttachObject;
            }
        }

        /// <summary>
        /// 是否跟随在附加对象正中间
        /// </summary>
        public bool FollowCenterPosition { get; set; }

        /// <summary>
        /// 跟随依附对象
        /// </summary>
        /// <param name="objectBase"></param>
        protected virtual void FollowAttachObject(ObjectBase objectBase)
        {
            Point followPoint = FollowCenterPosition ? objectBase.CenterPoint : objectBase.Coordinate;//note move centerpoint to base class
            Coordinate = followPoint;
        }

        /// <summary>
        /// 循环显示次数 小于或等于0时 不限制次数
        /// </summary>
        public int RepeatCount { get; set; }
        private int _alreadyRepeatCount;

        protected override void RefreshFrame()
        {
            base.RefreshFrame();
            if (RepeatCount > 0 && CurrentFrameIndex == 0)
            {
                _alreadyRepeatCount++;
                if (_alreadyRepeatCount == RepeatCount)
                {
                    RemoveSelf();
                }
            }
        }

        protected override void OnRemovedSelf()
        {
            TryRemoveAttachObjectCoordinateChangedEvent();
            base.OnRemovedSelf();
        }
    }
}

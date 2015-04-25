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
    public partial class Magic : Effect
    {
        public Magic(FrameResolver frameResolver, ObjectPart objectPart, Actions currentActions, ActionState actionState, Size bodySize, bool start = true)
            : base(frameResolver, new List<ObjectPart>() { objectPart }, new Dictionary<Actions, ActionState>() { { currentActions, actionState } }, bodySize, currentActions, start)
        {
        }

        public Magic(FrameResolver frameResolver, IList<ObjectPart> objectParts, Dictionary<Actions, ActionState> actionStates, Size bodySize, Actions currentActions=Actions.Stand,bool start=true)
            : base(frameResolver, objectParts, actionStates, bodySize,currentActions,start)
        {
            InitializeComponent();
        }

        /// <summary>
        /// 伤害起效帧索引
        /// </summary>
        public int DamageFrameIndex { get; set; }
        /// <summary>
        /// 伤害范围(坐标为原点 该值为半径)
        /// </summary>
        public int DamageRange { get; set; }

        protected override void RefreshFrame()
        {
            base.RefreshFrame();
            if(DamageFrameIndex==CurrentFrameIndex)
            {
                Attack();
            }
        }

        private void Attack()
        {
            //todo
        }
    }
}

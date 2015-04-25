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
    public partial class NPC : Sprite
    {
        public NPC(FrameResolver frameResolver, IList<ObjectPart> objectParts, Dictionary<Actions, ActionState> actionStates, Size bodySize, Rect physicalArea) :
            base(frameResolver,objectParts,actionStates,bodySize,physicalArea)
        {
            FullLife = 1;
            Life = 1;
        }

        protected override bool IsHostility(Sprite sprite)
        {
            return false;
        }

        protected override double ComputerHarm()
        {
            return 0;
        }
    }
}

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
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using System.Windows.Threading;
using Radiance.Game.Enumeration;
using Radiance.Game.Event;
using Radiance.Game.Model;
using Radiance.Game.Resolver;

namespace Radiance.Game.Objects
{
    public partial class DynamicalObject:ObjectBase
    {
        private DynamicalObject()
        {
            InitializeComponent();
        }

        public DynamicalObject(FrameResolver frameResolver, ObjectPart objectPart, Actions currentActions, ActionState actionState, Size bodySize, bool start = true)
            : this(frameResolver, new List<ObjectPart>() { objectPart }, new Dictionary<Actions, ActionState>() { { currentActions, actionState } }, bodySize, currentActions, start)
        {
        }

        public DynamicalObject(FrameResolver frameResolver, IList<ObjectPart> objectParts,Dictionary<Actions, ActionState> actionStates,Size bodySize , Actions currentActions=Actions.Stand,bool start=true)
            : this()
        {
            this.FrameResolver = frameResolver;
            this.ObjectParts = objectParts;
            this.ActionStates = actionStates;
            _action = currentActions;
            SingleWidth = bodySize.Width;
            SingleHeight = bodySize.Height;
            
            Timer = new DispatcherTimer();
            InitAction();
            Timer.Tick += Timer_Tick;
            if(start)
            {
                Start();
            }
        }

        #region 界面

        /// <summary>
        /// 设置阴影
        /// </summary>
        public bool ShadowVisible
        {
            set { BodyShadow.BlurRadius = value ? 7 : 0; }
        }

        #endregion

        #region 方向

        /// <summary>
        /// 获取或设置当前朝向:0朝上4朝下,顺时针依次为0,1,2,3,4,5,6,7(关联属性)
        /// </summary>
        public int Direction
        {
            get { return Convert.ToInt32(GetValue(DirectionProperty)); }
            set { SetValue(DirectionProperty, value); }
        }
        public static readonly DependencyProperty DirectionProperty = DependencyProperty.Register(
            "Direction",
            typeof(int),
            typeof(DynamicalObject),
            null
        );

        #endregion

        #region 计时器

        public DispatcherTimer Timer { get; set; }

        public int RefreshInterval
        {
            get { return Timer.Interval.Milliseconds; }
            set { Timer.Interval = TimeSpan.FromMilliseconds(value); }
        }

        protected virtual void Timer_Tick(object sender, EventArgs e)
        {
            FrameChangingEventArgs fce = OnFrameChanging();
            if (fce==null || fce.Continue)
            {
                RefreshFrame();
            }
        }

        public void Start()
        {
            Timer.Start();
        }

        public void Stop()
        {
            Timer.Stop();
        }

        public event FrameChangingEventHandler FrameChanging;

        protected virtual FrameChangingEventArgs OnFrameChanging()
        {
            if (FrameChanging != null)
            {
                FrameChangingEventArgs fce=new FrameChangingEventArgs();
                FrameChanging(this,fce);
                return fce;
            }
            return null;
        }

        public int NextFrameIndex
        {
            get { return CurrentFrameIndex == CurrentFrameCount - 1 ? 0 : CurrentFrameIndex + 1; }
        }

        public int PrevFrameIndex
        {
            get { return CurrentFrameIndex == 0 ? CurrentFrameCount - 1 : CurrentFrameIndex - 1; }
        }

        private void CirculateIncreaseCurrentFrameIndex()
        {
            CurrentFrameIndex = NextFrameIndex;
        }

        protected virtual void RefreshFrame()
        {
            if (base.Visible)//不可见时不解析帧 但递增帧索引
            {
                Body.Source = ResolveCurrentFrame();
            }
            CirculateIncreaseCurrentFrameIndex();
        }

        #endregion

        #region 动作

        private Actions _action;

        public Actions Action
        {
            get { return _action; }
            set
            {
                if (_action != value)
                {
                    Actions oldAction = _action;
                    _action = value;
                    ChangeAction(oldAction);
                }
            }
        }

        public Dictionary<Actions, ActionState> ActionStates { get; set; }

        protected virtual void ChangeAction(Actions oldAction)
        {
            InitAction();
        }

        public void InitAction()
        {
            CurrentFrameIndex = 0;
            CurrentFrameCount = ActionStates[Action].FrameCount;
            RefreshInterval = ActionStates[Action].RefreshInterval;
        }

        #endregion

        #region 部件相关信息

        public IList<ObjectPart> ObjectParts { get; set; }
        public int CurrentFrameIndex { get; set; }
        public int CurrentFrameCount { get; set; }
        public sealed override double SingleWidth { get { return Body.Width; } set { Body.Height = value; } }
        public sealed override double SingleHeight { get { return Body.Height; } set { Body.Width = value; } }

        /// <summary>
        /// 对象实体区域（相对于本对象的位置）
        /// </summary>
        public Rect PhysicalArea { get; set; }

        /// <summary>
        /// 对象实体区域（相对于外部元素的位置）
        /// </summary>
        public Rect GlobalPhysicalArea
        {
            get { return new Rect(Left + PhysicalArea.X, Top + PhysicalArea.Y, PhysicalArea.Width, PhysicalArea.Height); }
        }

        /// <summary>
        /// 对象实体中心位置（相对于外部元素的位置）
        /// </summary>
        public Point GlobalPhysicalCenter
        {
            get
            {
                return new Point(GlobalPhysicalArea.Left + GlobalPhysicalArea.Width/2,
                                 GlobalPhysicalArea.Top + GlobalPhysicalArea.Height/2);
            }
        }

        #endregion

        #region 帧解析器

        private FrameResolver _frameResolver;

        public FrameResolver FrameResolver
        {
            get { return _frameResolver; }
            set
            {
                _frameResolver = value;
                _frameResolver.DynamicalObject = this;
            }
        }

        public WriteableBitmap ResolveCurrentFrame()
        {
            return FrameResolver.ResolveCurrentFrame();
        }

        #endregion

    }
}
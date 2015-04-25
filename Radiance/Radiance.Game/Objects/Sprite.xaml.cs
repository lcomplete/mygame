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
using System.Windows.Threading;
using Radiance.Core.AStar;
using Radiance.Game.Common;
using Radiance.Game.Enumeration;
using Radiance.Game.Event;
using Radiance.Game.Model;
using Radiance.Game.Resolver;

namespace Radiance.Game.Objects
{
    public abstract partial class Sprite : DynamicalObject
    {
        /// <summary>
        /// 精灵基类
        /// </summary>
        protected Sprite(FrameResolver frameResolver, IList<ObjectPart> objectParts,Dictionary<Actions, ActionState> actionStates,Size bodySize,Rect physicalArea,Actions currentAction=Actions.Stand,bool start=true):
            base(frameResolver,objectParts,actionStates,bodySize,currentAction,start)
        {
            InitializeComponent();
            PhysicalArea = physicalArea;
            Direction = 4;

            SetDefaultUI();
        }

        protected void SetDefaultUI()
        {
            MaskImage.ImageFailed += MaskImage_ImageFailed;
            Intro.SetValue(Canvas.TopProperty, Math.Max(PhysicalArea.Top - 55, 0));
            Intro.Width = SingleWidth;
            TitleBrush = new SolidColorBrush(Colors.White);
            CharacterNameBrush = new SolidColorBrush(Colors.Yellow);
            LifeBrush = new SolidColorBrush(Color.FromArgb(255, 50, 205, 50));
            LifeUITotalWidth = 60;
        }

        #region 攻击相关

        /// <summary>
        /// 攻击范围
        /// </summary>
        public double AttackRange { get; set; }
        /// <summary>
        /// 锁定精灵
        /// </summary>
        public virtual Sprite LockSprite { get; set; }
        /// <summary>
        /// 攻击关键帧（到该帧时才计算伤害）
        /// </summary>
        public int AttackKeyFrame { get; set; }

        public bool CanAttackLockSprite
        {
            get
            {
                return IsHostility(LockSprite) && !LockSprite.IsDead &&
                       CollisionDetectionUtils.IsInDistance(this.Coordinate, LockSprite.Coordinate, AttackRange);
            }
        }

        /// <summary>
        /// 是否为敌对精灵
        /// </summary>
        /// <param name="sprite"></param>
        /// <returns></returns>
        protected abstract bool IsHostility(Sprite sprite);

        public void BeginAttack()
        {
            if (LockSprite != null)
            {
                RemoveCurrentAnimation();
                Direction = LogicUtils.GetDirection(LockSprite.Coordinate.X, LockSprite.Coordinate.Y,
                                                    Coordinate.X, Coordinate.Y);

                Action = Actions.Attack;
            }
        }

        #endregion

        #region 蒙版

        /// <summary>
        /// 获取或设置精灵身体蒙板是否可见
        /// </summary>
        public bool MaskVisibile {
            get { return Mask.Visibility==Visibility.Visible; }
            set { Mask.Visibility = value ? Visibility.Visible : Visibility.Collapsed; }
        }

        /// <summary>
        /// 获取或设置精灵身体蒙板颜色
        /// </summary>
        public Brush MaskColor {
            get { return Mask.Fill; }
            set { Mask.Fill = value; }
        }

        public void ShowMask(Color color)
        {
            Mask.Height = SingleHeight;
            Mask.Width = SingleWidth;
            MaskColor = new SolidColorBrush(color);
            MaskVisibile = true;
        }

        public void HideMask()
        {
            MaskVisibile = false;
        }

        #endregion

        #region 精灵属性

        /// <summary>
        /// 头衔
        /// </summary>
        public string Title
        {
            get { return TextTitle.Text; }
            set { TextTitle.Text = value; }
        }

        /// <summary>
        /// 获取或设置姓名
        /// </summary>
        public string CharacterName
        {
            get { return TextCharacterName.Text; }
            set { TextCharacterName.Text = value; }
        }

        /// <summary>
        /// 最大生命值
        /// </summary>
        public double FullLife { get; set; }

        private double _life;
        /// <summary>
        /// 当前生命值
        /// </summary>
        public double Life
        {
            get { return _life; }
            set
            {
                _life = value;
                if (FullLife > 0)
                {
                    LifeUIWidth = Math.Max((_life/FullLife)*LifeUITotalWidth,0);
                }
                if(_life<=0)
                {
                    Die();
                }
            }
        }

        public bool IsDead { get { return Action == Actions.Death; } }

        protected virtual void Die()
        {
            Action = Actions.Death;
        }

        #endregion

        #region 界面属性

        /// <summary>
        /// 头衔笔刷
        /// </summary>
        public Brush TitleBrush {
            set { TextTitle.Foreground = value; }
        }

        /// <summary>
        /// 姓名笔刷
        /// </summary>
        public Brush CharacterNameBrush {
            set { TextCharacterName.Foreground = value; }
        }

        /// <summary>
        /// 设置头顶生命值条颜色笔刷
        /// </summary>
        public Brush LifeBrush {
            set { LifeRect.Fill = value; }
        }

        /// <summary>
        /// 获取或设置头顶生命值条当前宽度
        /// </summary>
        public double LifeUIWidth {
            get { return LifeRect.Width; }
            protected set { LifeRect.Width = value; }
        }

        /// <summary>
        /// 获取或设置头顶生命值条满值宽度
        /// </summary>
        public double LifeUITotalWidth {
            get { return LifeBorder.Width; }
            set { LifeBorder.Width = value; }
        }

        //必须注册此事件,否则会造成系统崩溃,由蒙板图片源引发
        protected void MaskImage_ImageFailed(object sender, ExceptionRoutedEventArgs e)
        {
            sender = null;
        }

        #endregion

        #region 刷新界面、改变动作

        protected override void RefreshFrame()
        {
            if (Action == Actions.Attack)
            {
                if (CurrentFrameIndex == AttackKeyFrame)
                {
                    LockSprite.Life -= ComputerHarm();
                }
                if(LockSprite.IsDead)
                {
                    Action = Actions.Stand;
                }
            }

            base.RefreshFrame();
            if (Action == Actions.Death && CurrentFrameIndex == 0)
            {
                Stop();
            }
            else if (MaskVisibile)
            {
                MaskImage.ImageSource = Body.Source;
            }
        }

        protected abstract double ComputerHarm();

        protected override void ChangeAction(Actions oldAction)
        {
            base.ChangeAction(oldAction);
            if (Action == Actions.Stand)
            {
                PauseStoryboard();
                RefreshFrame();
            }
        }

        #endregion

        #region 故事板

        private Storyboard _storyboard;
        
        protected void OpenStoryboard()
        {
            _storyboard = new Storyboard();
        }

        protected void PauseStoryboard()
        {
            if(_storyboard!=null)
            {
                _storyboard.Pause();
            }
        }

        protected void StartStoryboard()
        {
            if(_storyboard!=null)
            {
                _storyboard.Begin();
            }
        }

        protected void AddAnimation(Timeline value)
        {
            if (_storyboard == null)
            {
                _storyboard=new Storyboard();
            }
            _storyboard.Children.Add(value);
        }

        protected void RemoveCurrentAnimation()
        {
            if(_storyboard!=null)
            {
                _storyboard.Pause();
                _storyboard=new Storyboard();
            }
        }

        #endregion

        #region 移动相关

        /// <summary>
        /// 路障矩阵
        /// </summary>
        public byte[,] FixedRoadBlock
        {
            get
            {
                if (Map != null)
                {
                    return Map.FixedRoadBlock;
                }
                return null;
            }
        }

        /// <summary>
        /// 目的地
        /// </summary>
        public Point Destination { get; set; }

        /// <summary>
        /// 脚底Y方向保留单元格数量（用于构造动态障碍物）
        /// </summary>
        public int HoldGridY { get; set; }

        /// <summary>
        /// 脚底X方向保留单元格数量（用于构造动态障碍物）
        /// </summary>
        public int HoldGridX { get; set; }

        public bool IsAstarMove { get; private set; }

        protected override void OnCoordinateChanged()
        {
            base.OnCoordinateChanged();
            if (CanAttackLockSprite)
            {
                BeginAttack();
            }
            else if (Destination == Coordinate)
            {
                Action = Actions.Stand;
            }
            else
            {
                DetectionRoadblock();
            }
        }

        private void DetectionRoadblock()
        {
            if (!IsAstarMove && Action == Actions.Run && WillCollide(Direction))
            {
                AStarMove();
            }
        }

        private bool WillCollide(Point p)
        {
            return WillCollide(LogicUtils.GetDirection(p.X, p.Y, Coordinate.X, Coordinate.Y));
        }

        protected bool WillCollide(int direction)
        {
            if (FixedRoadBlock == null)
            {
                return false;
            }

            //精灵当前在障碍物矩阵中的点
            int currentX = (int)(Coordinate.X / Map.GridSize);
            int currentY = (int)(Coordinate.Y / Map.GridSize);
            //根据方向得到偏移量
            int willOffsetX = direction < 4 && direction > 0 ? 1 : direction > 4 && direction < 8 ? -1 : 0;
            int willOffsetY = direction == 0 || direction == 1 || direction == 7
                                  ? -1
                                  : direction > 2 && direction < 6 ? 1 : 0;
            //得到起始检测点
            int beginX = Math.Min(Math.Max(currentX - HoldGridX + willOffsetX, 0),
                                  FixedRoadBlock.GetUpperBound(0) - 2 * HoldGridX - 1);
            int beginY = Math.Min(Math.Max(currentY - HoldGridY + willOffsetY, 0),
                                  FixedRoadBlock.GetUpperBound(1) - 2 * HoldGridY - 1);
            //根据起始点和精灵占据范围 查找矩阵内是否有障碍物
            for (int i = beginX; i < beginX + HoldGridX * 2 + 1; i++)
            {
                for (int j = beginY; j < beginY + HoldGridY * 2 + 1; j++)
                {
                    if (FixedRoadBlock[i, j] == 0)
                    {
                        return true;
                    }
                }
            }

            return false;
        }

        public virtual void MoveTo(Point destination)
        {
            if(destination==Coordinate)
            {
                return;
            }
            if(CanAttackLockSprite)
            {
                BeginAttack();
                return;
            }

            Destination = destination;
            Action = Actions.Run;
            Direction = LogicUtils.GetDirection(destination.X, destination.Y, Coordinate.X, Coordinate.Y);
            if (WillCollide(Direction))
            {
                AStarMove();
            }
            else
            {
                LinearMove();
            }
        }

        /// <summary>
        /// 直线移动
        /// </summary>
        protected void LinearMove()
        {
            IsAstarMove = false;

            OpenStoryboard();
            int size = Map == null ? 10 : Map.GridSize;
            //计算总的移动花费
            double moveCost = LogicUtils.GetAnimationTimeConsuming(this.Coordinate, Destination, size, size, RefreshInterval);

            DoubleAnimation doubleAnimation = new DoubleAnimation()
            {
                To = Direction,
                Duration = new Duration(TimeSpan.Zero)
            };
            Storyboard.SetTarget(doubleAnimation, this);
            Storyboard.SetTargetProperty(doubleAnimation, new PropertyPath("Direction"));
            AddAnimation(doubleAnimation);

            PointAnimation pointAnimation = new PointAnimation()
                                                {
                                                    To = Destination,
                                                    Duration = new Duration(TimeSpan.FromMilliseconds(moveCost))
                                                };
            Storyboard.SetTarget(pointAnimation, this);
            Storyboard.SetTargetProperty(pointAnimation, new PropertyPath("Coordinate"));
            AddAnimation(pointAnimation);
            StartStoryboard();
        }

        protected void AStarMove()
        {
            if(FixedRoadBlock==null)
            {
                return;
            }
            IsAstarMove = true;

            Point start = new Point() {X = this.Coordinate.X/Map.GridSize, Y = this.Coordinate.Y/Map.GridSize},
                  end = new Point() {X = Destination.X/Map.GridSize, Y = Destination.Y/Map.GridSize};

            if (start != end)
            {
                PathFinderFast pathFinderFast = new PathFinderFast(FixedRoadBlock)
                                                    {
                                                        HeavyDiagonals = false,
                                                        HeuristicEstimate = 2,
                                                        SearchLimit = 2000
                                                    };
                List<PathFinderNode> path = pathFinderFast.FindPath(start, end);

                if (path == null || path.Count <= 1)
                {
                    this.Action = Actions.Stand;
                }
                else
                {
                    OpenStoryboard();
                    Duration moveCost = new Duration(TimeSpan.FromMilliseconds(path.Count*RefreshInterval));//todo enhance this
                    //方向动画
                    var doubleAnimationUsingKeyFrames = new DoubleAnimationUsingKeyFrames() {Duration = moveCost};
                    Storyboard.SetTarget(doubleAnimationUsingKeyFrames, this);
                    Storyboard.SetTargetProperty(doubleAnimationUsingKeyFrames, new PropertyPath("Direction"));
                    //坐标动画
                    var pointAnimationUsingKeyFrames = new PointAnimationUsingKeyFrames() {Duration = moveCost};
                    Storyboard.SetTarget(pointAnimationUsingKeyFrames, this);
                    Storyboard.SetTargetProperty(pointAnimationUsingKeyFrames, new PropertyPath("Coordinate"));

                    LinearPointKeyFrame linearPointKeyFrame;
                    LinearDoubleKeyFrame linearDoubleKeyFrame;
                    for (int i = path.Count - 1; i >= 0; i--)
                    {
                        KeyTime keyTime =
                            KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(this.RefreshInterval*(path.Count - 1 - i)));
                        //加入坐标变换的匀速关键帧
                        linearPointKeyFrame = new LinearPointKeyFrame() {KeyTime = keyTime};
                        linearPointKeyFrame.Value = i == path.Count - 1
                                                        ? Coordinate
                                                        : i == 0
                                                              ? Destination
                                                              : new Point(path[i].X*Map.GridSize + Map.GridSize/2,
                                                                          path[i].Y*Map.GridSize + Map.GridSize/2);
                        pointAnimationUsingKeyFrames.KeyFrames.Add(linearPointKeyFrame);
                        //加入朝向匀速关键帧
                        linearDoubleKeyFrame = new LinearDoubleKeyFrame() {KeyTime = keyTime};
                        int targetI = i == 0 ? 0 : i - 1;
                        linearDoubleKeyFrame.Value = LogicUtils.GetDirectionByGrid(path[targetI].X, path[targetI].Y,
                                                                                     path[targetI + 1].X,
                                                                                     path[targetI + 1].Y);
                        doubleAnimationUsingKeyFrames.KeyFrames.Add(linearDoubleKeyFrame);
                    }
                    AddAnimation(pointAnimationUsingKeyFrames);
                    AddAnimation(doubleAnimationUsingKeyFrames);
                    StartStoryboard();
                }
            }
        }

        #endregion

    }
}

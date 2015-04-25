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
using System.Linq;
using Radiance.Game.Common;
using Radiance.Game.Event;

namespace Radiance.Game.Objects
{
    public partial class Map : Canvas
    {

        /// <summary>
        /// 地图遮罩控件
        /// </summary>
        public Map(int mapCode, int fullWidth,int fullHeight,int sectionWidth,int sectionHeight,double screenWidth,double screenHeight, Canvas wrapper)
        {
            InitializeComponent();

            _centerSectionPoint=new Point(-1,-1);
            _currentSections = new Dictionary<Point, bool>(9);

            this.MapCode = mapCode;
            this.FullWidth = fullWidth;
            this.FullHeight = fullHeight;
            this.SectionHeight = sectionHeight;
            this.SectionWidth = sectionWidth;
            this.ScreenWidth = screenWidth;
            this.ScreenHeight = screenHeight;
            this.Wrapper = wrapper;
        }

        #region 地图相关信息

        public byte[,] FixedRoadBlock;//todo make this property
        public int GridSize { get; set; }

        /// <summary>
        /// 地图代号
        /// </summary>
        public int MapCode { get; private set; }

        /// <summary>
        /// 获取或设置地图偏移量
        /// </summary>
        public Point Offset
        {
            get { return (Point)GetValue(OffsetProperty); }
            set { SetValue(OffsetProperty, value); }
        }

        public static readonly DependencyProperty OffsetProperty = DependencyProperty.Register(
            "Offset",
            typeof(Point),
            typeof(Map),
            new PropertyMetadata(ChangeOffsetProperty)
        );

        private static void ChangeOffsetProperty(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            Map map = (Map)d;
            Point offset = (Point)e.NewValue;
            map.SetValue(Canvas.LeftProperty,offset.X);
            map.SetValue(Canvas.TopProperty,offset.Y);
            map.OnOffsetChanged();
        }

        public event OffsetChangedEventHandler OffsetChanged;
        private void OnOffsetChanged()
        {
            if (OffsetChanged != null)
            {
                OffsetChanged(this);
            }
        }

        public Canvas Wrapper
        {
            get { return this.Parent as Canvas; }
            set { value.Children.Add(this); }
        }

        #endregion

        #region 绘制切片

        private Dictionary<Point, bool> _currentSections; //当前切片字典集合 true表示不可移除 false表示应移除

        private bool ExistsSection(Point point)
        {
            return _currentSections.ContainsKey(point);
        }

        /// <summary>
        /// 将所有切片设置为可移除
        /// </summary>
        private void SetSectionRemoveableFlag()
        {
            List<Point> pointKeys = new List<Point>();
            pointKeys.AddRange(_currentSections.Keys);
            foreach (var key in pointKeys)
            {
                _currentSections[key] = false;
            }
        }

        private void AddSection(Point sectionPoint)
        {
            if (!ExistsSection(sectionPoint))
            {
                int x = (int) sectionPoint.X;
                int y = (int) sectionPoint.Y;
                var image = new Image()
                                {
                                    Name = "Section_" + sectionPoint.ToString(),
                                    Width = SectionWidth + 1,
                                    Height = SectionHeight + 1
                                };
                image.SetValue(Canvas.ZIndexProperty,0);
                Children.Add(image);
                image.Source =
                    ImageUtils.GetImageSource(
                        new Uri(
                            string.Format("/Radiance.game;component/Resources/Map/{0}/Section/{1}_{2}.jpg",
                                          MapCode.ToString(), x.ToString(), y.ToString()), UriKind.Relative),
                        true);

                image.SetValue(LeftProperty, (double) x*SectionWidth);
                image.SetValue(TopProperty, (double) y*SectionHeight);
            }
            _currentSections[sectionPoint] = true; //标记为不可移除
        }

        /// <summary>
        /// 移除已绘制但不再使用的切片
        /// </summary>
        private void RemoveUnusedSections()
        {
            List<Point> pointKeys = new List<Point>();
            pointKeys.AddRange(_currentSections.Keys);
            foreach (var key in pointKeys)
            {
                if (!_currentSections[key])
                {
                    UIElement image = FindName("Section_" + key.ToString()) as UIElement;
                    Children.Remove(image);
                    _currentSections.Remove(key);
                }
            }
        }

        private void DrawSection()
        {
            SetSectionRemoveableFlag();
            Point centerSectionPoint = CenterSectionPoint;
            int xSectionCount = FullWidth/SectionWidth;
            int ySectionCount = FullHeight/SectionHeight;
            Point startSectionPoint = new Point(Math.Min(Math.Max(centerSectionPoint.X - 1, 0), xSectionCount - 3),
                                                Math.Min(Math.Max(centerSectionPoint.Y - 1, 0), ySectionCount - 3));
            for (int i = 0; i < 3; i++)
            {
                for (int j = 0; j < 3; j++)
                {
                    var sectionPoint = new Point(startSectionPoint.X + i, startSectionPoint.Y + j);
                    AddSection(sectionPoint);
                }
            }
            RemoveUnusedSections();
        }

        private Point _centerSectionPoint;
        /// <summary>
        /// 主角当前所在切片点
        /// </summary>
        public Point CenterSectionPoint
        {
            get { return _centerSectionPoint; }
            set
            {
                if ((int)_centerSectionPoint.X != (int)value.X || (int)_centerSectionPoint.Y != (int)value.Y)
                {
                    _centerSectionPoint = value;
                    DrawSection();
                }
            }
        }

        #endregion

        #region 主角和怪物

        public void AddMonster(Sprite sprite)
        {
            AddObject(sprite);
        }

        public IEnumerable<Monster> Monsters
        {
            get { return Children.OfType<Monster>(); }
        }

        private Sprite _leader;

        public Sprite Leader
        {
            get { return _leader; }
            set
            {
                if (_leader != null)
                {
                    Children.Remove(_leader);
                }
                _leader = value;
                AddObject(_leader);
                _leader.CoordinateChanged += _leader_CoordinateChanged;
                _leader_CoordinateChanged(_leader);
            }
        }

        public void AddObject(ObjectBase objectBase)
        {
            Children.Add(objectBase);
        }

        void _leader_CoordinateChanged(ObjectBase objectBase)
        {
            CenterSectionPoint = new Point((int)objectBase.Coordinate.X / SectionWidth, (int)objectBase.Coordinate.Y / SectionHeight);//更新所在切片
            double offsetX = -Math.Min(Math.Max(objectBase.Coordinate.X - ScreenWidth / 2, 0), FullWidth - ScreenWidth);
            double offsetY = -Math.Min(Math.Max(objectBase.Coordinate.Y - ScreenHeight / 2, 0), FullHeight - ScreenHeight);
            Offset = new Point(offsetX, offsetY);//更新地图偏移量
        }

        #endregion

        #region 宽高等信息

        public int FullWidth
        {
            get { return Convert.ToInt32(Width); }
            set { Width = value; }
        }
        public int FullHeight
        {
            get { return Convert.ToInt32(Height); }
            set { Height = value; }
        }

        public int SectionWidth { get; private set; }
        public int SectionHeight { get; private set; }
        public double ScreenWidth { get; set; }
        public double ScreenHeight { get; set; }

        #endregion
        
    }
}

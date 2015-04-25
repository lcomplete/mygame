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
using Radiance.Game.Event;

namespace Radiance.Game.Objects
{
    public abstract partial class ObjectBase : Canvas
    {
        protected ObjectBase()
        {
            InitializeComponent();
        }

        public abstract double SingleWidth { get; set; }
        public abstract double SingleHeight { get; set; }

        #region 显示隐藏

        public bool Visible
        {
            get { return this.Visibility == Visibility.Visible; }
        }

        public void Hide()
        {
            this.Visibility = Visibility.Collapsed;
        }

        public void Show()
        {
            this.Visibility = Visibility.Visible;
            Coordinate = Coordinate;
        }

        #endregion

        #region 位置

        public Map Map
        {
            get { return this.Parent as Map; }
        }

        public event CoordinateEventHandler CoordinateChanged;
        /// <summary>
        /// 获取或设置精灵脚底坐标(关联属性)
        /// </summary>
        public Point Coordinate
        {
            get { return (Point)GetValue(CoordinateProperty); }
            set { SetValue(CoordinateProperty, value); }
        }

        public static readonly DependencyProperty CoordinateProperty = DependencyProperty.Register(
            "Coordinate",
            typeof(Point),
            typeof(ObjectBase),
            new PropertyMetadata(ChangeCoordinateProperty)
        );

        private static void ChangeCoordinateProperty(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            ObjectBase obj = (ObjectBase)d;
            Point point = (Point)e.NewValue;
            if (obj.Visible)
            {
                obj.SetValue(Canvas.LeftProperty, point.X - obj.CoordinateMarginLeft);
                obj.SetValue(Canvas.TopProperty, point.Y - obj.CoordinateMarginTop);
                obj.SetValue(Canvas.ZIndexProperty, (int)point.Y);
            }
            obj.OnCoordinateChanged();
        }

        protected virtual void OnCoordinateChanged()
        {
            if (CoordinateChanged != null)
            {
                CoordinateChanged(this);
            }
        }

        /// <summary>
        /// 获取或设置当前对象左上角离实际坐标的X距离
        /// </summary>
        public double CoordinateMarginLeft { get; set; }

        /// <summary>
        /// 获取或设置当前对象左上角离实际坐标的Y距离
        /// </summary>
        public double CoordinateMarginTop { get; set; }

        public double Top { get { return Convert.ToDouble(GetValue(Canvas.TopProperty)); } }

        public double Left { get { return Convert.ToDouble(GetValue(Canvas.LeftProperty)); } }

        /// <summary>
        /// 对象中心点（相对外部元素的位置）
        /// </summary>
        public Point CenterPoint
        {
            get { return new Point(Top + SingleWidth / 2, Left + SingleHeight / 2); }
        }

        /// <summary>
        /// 实际区域
        /// </summary>
        public Rect ActualRect
        {
            get
            {
                return new Rect(Top,Left,SingleWidth,SingleHeight);
            }
        }

        #endregion

        #region 移除自身

        public void RemoveSelf()
        {
            var parent = Parent as Canvas;
            if (parent != null)
            {
                parent.Children.Remove(this);
            }
            OnRemovedSelf();
        }

        public event RemovedSelfEventHandler Removed;
        protected virtual void OnRemovedSelf()
        {
            if(Removed!=null)
            {
                Removed(this);
            }
        }

        #endregion
    }
}

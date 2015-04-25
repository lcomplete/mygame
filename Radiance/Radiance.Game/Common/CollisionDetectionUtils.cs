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

namespace Radiance.Game.Common
{
    public sealed class CollisionDetectionUtils
    {
        /// <summary>
        /// 判断点是矩形区域内
        /// </summary>
        public static bool IsInRect(Rect physicalArea, Point point)
        {
            return point.X >= physicalArea.Left && point.X <= physicalArea.Top + physicalArea.Width && point.Y >= physicalArea.Top &&
                   point.Y <= physicalArea.Top + physicalArea.Height;
        }

        public static bool IsInDistance(Point point1,Point point2,double distance)
        {
            return GetDistance(point1, point2) < distance;
        }

        public static double GetDistance(Point point1,Point point2)
        {
            return Math.Sqrt(Math.Pow(point2.X - point1.X, 2) + Math.Pow(point2.Y - point1.Y, 2));
        }

        public static bool RectHitCircle(Rect targetRect, Point currentPosition, double radius)
        {
            //计算矩形顶点是否在圆内
            Point[] rectPoints = GetRectVertex(targetRect);
            for (int i = 0; i < rectPoints.Length; i++)
            {
                if (IsInDistance(rectPoints[0], currentPosition, radius))
                    return true;
            }
            //圆心X坐标在矩形x轴上时 Y坐标在targetRect.Y-radius到targetRect.Y+targetRect.Height+radius范围内则产生碰撞
            if (currentPosition.X > targetRect.X && currentPosition.X < targetRect.X + targetRect.Width)
            {
                if (currentPosition.Y > targetRect.Y - radius && currentPosition.Y < targetRect.Y + targetRect.Height + radius)
                    return true;
            }
            if (currentPosition.Y > targetRect.Y && currentPosition.Y < targetRect.Y + targetRect.Height)
            {
                if (currentPosition.X > targetRect.X - radius && currentPosition.X < targetRect.X + targetRect.Width + radius)
                    return true;
            }

            return false;
        }

        public static bool RectHitRect(Rect targetRect, Rect currentRect)
        {
            double minDistanceX = targetRect.Width / 2 + currentRect.Width / 2;//产生碰撞的最小X距离
            double minDistanceY = targetRect.Height / 2 + currentRect.Height / 2;
            Point targetCenterPoint = new Point(targetRect.X + targetRect.Width / 2, targetRect.Y + targetRect.Height / 2);
            Point currentCenterPoint = new Point(currentRect.X + currentRect.Width / 2, currentRect.Y + currentRect.Height / 2);
            //实际距离小于最小碰撞距离则发生碰撞
            return Math.Abs(targetCenterPoint.X - currentCenterPoint.X) < minDistanceX &&
                   Math.Abs(targetCenterPoint.Y - currentCenterPoint.Y) < minDistanceY;
        }

        public static bool PointInRect(Rect targetRect, Point point)
        {
            return point.X > targetRect.X && point.X < targetRect.X + targetRect.Width
                   && point.Y > targetRect.Y && point.Y < targetRect.Y + targetRect.Height;
        }

        /// <summary>
        /// 获得矩形顶点 按Z方向排列
        /// </summary>
        /// <param name="targetRect"></param>
        /// <returns></returns>
        public static Point[] GetRectVertex(Rect targetRect)
        {
            return new Point[]
                       {
                           new Point(targetRect.X, targetRect.Y),
                           new Point(targetRect.X + targetRect.Width, targetRect.Y),
                           new Point(targetRect.X, targetRect.Y + targetRect.Height),
                           new Point(targetRect.X + targetRect.Width, targetRect.Y + targetRect.Height)
                       };
        }

    }
}

using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Radiance.Game.Enumeration;

namespace Radiance.Game.Common
{
    public sealed class LogicUtils
    {

        /// <summary>
        /// 获得当前位置到目标位置的方向
        /// </summary>
        /// <param name="targetX">目标点的X值</param>
        /// <param name="targetY">目标点的Y值</param>
        /// <param name="currentX">当前点的X值</param>
        /// <param name="currentY">当前点的Y值</param>
        /// <returns>精灵朝向代号(以北为0顺时针依次1,2,3,4,5,6,7)</returns>
        public static int GetDirection(double targetX, double targetY, double currentX, double currentY)
        {
            double tan = (targetY - currentY) / (targetX - currentX);
            if (Math.Abs(tan) >= Math.Tan(Math.PI * 3 / 8) && targetY <= currentY)
            {
                return 0;
            }
            if (Math.Abs(tan) > Math.Tan(Math.PI / 8) && Math.Abs(tan) < Math.Tan(Math.PI * 3 / 8) && targetX > currentX && targetY < currentY)
            {
                return 1;
            }
            if (Math.Abs(tan) <= Math.Tan(Math.PI / 8) && targetX >= currentX)
            {
                return 2;
            }
            if (Math.Abs(tan) > Math.Tan(Math.PI / 8) && Math.Abs(tan) < Math.Tan(Math.PI * 3 / 8) && targetX > currentX && targetY > currentY)
            {
                return 3;
            }
            if (Math.Abs(tan) >= Math.Tan(Math.PI * 3 / 8) && targetY >= currentY)
            {
                return 4;
            }
            if (Math.Abs(tan) > Math.Tan(Math.PI / 8) && Math.Abs(tan) < Math.Tan(Math.PI * 3 / 8) && targetX < currentX && targetY > currentY)
            {
                return 5;
            }
            if (Math.Abs(tan) <= Math.Tan(Math.PI / 8) && targetX <= currentX)
            {
                return 6;
            }
            if (Math.Abs(tan) > Math.Tan(Math.PI / 8) && Math.Abs(tan) < Math.Tan(Math.PI * 3 / 8) && targetX < currentX && targetY < currentY)
            {
                return 7;
            }
            return 0;
        }

        /// <summary>
        /// 计算出动画时间花费
        /// </summary>
        public static double GetAnimationTimeConsuming(Point start, Point end, int zoomX, int zoomY, double unitCost)
        {
            return Math.Sqrt(Math.Pow((end.X - start.X) / zoomX, 2) + Math.Pow((end.Y - start.Y) / zoomY, 2)) * unitCost;
        }

        /// <summary>
        /// 寻路模式中根据单元格方向来判断精灵朝向
        /// </summary>
        /// <param name="targetX">目标点的X值</param>
        /// <param name="targetY">目标点的Y值</param>
        /// <param name="currentX">当前点的X值</param>
        /// <param name="currentY">当前点的Y值</param>
        /// <returns>精灵朝向代号(以北为0顺时针依次1,2,3,4,5,6,7)</returns>
        public static double GetDirectionByGrid(int targetX, int targetY, int currentX, int currentY)
        {
            int direction = 2;
            if (targetX < currentX)
            {
                if (targetY < currentY)
                {
                    direction = 7;
                }
                else if (targetY == currentY)
                {
                    direction = 6;
                }
                else if (targetY > currentY)
                {
                    direction = 5;
                }
            }
            else if (targetX == currentX)
            {
                if (targetY < currentY)
                {
                    direction = 0;
                }
                else if (targetY > currentY)
                {
                    direction = 4;
                }
            }
            else if (targetX > currentX)
            {
                if (targetY < currentY)
                {
                    direction = 1;
                }
                else if (targetY == currentY)
                {
                    direction = 2;
                }
                else if (targetY > currentY)
                {
                    direction = 3;
                }
            }
            return direction;
        }
    }
}

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
using Radiance.Game.Enumeration;

namespace Radiance.Game.Model
{
    public class ObjectPart
    {
        /// <summary>
        /// 部件类型
        /// </summary>
        public ObjectPartType Type { get; set; }
        
        /// <summary>
        /// 调整到图片中心后相对左上角偏移量
        /// </summary>
        public Point CenterOffset { get; set; }

        /// <summary>
        /// 图片文件夹代号
        /// </summary>
        public int PartCode { get; set; }

        public ObjectPart(ObjectPartType partType,int partCode, Point centerOffset=new Point())
        {
            Type = partType;
            PartCode = partCode;
            CenterOffset = centerOffset;
        }
    }
}

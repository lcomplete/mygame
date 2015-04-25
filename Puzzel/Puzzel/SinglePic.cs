using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Text;
using System.Windows.Forms;

namespace Puzzel
{
    class SinglePic : UserControl
    {
        public SinglePic(Rectangle picRect,Image sourcePic)
        {
            InitializeComponent();
            this.Size = picRect.Size;
            this.picRect = picRect;
            this.sourcePic = sourcePic;
            this.Enabled = false;
        }
        /// <summary>
        /// 图片显示区域
        /// </summary>
        private Rectangle picRect;
        /// <summary>
        /// 图片源
        /// </summary>
        private Image sourcePic;

        private int number;
        public int Number
        {
            get { return number; }
            set { number = value; }
        }


        private void InitializeComponent()
        {
            this.SuspendLayout();
            this.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.ResumeLayout(false);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            Graphics g = e.Graphics;
            g.DrawImage(sourcePic, ClientRectangle, picRect, GraphicsUnit.Pixel);
        }
    }
}

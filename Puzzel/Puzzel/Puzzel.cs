using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.IO;

namespace Puzzel
{
    public partial class Puzzel : Form
    {
        public Puzzel()
        {
            InitializeComponent();
        }
        private int iRows,iCols;
        private Size onePicSize;
        private Point nullPosition;
        private SinglePic[,] arrPic;
        private int confusionNum;
        private Image bigImg;
        private bool success;
        private DateTime startime;
        private DateTime endtime;
        private int boundary=150;

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            Init(Properties.Resources.bingxin, 3, 3);
        }

        protected override void OnMouseClick(MouseEventArgs e)
        {
            base.OnMouseClick(e);
            if (success)
                return;
            Point mousePt = e.Location;
            if (mousePt.X > boundary)
            {
                Point movePt = new Point((mousePt.X - boundary) / (PicPanel.Width / iCols), mousePt.Y / (PicPanel.Height / iRows));
                int x = movePt.X;
                int y = movePt.Y;
                if (x == nullPosition.X)
                {
                    if (y > nullPosition.Y)
                    {
                        for (int i = nullPosition.Y + 1; i <= y; i++)
                            MoveTile(x, i);
                    }
                    else if (y < nullPosition.Y)
                    {
                        for (int i = nullPosition.Y - 1; i >= y; i--)
                            MoveTile(x, i);
                    }
                }
                else if (y == nullPosition.Y)
                {
                    if (x > nullPosition.X)
                    {
                        for (int i = nullPosition.X + 1; i <= x; i++)
                            MoveTile(i, y);
                    }
                    else if (x < nullPosition.X)
                    {
                        for (int i = nullPosition.X - 1; i >= x; i--)
                            MoveTile(i, y);
                    }
                }
                if (arrPic[iRows - 1, iCols - 1] == null)//最后一张图为null时 判断是否拼完
                {
                    CheckComplete();
                    if (success)
                    {
                        ClearPicArray();
                        bigImg.Dispose();
                    }
                }
            }
            else if (PicFileDialog.ShowDialog() == DialogResult.OK)
            {

                try
                {
                    Image img = Image.FromFile(PicFileDialog.FileName);
                    if (!success)
                    {
                        ClearPicArray();//一盘还未结束时销毁图片
                        bigImg.Dispose();
                    }
                    else
                    {
                        success = false;//重新开始一局
                        iRows++;
                        iCols++;
                        Invalidate();//擦除过关信息
                    }
                    Init(img, iRows, iCols);
                }
                catch
                {
                    MessageBox.Show("Wrong File Mode.");
                }
            }
        }

        void Init(Image sourceImg,int irows, int icols)
        {
            if (irows < 3 && icols < 3)
                return;
            PicPanel.Visible = true;
            bigImg = sourceImg;
            Size imgSize = bigImg.Size;
            iRows = irows;
            iCols = icols;
            confusionNum = iRows * iCols * iRows*iCols*2;//随机移动的次数
            arrPic = new SinglePic[iRows, iCols];
            MaximumSize = new Size(imgSize.Width+boundary + SystemInformation.BorderSize.Width * 2, imgSize.Height + SystemInformation.CaptionHeight);
            MinimumSize = MaximumSize;
            ClientSize =new Size(imgSize.Width+boundary,imgSize.Height);
            PicPanel.Location = new Point(boundary, 0);
            PicPanel.Size = imgSize;
            PicPanel.Enabled = false;
            onePicSize = new Size(imgSize.Width / iCols, imgSize.Height / iRows);
            for (int i = 0; i < iRows; i++)//按顺序分配图片
            {
                for (int j = 0; j < iCols; j++)
                {
                    if ((i + 1) * (j + 1) == iRows * iCols)
                        continue;
                    Rectangle singPicRect = new Rectangle(new Point(j * onePicSize.Width, i * onePicSize.Height), onePicSize);
                    SinglePic singlePic = new SinglePic(singPicRect, bigImg);
                    singlePic.Location = singPicRect.Location;
                    singlePic.Parent = PicPanel;
                    singlePic.Number = i * iCols + j + 1;
                    arrPic[i, j] = singlePic;
                }
            }
            nullPosition = new Point(iCols - 1, iRows - 1);
            this.KeyDown -= new KeyEventHandler(KeyDownHandler);//初始化时 去除按键事件 图片随机移动完成后添加
            Timer timer = new Timer();
            timer.Interval = 1;
            timer.Tick += new EventHandler(Confusion);
            timer.Start();
        }
        /// <summary>
        /// 在右上角显示缩略图
        /// </summary>
        void MakeThumber()
        {
            using (Graphics g = CreateGraphics())
            {
                float scale=(float)boundary/bigImg.Width;
                float h=scale*bigImg.Height;
                g.DrawImage(bigImg, 0, 0, 150, h);
            }
        }

        void Confusion(object sender,EventArgs e)
        {
            Random rnd = new Random();
            int direction = rnd.Next(4);
            int x = nullPosition.X;
            int y = nullPosition.Y;
            switch (direction)
            {
                case 0:
                    if (x + 1 != iCols)
                        MoveTile(x + 1, y);
                    break;
                case 1:
                    if (x != 0)
                        MoveTile(x - 1, y);
                    break;
                case 2:
                    if (y + 1 != iRows)
                        MoveTile(x, y + 1);
                    break;
                case 3:
                    if (y != 0)
                        MoveTile(x, y - 1);
                    break;
            }
            if (--confusionNum == 0)
            {
                Timer timer = (Timer)sender;
                timer.Stop();
                startime = DateTime.Now;//设置开始时间
                timer.Tick -= new EventHandler(Confusion);
                this.KeyDown += new KeyEventHandler(KeyDownHandler);//图片随机移动完成后 添加事件
            }
        }
        /// <summary>
        /// 移动小图
        /// </summary>
        /// <param name="x">列</param>
        /// <param name="y">行</param>
        void MoveTile(int x, int y)
        {
            int nullx = nullPosition.X;
            int nully = nullPosition.Y;
            arrPic[y, x].Location = new Point(nullx * onePicSize.Width, nully * onePicSize.Height);//图片移到空位置
            arrPic[nully, nullx] = arrPic[y, x];//空位置引用图片
            nullPosition = new Point(x,y);
            arrPic[y, x] = null;//原位置设置为空
        }

        void KeyDownHandler(object sender,KeyEventArgs e)
        {
            //press any key to continue
            if (success)
            {
                success = false;
                Invalidate();//擦除过关信息
                switch (iRows % 3)//初始化下一关
                {
                    case 0:
                        Init(Properties.Resources.mudu, ++iRows, ++iCols);
                        break;
                    case 1:
                        Init(Properties.Resources.yangqiu, ++iRows, ++iCols);
                        break;
                    case 2:
                        Init(Properties.Resources.bingxin, ++iRows, ++iCols);
                        break;
                }
                return;
            }
            else if(e.KeyCode==Keys.Escape)//重新开始
            {
                ClearPicArray();//清除小图 但不销毁大图
                Init(bigImg, iRows, iCols);
                return;
            }
            int x=nullPosition.X;
            int y=nullPosition.Y;
            switch (e.KeyCode)
            {
                case Keys.Left:
                    if (x + 1 != iCols)
                        MoveTile(x + 1, y);
                    break;
                case Keys.Right:
                    if (x != 0)
                        MoveTile(x - 1, y);
                    break;
                case Keys.Up:
                    if (y + 1 != iRows)
                        MoveTile(x, y + 1);
                    break;
                case Keys.Down:
                    if (y != 0)
                        MoveTile(x, y - 1);
                    break;
            }
            if (arrPic[iRows - 1, iCols - 1] == null)//最后一涨图为null时 判断是否拼完
            {
                CheckComplete();
                if (success)
                {
                    ClearPicArray();
                    bigImg.Dispose();
                }
            }
        }
        /// <summary>
        /// 检查是否完成拼图 是则将success 设置为true
        /// </summary>
        void CheckComplete()
        {
            for (int i = 0; i < iRows; i++)
            {
                for (int j = 0; j < iCols; j++)
                {
                    if ((i + 1) * (j + 1) == iRows * iCols)
                        continue;
                    if (arrPic[i, j].Number != i * iCols + j + 1)
                    {
                        return;
                    }
                }
            }
            endtime = DateTime.Now;//设置结束时间
            success = true;
        }
        /// <summary>
        /// 释放小图
        /// </summary>
        void ClearPicArray()
        {
            for (int i = 0; i < iRows; i++)
            {
                for (int j = 0; j < iCols; j++)
                {
                    if (arrPic[i, j] == null)
                        continue;
                    arrPic[i, j].Dispose();
                }
            }
            arrPic = null;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            Graphics g = e.Graphics;
            if (!success)//未成功时 显示缩略图
            {
                g.Clear(BackColor);
                MakeThumber();
            }
            else//成功时 显示过关信息 图片已隐藏
            {
                PicPanel.Visible = false;
                g.FillRectangle(new SolidBrush(BackColor), ClientRectangle);
                TimeSpan ts = endtime - startime;
                double isecond = ts.TotalSeconds;
                string sSuccess = "Congratulations!\nYou are winner,\nbut you spend " +
                    isecond.ToString() + " second.\nMake determined and persistent efforts.\nPress any key to continue.";
                SizeF strSize = g.MeasureString(sSuccess, Font);
                float iscale = Math.Min(ClientRectangle.Width / strSize.Width, ClientRectangle.Height / strSize.Height);
                StringFormat sf = new StringFormat();
                sf.LineAlignment = sf.Alignment |= StringAlignment.Center;
                g.DrawString(sSuccess, new Font(Font.FontFamily, iscale * Font.SizeInPoints), Brushes.White, ClientRectangle, sf);
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            bigImg.Dispose();
        }
    }
}

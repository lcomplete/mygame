using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Forms;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using MessageBox = System.Windows.MessageBox;
using Path = System.IO.Path;

namespace RPGViewerHelper
{
    /// <summary>
    /// MainWindow.xaml 的交互逻辑
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void btnBuild_Click(object sender, RoutedEventArgs e)
        {
            if(!Directory.Exists(txtSourcePath.Text))
            {
                MessageBox.Show("源文件夹不存在");
            }
            else if(string.IsNullOrWhiteSpace(txtTargetPath.Text))
            {
                System.Windows.Forms.MessageBox.Show("请输入目标路径");
            }
            else
            {
                string[] fileNames= Directory.GetFiles(txtSourcePath.Text, "*.png");
                if (fileNames.Length == 0)
                {
                    MessageBox.Show("源文件夹中没有文件");
                }
                else
                {
                    if(!Directory.Exists(txtTargetPath.Text))
                    {
                        Directory.CreateDirectory(txtTargetPath.Text);
                    }
                    int successCount = 0;
                    int offsetX, offsetY;
                    int.TryParse(txtOffsetX.Text,out offsetX);
                    int.TryParse(txtOffsetY.Text, out offsetY);
                    foreach (var fileName in fileNames)
                    {
                        try
                        {
                            string offsetInfo = File.ReadLines(fileName + ".info.txt").ToList()[1];
                            int[] offsetAndSize = Array.ConvertAll(offsetInfo.Split(','), s => int.Parse(s));
                            int x = offsetAndSize[0],
                                y = offsetAndSize[1],
                                width = offsetAndSize[2],
                                height = offsetAndSize[3];

                            BitmapImage image = new BitmapImage(new Uri(fileName, UriKind.Absolute));
                            using (System.IO.FileStream fileStream = new System.IO.FileStream(txtTargetPath.Text +"\\"+ Path.GetFileName(fileName),
                                                                                              System.IO.FileMode.Create))
                            {
                                DrawingVisual drawingVisual = new DrawingVisual();
                                DrawingContext drawingContext = drawingVisual.RenderOpen();

                                drawingContext.DrawImage(image, new Rect(0, 0, image.Width, image.Height));
                                drawingVisual.Offset = new Vector(x+offsetX, y+offsetY);
                                drawingContext.Close();

                                RenderTargetBitmap renderTargetBitmap = new RenderTargetBitmap(width, height, 0, 0,
                                                                                               PixelFormats.Pbgra32);
                                renderTargetBitmap.Render(drawingVisual);
                                PngBitmapEncoder encoder = new PngBitmapEncoder();
                                encoder.Frames.Add(BitmapFrame.Create(renderTargetBitmap));
                                encoder.Save(fileStream);
                            }
                            successCount++;
                        }
                        catch(Exception ex)
                        {
                            txtOutput.Text = ex.ToString();
                            return;
                        }
                    }
                    txtOutput.Text = string.Format("生成成功，一共生成{0}个文件", successCount.ToString());
                }
            }
        }

        private void btnSelectDirectory_Click(object sender, RoutedEventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog=new FolderBrowserDialog()
                                                        {
                                                            Description = "请选择图片所在文件夹",
                                                            ShowNewFolderButton = true
                                                        };
            folderBrowserDialog.Disposed += new EventHandler(folderBrowserDialog_Disposed);
            folderBrowserDialog.ShowDialog();
            folderBrowserDialog.Dispose();
        }

        private void folderBrowserDialog_Disposed(object sender, EventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog = sender as FolderBrowserDialog;
            txtSourcePath.Text = folderBrowserDialog.SelectedPath;
        }

        private void btnBrowerTartgetPath_Click(object sender, RoutedEventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog = new FolderBrowserDialog()
            {
                Description = "请选择图片输出文件夹",
                ShowNewFolderButton = true
            };
            folderBrowserDialog.Disposed += new EventHandler(folderBrowserTargetPathDialog_Disposed);
            folderBrowserDialog.ShowDialog();
            folderBrowserDialog.Dispose();
        }

        private void folderBrowserTargetPathDialog_Disposed(object sender, EventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog = sender as FolderBrowserDialog;
            txtTargetPath.Text = folderBrowserDialog.SelectedPath;
        }
    }
}

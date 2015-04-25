using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Resources;
using System.Windows.Shapes;
using Radiance.Game.Enumeration;
using Radiance.Game.Objects;

namespace Radiance.Game.Common
{
    public sealed class ImageUtils
    {

        public static BitmapSource GetImageSource(Uri uri,bool isResource=false)
        {
            if (!isResource)
            {
                return new BitmapImage(uri);
            }
            StreamResourceInfo resourceInfo = Application.GetResourceStream(uri);
            BitmapImage bitmapImage = new BitmapImage();
            if (resourceInfo != null && resourceInfo.Stream != null)
            {
                bitmapImage.SetSource(resourceInfo.Stream);
            }
            return bitmapImage;
        }

        public static BitmapSource GetRelativeImage(string uri,bool isResource=false)
        {
            return GetImageSource(new Uri(uri, UriKind.Relative), isResource);
        }

        /// <summary>
        /// 获取被生成为Resource的png图片大小 
        /// </summary>
        /// <param name="uri"></param>
        /// <returns></returns>
        public static Size GetPNGSize(Uri uri)
        {
            StreamResourceInfo resourceInfo = Application.GetResourceStream(uri);

            if (resourceInfo!=null && resourceInfo.Stream!=null)
            {
                try
                {
                    byte[] header = new byte[8];
                    resourceInfo.Stream.Read(header, 0, header.Length);
                    if (header[0] == 0x89 &&
                        header[1] == 0x50 && // P
                        header[2] == 0x4E && // N
                        header[3] == 0x47 && // G
                        header[4] == 0x0D && // CR
                        header[5] == 0x0A && // LF
                        header[6] == 0x1A && // EOF
                        header[7] == 0x0A) // LF
                    {
                        byte[] buffer = new byte[16];
                        resourceInfo.Stream.Read(buffer, 0, buffer.Length);
                        Array.Reverse(buffer, 8, 4);
                        Array.Reverse(buffer, 12, 4);

                        double width = BitConverter.ToInt32(buffer, 8);
                        double height = BitConverter.ToInt32(buffer, 12);
                        return new Size(width, height);
                    }
                }
                catch
                {
                    //ignore
                }
                finally
                {
                    resourceInfo.Stream.Close();
                }
            }

            return new Size();
        }

    }
}

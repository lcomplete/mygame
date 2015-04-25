using System;
using System.Collections.Generic;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using Radiance.Game.Common;
using Radiance.Game.Enumeration;
using Radiance.Game.Model;
using Radiance.Game.Objects;
using System.Linq;

namespace Radiance.Game.Resolver
{
    public class FrameResolver
    {
        public DynamicalObject DynamicalObject { get; set; }

        protected bool IsResource { get; set; }

        public FrameResolver()
        {
            this.IsResource = true;
        }

        public WriteableBitmap ResolveCurrentFrame()
        {
            WriteableBitmap writeableBitmap = new WriteableBitmap((int)DynamicalObject.SingleWidth,(int)DynamicalObject.SingleHeight);
            foreach (var objectPart in ReOrderObjectParts())
            {
                BitmapSource source = GetPartImageSource(objectPart);
                var image = new Image() {Source = source};
                var transform = GetTransform(source, objectPart);
                writeableBitmap.Render(image, transform);
            }
            writeableBitmap.Invalidate();
            return writeableBitmap;
        }

        protected virtual IList<ObjectPart> ReOrderObjectParts()
        {
            return DynamicalObject.ObjectParts;
        }

        protected virtual Transform GetTransform(BitmapSource source, ObjectPart objectPart)
        {
            return new TranslateTransform()
            {
                X = (int)((DynamicalObject.SingleWidth - source.PixelWidth)/2) + objectPart.CenterOffset.X,
                Y = (int)((DynamicalObject.SingleHeight - source.PixelHeight)/2) + objectPart.CenterOffset.Y
            };
        }

        private BitmapSource GetPartImageSource(ObjectPart objectPart)
        {
            Uri uri = new Uri((IsResource ? "/Radiance.game;component" : string.Empty) + GetPartImageAddress(objectPart),UriKind.Relative);
            return ImageUtils.GetImageSource(uri, IsResource);
        }

        protected virtual string GetPartImageAddress(ObjectPart objectPart)
        {
            string address = string.Format("/Resources/ObjectParts/{0}/{1}/{2}/{3}.png", objectPart.Type.ToString(),
                                           DynamicalObject.Action.ToString(), objectPart.PartCode.ToString(),
                                           GetPartImageIndex().ToString()
                                           );
            return address;
        }

        protected virtual int GetPartImageIndex()
        {
            return DynamicalObject.CurrentFrameCount*DynamicalObject.Direction + DynamicalObject.CurrentFrameIndex;
        }
    }
}

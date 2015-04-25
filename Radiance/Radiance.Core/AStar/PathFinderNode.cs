using System.Runtime.InteropServices;

namespace Radiance.Core.AStar
{
    [StructLayout(LayoutKind.Sequential), Author("QX")]
    public struct PathFinderNode
    {
        public int F;
        public int G;
        public int H;
        public int X;
        public int Y;
        public int PX;
        public int PY;
    }
}


namespace Radiance.Core.AStar
{
    [Author("QX")]
    public enum PathFinderNodeType
    {
        Close = 8,
        Current = 0x10,
        End = 2,
        Open = 4,
        Path = 0x20,
        Start = 1
    }
}


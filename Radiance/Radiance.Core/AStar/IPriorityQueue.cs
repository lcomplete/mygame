namespace Radiance.Core.AStar
{
    [Author("QX")]
    public interface IPriorityQueue<T>
    {
        T Peek();
        T Pop();
        int Push(T item);
        void Update(int i);
    }
}


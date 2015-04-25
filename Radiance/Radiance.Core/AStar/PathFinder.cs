using System;
using System.Collections.Generic;
using System.Windows;

namespace Radiance.Core.AStar
{
    [Author("QX")]
    public class PathFinder : IPathFinder
    {
        private List<PathFinderNode> mClose = new List<PathFinderNode>();
        private bool mDiagonals = true;
        private HeuristicFormula mFormula = HeuristicFormula.Manhattan;
        private byte[,] mGrid = null;
        private bool mHeavyDiagonals = false;
        private int mHEstimate = 2;
        private PriorityQueueB<PathFinderNode> mOpen = new PriorityQueueB<PathFinderNode>(new ComparePFNode());
        private int mSearchLimit = 0x7d0;
        private bool mStop = false;
        private bool mStopped = true;
        private bool mTieBreaker = false;

        public PathFinder(byte[,] grid)
        {
            if (grid == null) throw new Exception("Grid cannot be null");
            this.mGrid = grid;
        }

        public List<PathFinderNode> FindPath(Point start, Point end)
        {
            PathFinderNode node;
            sbyte[,] numArray;
            int num3;
            bool flag = false;
            int upperBound = this.mGrid.GetUpperBound(0);
            int num2 = this.mGrid.GetUpperBound(1);
            this.mStop = false;
            this.mStopped = false;
            this.mOpen.Clear();
            this.mClose.Clear();
            if (this.mDiagonals)
                numArray = new sbyte[,] { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 }, { 1, -1 }, { 1, 1 }, { -1, 1 }, { -1, -1 } };
            else
                numArray = new sbyte[,] { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 } };
            node.G = 0;
            node.H = this.mHEstimate;
            node.F = node.G + node.H;
            node.X = (int) start.X;
            node.Y = (int) start.Y;
            node.PX = node.X;
            node.PY = node.Y;
            this.mOpen.Push(node);
            while (this.mOpen.Count > 0 && !this.mStop)
            {
                node = this.mOpen.Pop();
                if (node.X == end.X && node.Y == end.Y)
                {
                    this.mClose.Add(node);
                    flag = true;
                    break;
                }
                if (this.mClose.Count > this.mSearchLimit)
                {
                    this.mStopped = true;
                    return null;
                }
                num3 = 0;
                while (num3 < (this.mDiagonals ? 8 : 4))
                {
                    PathFinderNode node2;
                    node2.X = node.X + numArray[num3, 0];
                    node2.Y = node.Y + numArray[num3, 1];
                    if (node2.X >= 0 && node2.Y >= 0 && node2.X < upperBound && node2.Y < num2)
                    {
                        int num4;
                        if (this.mHeavyDiagonals && num3 > 3)
                            num4 = node.G + ((int) (this.mGrid[node2.X, node2.Y] * 2.41));
                        else
                            num4 = node.G + this.mGrid[node2.X, node2.Y];
                        if (num4 != node.G)
                        {
                            int num5 = -1;
                            int num6 = 0;
                            while (num6 < this.mOpen.Count)
                            {
                                if (this.mOpen[num6].X == node2.X && this.mOpen[num6].Y == node2.Y)
                                {
                                    num5 = num6;
                                    break;
                                }
                                num6++;
                            }
                            if (num5 == -1 || this.mOpen[num5].G > num4)
                            {
                                int num7 = -1;
                                for (num6 = 0; num6 < this.mClose.Count; num6++)
                                {
                                    if (this.mClose[num6].X == node2.X && this.mClose[num6].Y == node2.Y)
                                    {
                                        num7 = num6;
                                        break;
                                    }
                                }
                                if (num7 == -1 || this.mClose[num7].G > num4)
                                {
                                    node2.PX = node.X;
                                    node2.PY = node.Y;
                                    node2.G = num4;
                                    switch (this.mFormula)
                                    {
                                        case HeuristicFormula.MaxDXDY:
                                            node2.H = this.mHEstimate * Math.Max(Math.Abs((int) (node2.X - ((int) end.X))), Math.Abs((int) (node2.Y - ((int) end.Y))));
                                            break;

                                        case HeuristicFormula.DiagonalShortCut:
                                        {
                                            int num8 = Math.Min(Math.Abs((int) (node2.X - ((int) end.X))), Math.Abs((int) (node2.Y - ((int) end.Y))));
                                            int num9 = Math.Abs((int) (node2.X - ((int) end.X))) + Math.Abs((int) (node2.Y - ((int) end.Y)));
                                            node2.H = this.mHEstimate * 2 * num8 + this.mHEstimate * (num9 - 2 * num8);
                                            break;
                                        }
                                        case HeuristicFormula.Euclidean:
                                            node2.H = (int) (this.mHEstimate * Math.Sqrt(Math.Pow(node2.X - end.X, 2.0) + Math.Pow(node2.Y - end.Y, 2.0)));
                                            break;

                                        case HeuristicFormula.EuclideanNoSQR:
                                            node2.H = (int) (this.mHEstimate * (Math.Pow(node2.X - end.X, 2.0) + Math.Pow(node2.Y - end.Y, 2.0)));
                                            break;

                                        case HeuristicFormula.Custom1:
                                        {
                                            Point point = new Point(Math.Abs((double) (end.X - node2.X)), Math.Abs((double) (end.Y - node2.Y)));
                                            int num10 = Math.Abs((int) (((int) point.X) - ((int) point.Y)));
                                            int num11 = Math.Abs((int) ((((int) point.X) + ((int) point.Y) - num10) / 2));
                                            node2.H = this.mHEstimate * (num11 + num10 + (int) point.X + (int) point.Y);
                                            break;
                                        }
                                        default:
                                            node2.H = this.mHEstimate * (Math.Abs((int) (node2.X - ((int) end.X))) + Math.Abs((int) (node2.Y - ((int) end.Y))));
                                            break;
                                    }
                                    if (this.mTieBreaker)
                                    {
                                        int num12 = node.X - ((int) end.X);
                                        int num13 = node.Y - ((int) end.Y);
                                        int num14 = ((int) start.X) - ((int) end.X);
                                        int num15 = ((int) start.Y) - ((int) end.Y);
                                        int num16 = Math.Abs((int) (num12 * num15 - num14 * num13));
                                        node2.H += (int) (num16 * 0.001);
                                    }
                                    node2.F = node2.G + node2.H;
                                    this.mOpen.Push(node2);
                                }
                            }
                        }
                    }
                    num3++;
                }
                this.mClose.Add(node);
            }
            if (flag)
            {
                PathFinderNode node3 = this.mClose[this.mClose.Count - 1];
                for (num3 = this.mClose.Count - 1; num3 >= 0; num3--)
                {
                    if (node3.PX == this.mClose[num3].X && node3.PY == this.mClose[num3].Y || num3 == this.mClose.Count - 1)
                        node3 = this.mClose[num3];
                    else
                        this.mClose.RemoveAt(num3);
                }
                this.mStopped = true;
                return this.mClose;
            }
            this.mStopped = true;
            return null;
        }

        public void FindPathStop()
        {
            this.mStop = true;
        }

        public bool Diagonals
        {
            get
            {
                return this.mDiagonals;
            }
            set
            {
                this.mDiagonals = value;
            }
        }

        public HeuristicFormula Formula
        {
            get
            {
                return this.mFormula;
            }
            set
            {
                this.mFormula = value;
            }
        }

        public bool HeavyDiagonals
        {
            get
            {
                return this.mHeavyDiagonals;
            }
            set
            {
                this.mHeavyDiagonals = value;
            }
        }

        public int HeuristicEstimate
        {
            get
            {
                return this.mHEstimate;
            }
            set
            {
                this.mHEstimate = value;
            }
        }

        public int SearchLimit
        {
            get
            {
                return this.mSearchLimit;
            }
            set
            {
                this.mSearchLimit = value;
            }
        }

        public bool Stopped
        {
            get
            {
                return this.mStopped;
            }
        }

        public bool TieBreaker
        {
            get
            {
                return this.mTieBreaker;
            }
            set
            {
                this.mTieBreaker = value;
            }
        }

        [Author("QX")]
        internal class ComparePFNode : IComparer<PathFinderNode>
        {
            public int Compare(PathFinderNode x, PathFinderNode y)
            {
                if (x.F > y.F) return 1;
                if (x.F < y.F) return -1;
                return 0;
            }
        }
    }
}


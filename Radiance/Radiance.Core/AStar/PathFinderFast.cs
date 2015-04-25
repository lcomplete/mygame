using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows;

namespace Radiance.Core.AStar
{
    [Author("QX")]
    public class PathFinderFast : IPathFinder
    {
        private PathFinderNodeFast[] mCalcGrid = null;
        private List<PathFinderNode> mClose = new List<PathFinderNode>();
        private int mCloseNodeCounter = 0;
        private byte mCloseNodeValue = 2;
        private bool mDiagonals = true;
        private sbyte[,] mDirection = new sbyte[,] { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 }, { 1, -1 }, { 1, 1 }, { -1, 1 }, { -1, -1 } };
        private int mEndLocation = 0;
        private HeuristicFormula mFormula = HeuristicFormula.Manhattan;
        private bool mFound = false;
        private byte[,] mGrid = null;
        private ushort mGridX = 0;
        private ushort mGridXMinus1 = 0;
        private ushort mGridY = 0;
        private ushort mGridYLog2 = 0;
        private int mH = 0;
        private bool mHeavyDiagonals = false;
        private int mHEstimate = 2;
        private int mLocation = 0;
        private ushort mLocationX = 0;
        private ushort mLocationY = 0;
        private int mNewG = 0;
        private int mNewLocation = 0;
        private ushort mNewLocationX = 0;
        private ushort mNewLocationY = 0;
        private PriorityQueueB<Int32> mOpen = null;
        private byte mOpenNodeValue = 1;
        private int mSearchLimit = 0x7d0;
        private bool mStop = false;
        private bool mStopped = true;
        private bool mTieBreaker = false;

        public PathFinderFast(byte[,] grid)
        {
            if (grid == null) throw new Exception("Grid cannot be null");
            this.mGrid = grid;
            this.mGridX = (ushort) (this.mGrid.GetUpperBound(0) + 1);
            this.mGridY = (ushort) (this.mGrid.GetUpperBound(1) + 1);
            this.mGridXMinus1 = (ushort) (this.mGridX - 1);
            this.mGridYLog2 = (ushort) Math.Log((double) this.mGridY, 2.0);
            if (Math.Log((double) this.mGridX, 2.0) != ((int) Math.Log((double) this.mGridX, 2.0)) || Math.Log((double) this.mGridY, 2.0) != ((int) Math.Log((double) this.mGridY, 2.0))) throw new Exception("Invalid Grid, size in X and Y must be power of 2");
            if (this.mCalcGrid == null || this.mCalcGrid.Length != this.mGridX * this.mGridY) this.mCalcGrid = new PathFinderNodeFast[this.mGridX * this.mGridY];
            this.mOpen = new PriorityQueueB<Int32>(new ComparePFNodeMatrix(this.mCalcGrid));
        }

        public List<PathFinderNode> FindPath(Point start, Point end)
        {
            lock (this)
            {
                this.mFound = false;
                this.mStop = false;
                this.mStopped = false;
                this.mCloseNodeCounter = 0;
                this.mOpenNodeValue = (byte) (this.mOpenNodeValue + 2);
                this.mCloseNodeValue = (byte) (this.mCloseNodeValue + 2);
                this.mOpen.Clear();
                this.mClose.Clear();
                this.mLocation = (((int) start.Y) << this.mGridYLog2) + ((int) start.X);
                this.mEndLocation = (((int) end.Y) << this.mGridYLog2) + ((int) end.X);
                this.mCalcGrid[this.mLocation].G = 0;
                this.mCalcGrid[this.mLocation].F = this.mHEstimate;
                this.mCalcGrid[this.mLocation].PX = (ushort) start.X;
                this.mCalcGrid[this.mLocation].PY = (ushort) start.Y;
                this.mCalcGrid[this.mLocation].Status = this.mOpenNodeValue;
                this.mOpen.Push(this.mLocation);
                while (this.mOpen.Count > 0 && !this.mStop)
                {
                    this.mLocation = this.mOpen.Pop();
                    if (this.mCalcGrid[this.mLocation].Status != this.mCloseNodeValue)
                    {
                        this.mLocationX = (ushort) (this.mLocation & this.mGridXMinus1);
                        this.mLocationY = (ushort) (this.mLocation >> this.mGridYLog2);
                        if (this.mLocation == this.mEndLocation)
                        {
                            this.mCalcGrid[this.mLocation].Status = this.mCloseNodeValue;
                            this.mFound = true;
                            break;
                        }
                        if (this.mCloseNodeCounter > this.mSearchLimit)
                        {
                            this.mStopped = true;
                            return null;
                        }
                        for (int i = 0; i < (this.mDiagonals ? 8 : 4); i++)
                        {
                            this.mNewLocationX = (ushort) (this.mLocationX + this.mDirection[i, 0]);
                            this.mNewLocationY = (ushort) (this.mLocationY + this.mDirection[i, 1]);
                            this.mNewLocation = (this.mNewLocationY << this.mGridYLog2) + this.mNewLocationX;
                            if (this.mNewLocationX < this.mGridX && this.mNewLocationY < this.mGridY && this.mGrid[this.mNewLocationX, this.mNewLocationY] != 0)
                            {
                                if (this.mHeavyDiagonals && i > 3)
                                    this.mNewG = this.mCalcGrid[this.mLocation].G + ((int) (this.mGrid[this.mNewLocationX, this.mNewLocationY] * 2.41));
                                else
                                    this.mNewG = this.mCalcGrid[this.mLocation].G + this.mGrid[this.mNewLocationX, this.mNewLocationY];
                                if (this.mCalcGrid[this.mNewLocation].Status != this.mOpenNodeValue && this.mCalcGrid[this.mNewLocation].Status != this.mCloseNodeValue || this.mCalcGrid[this.mNewLocation].G > this.mNewG)
                                {
                                    this.mCalcGrid[this.mNewLocation].PX = this.mLocationX;
                                    this.mCalcGrid[this.mNewLocation].PY = this.mLocationY;
                                    this.mCalcGrid[this.mNewLocation].G = this.mNewG;
                                    switch (this.mFormula)
                                    {
                                        case HeuristicFormula.MaxDXDY:
                                            this.mH = this.mHEstimate * Math.Max(Math.Abs((int) (this.mNewLocationX - ((int) end.X))), Math.Abs((int) (this.mNewLocationY - ((int) end.Y))));
                                            break;

                                        case HeuristicFormula.DiagonalShortCut:
                                        {
                                            int num2 = Math.Min(Math.Abs((int) (this.mNewLocationX - ((int) end.X))), Math.Abs((int) (this.mNewLocationY - ((int) end.Y))));
                                            int num3 = Math.Abs((int) (this.mNewLocationX - ((int) end.X))) + Math.Abs((int) (this.mNewLocationY - ((int) end.Y)));
                                            this.mH = this.mHEstimate * 2 * num2 + this.mHEstimate * (num3 - 2 * num2);
                                            break;
                                        }
                                        case HeuristicFormula.Euclidean:
                                            this.mH = (int) (this.mHEstimate * Math.Sqrt(Math.Pow(this.mNewLocationY - end.X, 2.0) + Math.Pow(this.mNewLocationY - end.Y, 2.0)));
                                            break;

                                        case HeuristicFormula.EuclideanNoSQR:
                                            this.mH = (int) (this.mHEstimate * (Math.Pow(this.mNewLocationX - end.X, 2.0) + Math.Pow(this.mNewLocationY - end.Y, 2.0)));
                                            break;

                                        case HeuristicFormula.Custom1:
                                        {
                                            Point point = new Point(Math.Abs((double) (end.X - this.mNewLocationX)), Math.Abs((double) (end.Y - this.mNewLocationY)));
                                            int num4 = Math.Abs((int) (((int) point.X) - ((int) point.Y)));
                                            int num5 = Math.Abs((int) ((((int) point.X) + ((int) point.Y) - num4) / 2));
                                            this.mH = this.mHEstimate * (num5 + num4 + (int) point.X + (int) point.Y);
                                            break;
                                        }
                                        default:
                                            this.mH = this.mHEstimate * (Math.Abs((int) (this.mNewLocationX - ((int) end.X))) + Math.Abs((int) (this.mNewLocationY - ((int) end.Y))));
                                            break;
                                    }
                                    if (this.mTieBreaker)
                                    {
                                        int num6 = this.mLocationX - ((int) end.X);
                                        int num7 = this.mLocationY - ((int) end.Y);
                                        int num8 = ((int) start.X) - ((int) end.X);
                                        int num9 = ((int) start.Y) - ((int) end.Y);
                                        int num10 = Math.Abs((int) (num6 * num9 - num8 * num7));
                                        this.mH += (int) (num10 * 0.001);
                                    }
                                    this.mCalcGrid[this.mNewLocation].F = this.mNewG + this.mH;
                                    this.mOpen.Push(this.mNewLocation);
                                    this.mCalcGrid[this.mNewLocation].Status = this.mOpenNodeValue;
                                }
                            }
                        }
                        this.mCloseNodeCounter++;
                        this.mCalcGrid[this.mLocation].Status = this.mCloseNodeValue;
                    }
                }
                if (this.mFound)
                {
                    PathFinderNode node;
                    this.mClose.Clear();
                    int pX = (int) end.X;
                    int pY = (int) end.Y;
                    PathFinderNodeFast fast = this.mCalcGrid[(((int) end.Y) << this.mGridYLog2) + ((int) end.X)];
                    node.F = fast.F;
                    node.G = fast.G;
                    node.H = 0;
                    node.PX = fast.PX;
                    node.PY = fast.PY;
                    node.X = (int) end.X;
                    node.Y = (int) end.Y;
                    while (node.X != node.PX || node.Y != node.PY)
                    {
                        this.mClose.Add(node);
                        pX = node.PX;
                        pY = node.PY;
                        fast = this.mCalcGrid[(pY << this.mGridYLog2) + pX];
                        node.F = fast.F;
                        node.G = fast.G;
                        node.H = 0;
                        node.PX = fast.PX;
                        node.PY = fast.PY;
                        node.X = pX;
                        node.Y = pY;
                    }
                    this.mClose.Add(node);
                    this.mStopped = true;
                    return this.mClose;
                }
                this.mStopped = true;
                return null;
            }
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
                if (this.mDiagonals)
                    this.mDirection = new sbyte[,] { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 }, { 1, -1 }, { 1, 1 }, { -1, 1 }, { -1, -1 } };
                else
                    this.mDirection = new sbyte[,] { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 } };
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
        internal class ComparePFNodeMatrix : IComparer<int>
        {
            private PathFinderFast.PathFinderNodeFast[] mMatrix;

            public ComparePFNodeMatrix(PathFinderFast.PathFinderNodeFast[] matrix)
            {
                this.mMatrix = matrix;
            }

            public int Compare(int a, int b)
            {
                if (this.mMatrix[a].F > this.mMatrix[b].F) return 1;
                if (this.mMatrix[a].F < this.mMatrix[b].F) return -1;
                return 0;
            }
        }

        [StructLayout(LayoutKind.Sequential, Pack=1), Author("QX")]
        internal struct PathFinderNodeFast
        {
            public int F;
            public int G;
            public ushort PX;
            public ushort PY;
            public byte Status;
        }
    }
}


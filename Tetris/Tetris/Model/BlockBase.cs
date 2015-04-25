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
using System.Windows.Shapes;

namespace Tetris.Model
{
    public abstract class BlockBase
    {
        public BlockBase()
        {
            _cellMatrixList = GetDefaultCellMatrixList();
            _currentCellMatrix = _cellMatrixList[_matrixIndex];
            _color = GetDefaultColor();
        }

        //方块矩阵列表
        protected IList<int[,]> _cellMatrixList;
        public IList<int[,]> CellMatrixList { get { return _cellMatrixList; } }

        //当前格子矩阵
        private int[,] _currentCellMatrix;
        private int _matrixIndex=0;
        public int[,] CurrentCellMatrix
        {
            get { return _currentCellMatrix; }
        }

        //颜色
        protected CellColor _color;
        public CellColor Color { get { return _color; } }

        protected abstract IList<int[,]> GetDefaultCellMatrixList();
        protected virtual CellColor GetDefaultColor()
        {
            return CellColor.Cyan;
        }

        //旋转
        public void Rotate()
        {
            _currentCellMatrix = GetRotate();
            _matrixIndex = GetNextMatrixIndex();
        }

        private int GetNextMatrixIndex()
        {
            int nextMatrixIndex = _matrixIndex + 1;
            if (nextMatrixIndex >= _cellMatrixList.Count)
                nextMatrixIndex = 0;
            return nextMatrixIndex;
        }

        public int[,] GetRotate()
        {
            if(_cellMatrixList==null||_cellMatrixList.Count==0)
                throw new Exception("未设置方块矩阵列表");

            return _cellMatrixList[GetNextMatrixIndex()];
        }
    }
}

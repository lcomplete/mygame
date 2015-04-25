using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using System.Windows.Threading;
using Tetris.Model;

namespace Tetris
{
    public class TetrisController:INotifyPropertyChanged
    {
        #region 等级分数相关属性

        private int _score = 0;
        public int Score
        {
            get { return _score; }
            private set
            {
                _score = value;
                OnPropertyChanged("Score");
            }
        }

        private int _removeRowCount = 0;
        public int RemoveRowCount
        {
            get { return _removeRowCount; }
            private set
            {
                _removeRowCount = value;
                OnPropertyChanged("RemoveRowCount");
            }
        }

        private int _level = 1;
        public int Level
        {
            get { return _level; }
            private set
            {
                _level = value;
                OnPropertyChanged("Level");
            }
        }

        public int CurrentSpeed
        {
            get { return _speed - (_level - 1)*_decreaseSpeed; }
        }

        #endregion

        #region 游戏相关属性

        private int _rowsCount = 20;
        private int _colunmsCount = 10;
        private int _speed = 400;
        private int _decreaseSpeed = 20;
        private int _maxLevel = 15;
        private int _blockPointX = 3;
        private int _blockPointY = 0;

        //格子容器 行列结构
        public Cell[,] CellContainer { get; set; }
        //预览方块容器
        public Cell[] NextBlockContainer { get; private set; }

        private IList<BlockBase> _blockList;
        private BlockBase _currentBlock;
        private BlockBase _nextBlock;

        private Random _random;
        public GameStatus GameStatus { get; set; }

        #endregion

        private DispatcherTimer _dispatcher;

        public TetrisController()
        {
            _random=new Random();
            GameStatus = GameStatus.Ready;
            _blockList = GetBlockList();
            AssignCellContainer();

            _dispatcher=new DispatcherTimer();
            _dispatcher.Interval = TimeSpan.FromMilliseconds(_speed);
            _dispatcher.Tick+=new EventHandler(_dispatcher_Tick);

            CreateBlock();
            PaintBlock(0, 0);
        }

        public void _dispatcher_Tick(object sender, EventArgs e)
        {
            MoveBlock(Key.Down);
        }

        public void MoveBlock(Key key)
        {
            if (this.GameStatus != GameStatus.Play)
                return;
            
            int[,] toCellMatrix=_currentBlock.CurrentCellMatrix;
            int offsetX=0, offsetY=0;
            switch (key)
            {
                case Key.Up:
                    toCellMatrix = _currentBlock.GetRotate();
                    break;
                case Key.Down:
                case Key.Space:
                    offsetY = 1;
                    break;
                case Key.Left:
                    offsetX = -1;
                    break;
                case Key.Right:
                    offsetX = 1;
                    break;
            }

            if(key==Key.Space)//空格直接下降到最底部
            {
                while(!IsBoundary(toCellMatrix,offsetX,offsetY))
                {
                    offsetY++;
                }
                RemoveBlock();
                PaintBlock(offsetX,offsetY-1);
            }

            if(!IsBoundary(toCellMatrix,offsetX,offsetY) && key!=Key.Space)
            {
                RemoveBlock();
                if(key==Key.Up)//旋转
                {
                    _currentBlock.Rotate();
                }
                PaintBlock(offsetX,offsetY);
            }
            else if(key==Key.Down ||key==Key.Space) //检测到边界 并且方向为向下
            {
                RemoveRow();//移除可消除的行
                CreateBlock();
                if(this.GameStatus!=GameStatus.Over)
                    PaintBlock(0,0);
            }
        }

        private void RemoveRow()
        {
            int removeRowCount = 0;
            for (int i = 0; i < _rowsCount; i++)
            {
                bool isLine = true;
                for (int j = 0; j < _colunmsCount; j++)
                {
                    if (!CellContainer[i, j].Color.HasValue)
                    {
                        isLine = false;
                    }
                }
                if (isLine)
                {
                    removeRowCount++;
                    for (int j = 0; j < _colunmsCount; j++)
                    {
                        CellContainer[i, j].Color = null;
                        for (int k = i; k > 0; k--)
                        {
                            CellContainer[k, j].Color = CellContainer[k - 1, j].Color;
                        }
                    }
                }
            }

            if (removeRowCount > 0)
            {
                Scoring(removeRowCount);
                UpgradeLevel();
            }
        }

        private void UpgradeLevel()
        {
            Level = Math.Min(_maxLevel, Convert.ToInt32(Math.Sqrt(Score/20d)));
            _dispatcher.Interval = TimeSpan.FromMilliseconds(CurrentSpeed);
        }

        private void Scoring(int removeRowCount)
        {
            RemoveRowCount += removeRowCount;
            switch (removeRowCount)
            {
                case 1:
                    Score += 10;
                    break;
                case 2:
                    Score += 30;
                    break;
                case 3:
                    Score += 60;
                    break;
                case 4:
                    Score += 100;
                    break;
            }
        }

        private bool IsBoundary(int[,] cellMatrix,int offsetX,int offsetY,bool checkAfterRemove=true)
        {
            if(checkAfterRemove)
                RemoveBlock();
            bool isBoundary=false;
            for (int i = 0; i < 4; i++)
            {
                for (int j = 0; j < 4; j++)
                {
                    int globalPointY = i + _blockPointY + offsetY;
                    int globalPointX = j + _blockPointX + offsetX;
                    if (cellMatrix[i, j] == 1 && (globalPointX < 0 || globalPointX >= _colunmsCount ||globalPointY>=_rowsCount || CellContainer[globalPointY, globalPointX].Color.HasValue))
                    {
                        isBoundary= true;
                        break;
                    }
                }
            }
            if(checkAfterRemove)
                PaintBlock(0,0);
            return isBoundary;
        }

        public void GameStart()
        {
            if (GameStatus == GameStatus.Over)
            {
                Clear();
                Level = 1;
                Score = 0;
                RemoveRowCount = 0;
                CreateBlock();
                PaintBlock(0,0);
                _dispatcher.Interval = TimeSpan.FromMilliseconds(_speed);
            }
            this.GameStatus = GameStatus.Play;
            _dispatcher.Start();
        }

        public void GamePause()
        {
            this.GameStatus = GameStatus.Pause;
            _dispatcher.Stop();
        }

        public void Clear()
        {
            for (int i = 0; i < _rowsCount; i++)
            {
                for (int j = 0; j < _colunmsCount; j++)
                {
                    CellContainer[i, j].Color = null;
                }
            }
        }

        private void CreateBlock()
        {
            _blockPointX = 3;
            _blockPointY = 0;
            _currentBlock = _nextBlock ?? GetRandomBlock();
            for (int i = 0; i < _colunmsCount;i++ )
            {
                if(IsBoundary(_currentBlock.CurrentCellMatrix,0,0,false))
                {
                    OnGameOver(EventArgs.Empty);
                    return;
                }
            }
            _nextBlock = GetRandomBlock();
            AssignNextBlockContainer();
        }

        private void RemoveBlock()
        {
            for (int i = 0; i < 4; i++)
            {
                for (int j = 0; j < 4; j++)
                {
                    if(_currentBlock.CurrentCellMatrix[i,j]==1)
                    {
                        CellContainer[_blockPointY + i, _blockPointX + j].Color = null;
                    }
                }
            }
        }

        private void PaintBlock(int offsetX,int offsetY)
        {
            for (int i = 0; i < 4; i++)
            {
                for (int j = 0; j < 4; j++)
                {
                    if(_currentBlock.CurrentCellMatrix[i,j]==1)
                    {
                        Cell cell=CellContainer[_blockPointY + i + offsetY, _blockPointX + j + offsetX];
                        cell.Color = _currentBlock.Color;
                    }
                }
            }
            _blockPointX += offsetX;
            _blockPointY += offsetY;
        }

        //在预览框中分配格子
        private void AssignNextBlockContainer()
        {
            if(NextBlockContainer==null)
                NextBlockContainer=new Cell[4];
            int index = 0;
            for (int i = 0; i < 4; i++)
            {
                for (int j = 0; j < 4; j++)
                {
                    if(_nextBlock.CurrentCellMatrix[i,j]==1)
                    {
                        Cell cell = NextBlockContainer[index];
                        if (cell == null)
                        {
                            cell = new Cell();
                            NextBlockContainer[index] = cell;
                        }
                        cell.Color = _nextBlock.Color;
                        cell.Top = i * cell.rectangle.ActualHeight;
                        cell.Left = j * cell.rectangle.ActualWidth;
                        index++;
                    }
                }
            }
        }

        //在界面上分配隐藏了的格子
        private void AssignCellContainer()
        {
            CellContainer=new Cell[_rowsCount,_colunmsCount];
            for(int i=0;i<_rowsCount;i++)
            {
                for (int j = 0; j < _colunmsCount; j++)
                {
                    Cell cell=new Cell(){Color = null};
                    cell.Top = i*cell.rectangle.ActualHeight;
                    cell.Left = j*cell.rectangle.ActualWidth;
                    CellContainer[i, j] = cell;
                }
            }
        }

        private BlockBase GetRandomBlock()
        {
            return _blockList[_random.Next(0, _blockList.Count)];
        }

        private static IList<BlockBase> GetBlockList()
        {
            return new List<BlockBase>()
                {
                    new BlockI(),
                    new BlockL(),
                    new BlockL2(),
                    new BlockN(),
                    new BlockN2(),
                    new BlockO(),
                    new BlockT()
                };
        }

        public event PropertyChangedEventHandler PropertyChanged;
        public event EventHandler GameOver;

        private void OnGameOver(EventArgs e)
        {
            _nextBlock = null;
            this.GameStatus = GameStatus.Over;
            _dispatcher.Stop();
            if (GameOver != null)
                GameOver(this, e);
        }

        private void OnPropertyChanged(string property)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property));
            }
        }
    }
}

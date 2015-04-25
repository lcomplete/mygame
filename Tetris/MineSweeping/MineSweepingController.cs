using System;
using System.Collections.Generic;
using System.Windows.Threading;
using MineSweeping.Model;

namespace MineSweeping
{
    public class MineSweepingController
    {
        public GameSetting Setting { get; set; }
        public GameStatus Status { get; private set; }

        private Cell[,] _cellMatrix;
        public Cell[,] CellMatrix
        {
            get { return _cellMatrix; }
        }
        private DispatcherTimer _dispatcherForComputingTime;

        public MineSweepingController(GameSetting setting)
        {
            Setting = setting;
            Status = GameStatus.Ready;
            _dispatcherForComputingTime=new DispatcherTimer();
            _dispatcherForComputingTime.Interval = TimeSpan.FromSeconds(1);
            _dispatcherForComputingTime.Tick+=new EventHandler(_dispatcherForComputingTime_Tick);
        }

        private void _dispatcherForComputingTime_Tick(object sender, EventArgs e)
        {
            Setting.UseSecond += 1;
        }

        public void Play()
        {
            _cellMatrix = GetRandomCellMatrix();
            Status = GameStatus.Play;
            _dispatcherForComputingTime.Start();
            OnGameStart();
        }

        public void ScanCellAround(Cell cell)
        {
            bool hasWrongMark=false;
            if(cell.AroundBombsCount==0 ||GetAroundMarkCount(cell,out hasWrongMark)==cell.AroundBombsCount)
            {
                if(!hasWrongMark)
                for (int i = -1; i <= 1; i++)
                {
                    for (int j = -1; j <= 1; j++)
                    {
                        int x = cell.PointX + i, y = cell.PointY + j;
                        if ((i == 0 && j == 0) || x < 0 || x >= Setting.Width || y < 0 || y >= Setting.Height)
                            continue;
                        OpenCell(_cellMatrix[x,y]);
                    }
                }
            }

            if(hasWrongMark)
            {
                OnGameOver();
            }
            else
            {
                int unopenedCellCount = GetUnopenedCellCount();

            }
        }

        public void OpenCell(Cell cell)
        {
            if(cell.Opened)
                return;

            cell.Opened = true;
            if(cell.HasBomb)
            {
                cell.State = CellState.WrongChoice;
                OnGameOver();
            }
            else
            {
                cell.AroundBombsCount = GetAroundBombsCount(cell);
                if(cell.AroundBombsCount==0)
                    ScanCellAround(cell);
            }
        }

        public void MarkCell(Cell cell)
        {
            if(Setting.CanMarkCount==0)
                return;
            cell.State = cell.State == CellState.Mark ? CellState.None : CellState.Mark;
            Setting.CanMarkCount--;
        }

        private int GetAroundMarkCount(Cell cell,out bool hasWrongMark)
        {
            hasWrongMark = false;
            int markCount = 0;
            for (int i = -1; i <= 1; i++)
            {
                for (int j = -1; j <= 1; j++)
                {
                    int x = cell.PointX + i, y = cell.PointY + j;
                    if ((i == 0 && j == 0) || x < 0 || x >= Setting.Width || y < 0 || y >= Setting.Height)
                        continue;
                    Cell aroundCell = _cellMatrix[x, y];
                    if (aroundCell.State == CellState.Mark)
                    {
                        markCount++;
                        if(aroundCell.HasBomb)
                        {
                            hasWrongMark = true;
                            aroundCell.State = CellState.WrongMark;
                        }
                    }
                }
            }
            
            return markCount;
        }

        private int GetUnopenedCellCount()
        {
            int unopenedCount = 0;
            for (int i = 0; i < Setting.Width; i++)
            {
                for (int j = 0; j < Setting.Height; j++)
                {
                    if (!_cellMatrix[i, j].Opened)
                        unopenedCount++;
                }
            }
            return unopenedCount;
        }

        private int GetAroundBombsCount(Cell cell)
        {
            int bombsCount = 0;
            for (int i = -1; i <=1; i++)
            {
                for (int j = -1; j <=1; j++)
                {
                    int x = cell.PointX + i,y=cell.PointY+j;
                    if ( (i == 0 && j == 0) ||x<0||x>=Setting.Width||y<0||y>=Setting.Height )
                        continue;
                    if (_cellMatrix[x, y].HasBomb)
                        bombsCount++;
                }
            }
            return bombsCount;
        }

        private Cell[,] GetRandomCellMatrix()
        {
            Cell[,] matrix=new Cell[Setting.Width,Setting.Height];
            IList<bool> boombsSequence = GetBombsSequence();
            Random random=new Random();
            for (int i = 0; i < Setting.Width; i++)
            {
                for (int j = 0; j < Setting.Height; j++)
                {
                    int randomIndex = random.Next(0, boombsSequence.Count);
                    Cell cell = new Cell(boombsSequence[randomIndex],i,j);
                    cell.Top = i*cell.CurrentHeight;
                    cell.Left = j*cell.CurrentWidth;
                    matrix[i, j] = cell;
                    boombsSequence.RemoveAt(randomIndex);
                }
            }
            return matrix;
        }

        private IList<bool> GetBombsSequence()
        {
            int cellsCount = Setting.Width*Setting.Height;
            IList<bool> boombsSequence=new List<bool>(cellsCount);
            for (int i = 0; i < cellsCount; i++)
            {
                if(i<Setting.CanMarkCount)
                    boombsSequence.Add(true);
                else
                    boombsSequence.Add(false);
            }
            return boombsSequence;
        }

        public event EventHandler GameStart;
        public event EventHandler GameOver;
        public event EventHandler GameWin;

        private void OnGameStart()
        {
            if (GameStart != null)
                GameStart(this, EventArgs.Empty);
        }

        private void OnGameOver()
        {
            Status = GameStatus.Over;
            _dispatcherForComputingTime.Stop();
            for (int i = 0; i < Setting.Width; i++)
            {
                for (int j = 0; j < Setting.Height; j++)
                {
                    Cell cell = _cellMatrix[i, j];
                    if (!cell.Opened && cell.HasBomb)
                    {
                        if (cell.State == CellState.Mark)
                            cell.State = CellState.WrongMark;
                        else
                            cell.State = CellState.ShowBomb;
                    }
                }
            }

            if (GameOver != null)
                GameOver(this, EventArgs.Empty);
        }

        private void OnGameWin()
        {
            Status = GameStatus.Win;
            _dispatcherForComputingTime.Stop();
            for (int i = 0; i < Setting.Width; i++)
            {
                for (int j = 0; j < Setting.Height; j++)
                {
                    Cell cell = _cellMatrix[i, j];
                    if (!cell.Opened && !cell.HasBomb && cell.State != CellState.Mark)
                    {
                        cell.State = CellState.Mark;
                    }
                }
            }

            if (GameWin != null)
                GameWin(this, EventArgs.Empty);
        }
    }
}
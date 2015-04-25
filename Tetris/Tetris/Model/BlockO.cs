using System;
using System.Collections.Generic;

namespace Tetris.Model
{
    public class BlockO:BlockBase
    {
        protected override IList<int[,]> GetDefaultCellMatrixList()
        {
            return new List<int[,]>()
                       {
                           new int[,]
                               {
                                   {0, 0, 0, 0},
                                   {0, 1, 1, 0},
                                   {0, 1, 1, 0},
                                   {0, 0, 0, 0}
                               }
                       };
        }

        protected override CellColor GetDefaultColor()
        {
            return CellColor.Purple;
        }
    }
}
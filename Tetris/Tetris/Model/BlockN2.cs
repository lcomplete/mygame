using System;
using System.Collections.Generic;

namespace Tetris.Model
{
    public class BlockN2:BlockBase
    {
        protected override IList<int[,]> GetDefaultCellMatrixList()
        {
            return new List<int[,]>()
                       {
                           new int[,]
                               {
                                   {0, 1, 0, 0},
                                   {0, 1, 1, 0},
                                   {0, 0, 1, 0},
                                   {0, 0, 0, 0}
                               }
                           ,
                           new int[,]
                               {
                                   {0, 0, 1, 1},
                                   {0, 1, 1, 0},
                                   {0, 0, 0, 0},
                                   {0, 0, 0, 0}
                               }
                       };
        }

        protected override CellColor GetDefaultColor()
        {
            return CellColor.Blue;
        }
    }
}
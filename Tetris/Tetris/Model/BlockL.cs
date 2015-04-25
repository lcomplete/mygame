using System;
using System.Collections.Generic;
using System.Windows.Media;

namespace Tetris.Model
{
    public class BlockL : BlockBase
    {
        protected override IList<int[,]> GetDefaultCellMatrixList()
        {
            return new List<int[,]>()
                       {
                           new int[,]
                               {
                                   {0, 1, 0, 0},
                                   {0, 1, 0, 0},
                                   {0, 1, 1, 0},
                                   {0, 0, 0, 0}
                               }
                           ,
                           new int[,]
                               {
                                   {0, 0, 0, 0},
                                   {1, 1, 1, 0},
                                   {1, 0, 0, 0},
                                   {0, 0, 0, 0}
                               },
                           new int[,]
                               {
                                   {1, 1, 0, 0},
                                   {0, 1, 0, 0},
                                   {0, 1, 0, 0},
                                   {0, 0, 0, 0}
                               },
                           new int[,]
                               {
                                   {0, 0, 1, 0},
                                   {1, 1, 1, 0},
                                   {0, 0, 0, 0},
                                   {0, 0, 0, 0}
                               }
                       };
        }

        protected override CellColor GetDefaultColor()
        {
            return CellColor.Yellow;
        }
    }
}
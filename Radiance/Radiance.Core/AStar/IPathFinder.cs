using System.Collections.Generic;
using System.Windows;

namespace Radiance.Core.AStar
{
    [Author("QX")]
    public interface IPathFinder
    {
        List<PathFinderNode> FindPath(Point start, Point end);
        void FindPathStop();

        bool Diagonals { get; set; }

        HeuristicFormula Formula { get; set; }

        bool HeavyDiagonals { get; set; }

        int HeuristicEstimate { get; set; }

        int SearchLimit { get; set; }

        bool Stopped { get; }

        bool TieBreaker { get; set; }
    }
}


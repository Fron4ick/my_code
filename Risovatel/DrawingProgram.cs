using System;
using Avalonia.Media;
using RefactorMe.Common;

namespace RefactorMe
{
    static class CanvasPainter
    {
        private static float _x,_y;
        private static IGraphics _g;

        public static void Initialize(IGraphics graphics)
        {
            _g = graphics ?? throw new ArgumentNullException(nameof(graphics));
            _g.Clear(Colors.Black);
        }

        public static void SetPosition(float x,float y){ _x = x; _y = y; }

        public static void DrawStep(Pen pen,double len,double ang)
        {
            var nx = (float)(_x + len * Math.Cos(ang));
            var ny = (float)(_y + len * Math.Sin(ang));
            _g.DrawLine(pen, _x, _y, nx, ny);
            _x = nx; _y = ny;
        }

        public static void MoveOnly(double len,double ang)
        {
            _x = (float)(_x + len * Math.Cos(ang));
            _y = (float)(_y + len * Math.Sin(ang));
        }
    }

    public class ImpossibleSquare
    {
        private const double SideScale = 0.375, StripScale = 0.04;
        private static readonly double Sqrt2 = Math.Sqrt(2);
        private const double A45 = Math.PI / 4, A90 = Math.PI / 2;

        public static void Draw(int width,int height,double rotation,IGraphics graphics)
        {
            CanvasPainter.Initialize(graphics);

            var size = Math.Min(width, height);
            var diag = Sqrt2 * (size * SideScale + size * StripScale) / 2;

            var sx = (float)(diag * Math.Cos(A45 + Math.PI)) + width / 2f;
            var sy = (float)(diag * Math.Sin(A45 + Math.PI)) + height / 2f;
            CanvasPainter.SetPosition(sx, sy);

            var angles = new[] { 0.0, -A90, Math.PI, A90 };
            var pen = new Pen(Brushes.Yellow);

            foreach (var a in angles)
                DrawSide(size, a, pen);
        }

        private static void DrawSide(double size,double angle,Pen pen)
        {
            CanvasPainter.DrawStep(pen, size * SideScale, angle);
            CanvasPainter.DrawStep(pen, size * StripScale * Sqrt2, angle + A45);
            CanvasPainter.DrawStep(pen, size * SideScale, angle + Math.PI);
            CanvasPainter.DrawStep(pen, size * SideScale - size * StripScale, angle + A90);

            CanvasPainter.MoveOnly(size * StripScale, angle - Math.PI);
            CanvasPainter.MoveOnly(size * StripScale * Sqrt2, angle + 3 * A45);
        }
    }
}

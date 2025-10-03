using System;
using Avalonia.Media;
using RefactorMe.Common;

namespace RefactorMe
{
    static class CanvasPainter
    {
        private static float x;
        private static float y;
        private static IGraphics g;

        public static void Initialize(IGraphics graphics)
        {
            g = graphics ?? throw new ArgumentNullException(nameof(graphics));
            g.Clear(Colors.Black);
        }

        public static void SetPosition(float posX, float posY)
        {
            x = posX;
            y = posY;
        }

        public static void DrawStep(Pen pen, double length, double ang)
        {
            var nx = (float)(x + length * Math.Cos(ang));
            var ny = (float)(y + length * Math.Sin(ang));
            g.DrawLine(pen, x, y, nx, ny);
            x = nx;
            y = ny;
        }

        public static void MoveOnly(double length, double ang)
        {
            x = (float)(x + length * Math.Cos(ang));
            y = (float)(y + length * Math.Sin(ang));
        }
    }

    public class ImpossibleSquare
    {
        private const double SideScale = 0.375;
        private const double StripScale = 0.04;
        private static readonly double Sqrt2 = Math.Sqrt(2);
        private const double A45 = Math.PI / 4;
        private const double A90 = Math.PI / 2;
        private static readonly Pen SharedPen = new Pen(Brushes.Yellow);

        public static void Draw(int width, int height, double rotation, IGraphics graphics)
        {
            CanvasPainter.Initialize(graphics);

            var size = Math.Min(width, height);
            var diagonal = Sqrt2 * (size * SideScale + size * StripScale) / 2;

            var sx = (float)(diagonal * Math.Cos(A45 + Math.PI)) + width / 2f;
            var sy = (float)(diagonal * Math.Sin(A45 + Math.PI)) + height / 2f;
            CanvasPainter.SetPosition(sx, sy);

            var angles = new[] { 0.0, -A90, Math.PI, A90 };

            foreach (var a in angles)
                DrawSide(size, a, SharedPen);
        }

        private static void DrawSide(double size, double angle, Pen pen)
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

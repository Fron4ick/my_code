using System;
using Avalonia.Media;
using RefactorMe.Common;

namespace RefactorMe
{
    static class Painter
    {
        static double x, y;
        static IGraphics gfx;

        public static void Initialize(IGraphics graphics)
        {
            gfx = graphics;
            gfx.Clear(Colors.Black);
        }

        public static void SetPosition(double x0, double y0) => (x, y) = (x0, y0);

        // рисует от (x,y) в направлении angle шаг length и обновляет позицию
        public static void Step(Pen pen, double length, double angle)
        {
            var x1 = x + length * Math.Cos(angle);
            var y1 = y + length * Math.Sin(angle);
            gfx.DrawLine(pen, (float)x, (float)y, (float)x1, (float)y1);
            (x, y) = (x1, y1);
        }

        // сдвинуть без рисования
        public static void Move(double length, double angle)
        {
            x += length * Math.Cos(angle);
            y += length * Math.Sin(angle);
        }
    }

    public static class ImpossibleSquare
    {
        public static void Draw(int width, int height, double angleOfRotation, IGraphics grafika)
        {
            Painter.Initialize(graphics);

            var sz = Math.Min(width, height);
            var pen = new Pen(Brushes.Yellow);
            const double sqrt2 = Math.Sqrt(2);
            const double quarter = Math.PI / 4;

            // базовые размеры
            var side = sz * 0.375;
            var gap = sz * 0.04;
            var diag = Math.Sqrt(2) * (side + gap) / 2;

            // стартовая позиция (с учётом центра)
            var x0 = diag * Math.Cos(Math.PI / 4 + Math.PI) + width / 2.0;
            var y0 = diag * Math.Sin(Math.PI / 4 + Math.PI) + height / 2.0;
            Painter.SetPosition(x0, y0);

            // углы начала для четырёх сторон: 0, -pi/2, pi, pi/2
            double[] starts = { 0, -Math.PI / 2, Math.PI, Math.PI / 2 };

            foreach (var s in starts)
            {
                Painter.Step(pen, side, s);
                Painter.Step(pen, gap * sqrt2, s + quarter);
                Painter.Step(pen, side, s + Math.PI);
                Painter.Step(pen, side - gap, s + Math.PI / 2);

                // переходы между сторонами (поведение взято из оригинала)
                Painter.Move(gap, s - Math.PI);
                Painter.Move(gap * sqrt2, s + 3 * quarter);
            }
        }
    }
}

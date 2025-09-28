using System;
using Avalonia.Media;
using RefactorMe.Common;

namespace RefactorMe
{
    class Painter
    {
        static float x, y;
        static IGraphics graphics;

        public static void Initialize(IGraphics newGraphics)
        {
            graphics = newGraphics;
            //grafika.SmoothingMode = SmoothingMode.None;
            graphics.Clear(Colors.Black);
        }

        public static void Set_position(float x0, float y0)
        { x = x0; y = y0; }

        public static void MakeIt(Pen pen, double dlina, double angle)
        {
            //Делает шаг длиной dlina в направлении ugol и рисует пройденную траекторию
            var x1 = (float)(x + dlina * Math.Cos(angle));
            var y1 = (float)(y + dlina * Math.Sin(angle));
            graphics.DrawLine(pen, Painter.x, Painter.y, x1, y1);
            Painter.x = x1;
            Painter.y = y1;
        }

        public static void Change(double len, double angle)
        {
            x = (float)(x + len * Math.Cos(angle));
            y = (float)(y + len * Math.Sin(angle));
        }
    }

    public class ImpossibleSquare
    {
        public static void Draw(int width, int height, double angleOfRotation, IGraphics graphics)
        {
            Painter.Initialize(graphics);

            var sz = Math.Min(width, height);
            var diag = Math.Sqrt(2) * (sz * 0.375 + sz * 0.04) / 2;
            var x0 = (float)(diag * Math.Cos(Math.PI / 4 + Math.PI)) + width / 2f;
            var y0 = (float)(diag * Math.Sin(Math.PI / 4 + Math.PI)) + height / 2f;
            Painter.Set_position(x0, y0);

            double[] startAngles = { 0, -Math.PI / 2, Math.PI, Math.PI / 2 };

            foreach (var baseAngle in startAngles)
            {
                DrawSide(sz, baseAngle);
            }
        }

        private static void DrawSide(double sz, double angle)
        {
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375, angle);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.04 * Math.Sqrt(2), angle + Math.PI / 4);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375, angle + Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375 - sz * 0.04, angle + Math.PI / 2);

            Painter.Change(sz * 0.04, angle - Math.PI);
            Painter.Change(sz * 0.04 * Math.Sqrt(2), angle + 3 * Math.PI / 4);
        }
    }
}

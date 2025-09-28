    using System;
    using Avalonia.Media;
    using RefactorMe.Common;

    namespace RefactorMe
    {
        class Painter
        {
            static float x, y;
            static IGraphics graphics;

            public static void Initialize ( IGraphics newGraphics )
            {
                graphics = newGraphics;
                //grafika.SmoothingMode = SmoothingMode.None;
                graphics.Clear(Colors.Black);
            }

            public static void Set_position(float x0, float y0)
            {x = x0; y = y0;}

            public static void MakeIt(Pen pen, double dlina, double angle)
            {
            //Делает шаг длиной dlina в направлении ugol и рисует пройденную траекторию
            var x1 = (float) (x + dlina * Math.Cos(angle));
            var y1 = (float) (y + dlina * Math.Sin(angle));
            graphics.DrawLine(pen, x, y, x1, y1);
            x = x1;
            y = y1;
            }

            public static void Change(double lenght, double ugol)
            {
                x = (float)(x + lenght * Math.Cos(ugol)); 
            y = (float)(y + lenght * Math.Sin(ugol));
            }
        }
        
        public class ImpossibleSquare
    {
        public static void Draw(int width, int hight, double angleOfRotation, IGraphics graphics)
        {
            // ugolPovorota пока не используется, но будет использоваться в будущем
            Painter.Initialize(graphics);

            var sz = Math.Min(width, hight);

            var diagonal_length = Math.Sqrt(2) * (sz * 0.375f + sz * 0.04f) / 2;
            var x0 = (float)(diagonal_length * Math.Cos(Math.PI / 4 + Math.PI)) + width / 2f;
            var y0 = (float)(diagonal_length * Math.Sin(Math.PI / 4 + Math.PI)) + hight / 2f;

            Painter.Set_position(x0, y0);
            
            //Рисуем 1-ую сторону
                Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, 0);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.04f * Math.Sqrt(2), Math.PI / 4);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f - sz * 0.04f, Math.PI / 2);

            Painter.Change(sz * 0.04f, -Math.PI);
            Painter.Change(sz * 0.04f * Math.Sqrt(2), 3 * Math.PI / 4);

            //Рисуем 2-ую сторону
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, -Math.PI / 2);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.04f * Math.Sqrt(2), -Math.PI / 2 + Math.PI / 4);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, -Math.PI / 2 + Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f - sz * 0.04f, -Math.PI / 2 + Math.PI / 2);

            Painter.Change(sz * 0.04f, -Math.PI / 2 - Math.PI);
            Painter.Change(sz * 0.04f * Math.Sqrt(2), -Math.PI / 2 + 3 * Math.PI / 4);

            //Рисуем 3-ю сторону
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.04f * Math.Sqrt(2), Math.PI + Math.PI / 4);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, Math.PI + Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f - sz * 0.04f, Math.PI + Math.PI / 2);

            Painter.Change(sz * 0.04f, Math.PI - Math.PI);
            Painter.Change(sz * 0.04f * Math.Sqrt(2), Math.PI + 3 * Math.PI / 4);

            //Рисуем 4-ую сторону
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, Math.PI / 2);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.04f * Math.Sqrt(2), Math.PI / 2 + Math.PI / 4);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f, Math.PI / 2 + Math.PI);
            Painter.MakeIt(new Pen(Brushes.Yellow), sz * 0.375f - sz * 0.04f, Math.PI / 2 + Math.PI / 2);

            Painter.Change(sz * 0.04f, Math.PI / 2 - Math.PI);
            Painter.Change(sz * 0.04f * Math.Sqrt(2), Math.PI / 2 + 3 * Math.PI / 4);
        }
    }
    }

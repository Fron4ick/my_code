using System;
using System.Drawing;

namespace Fractals;

internal static class DragonFractalTask
{
	public static void DrawDragonFractal(Pixels pixels, int iterationsCount, int seed)
	{
		var random = new Random(seed);
		double x = 1;
		double y = 0;

		pixels.SetPixel(x, y);
		GeneratePoints(pixels, random, iterationsCount, x, y);
	}

	public static void GeneratePoints(Pixels pixels, Random random, int iterationsCount, double startX, double startY)
	{
		double x = startX;
		double y = startY;

		for (int i = 0; i < iterationsCount; i++)
		{
			var transformType = random.Next(2);
			var newPoint = Transform(x, y, transformType);
			
			x = newPoint.Item1;
			y = newPoint.Item2;
			pixels.SetPixel(x, y);
		}
	}

	public static Tuple<double, double> Transform(double x, double y, int transformType)
	{
        if (transformType == 0)
        {
            double newX = (x - y) / 2.0;
            double newY = (x + y) / 2.0;
            return Tuple.Create(newX, newY);
        }
        else
        {
            double newX = (-x - y) / 2.0 + 1;
            double newY = (x - y) / 2.0;
            return Tuple.Create(newX, newY);
        }
	}
}

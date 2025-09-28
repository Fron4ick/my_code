using System;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

public static class Time
{
    static void Main()
    {
        string[] time = Console.ReadLine().Split();
        int h = int.Parse(time[0]);
        int t = int.Parse(time[1]);
        int v = int.Parse(time[2]);
        int x = int.Parse(time[3]);
        Console.WriteLine(BetweenHourAndMin(h, t, v, x));
    }
    public static object BetweenHourAndMin(int hight, int time, int v, int x)
    {
        //var timeFlyMax = ;
        double minTimeOfStuffyEars = time - (hight - time * v) * 1.0 / (x - v);
        double maxTimeOfStuffyEars = Math.Min(time, hight * 1.0 /Math.Min(v, hight / time));

        return (minTimeOfStuffyEars, maxTimeOfStuffyEars);
    }
    
}
